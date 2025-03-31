import time
import json
import socket
import paho.mqtt.client as mqtt
from src.pyaccsharedmemory import accSharedMemory, ACC_STATUS
from src.schemas import ACC_EVENTS
from src.utils import strip_nulls_from_dataclass, Config


class MqttPublisher:
    def __init__(self, host: str, port: int, event_topic: str, telemetry_topic: str):
        """
        Manages MQTT connections
        """
        self.host = host
        self.port = port
        self.event_topic = event_topic
        self.telemetry_topic = telemetry_topic

        self._connected = False

        # Note: I use websocket MQTT connections, in line with previous activations
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, transport="websockets"
        )
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """
        Callback for when the client receives a CONNACK response
        """
        if rc == 0:
            self._connected = True
            print("[MQTT] Connected successfully.")
        else:
            self._connected = False
            print(f"[MQTT] Connection failed with code {rc}.")

    def _on_disconnect(self, client, userdata, flags, rc, properties=None):
        """
        Callback or when the client disconnects from the broker.
        """
        self._connected = False
        print("[MQTT] Disconnected. Will retry...")

    @property
    def is_connected(self):
        return self._connected

    def try_connect(self):
        """
        Attempts to connect to the MQTT broker
        """
        if not self._connected:
            try:
                self.client.connect(self.host, self.port, 60)
                self.client.loop_start()
                print("[MQTT] Attempting connection...")
            except Exception as e:
                print(f"[MQTT] MQTT connection failed: {e}")
                time.sleep(10)

    def publish_event(self, data: dict):
        """
        Publishes an event message to the MQTT broker.
        """
        if not self._connected:
            return
        try:
            payload = json.dumps(data)
            self.client.publish(self.event_topic, payload)
        except Exception as e:
            print(f"[MQTT] Event publish failed: {e}")
            self._force_reconnect()

    def publish_telemetry(self, data: dict):
        """
        Publishes a telemetry message to the MQTT broker.
        """
        if not self._connected:
            return
        try:
            payload = json.dumps(data)
            self.client.publish(self.telemetry_topic, payload)
        except Exception as e:
            print(f"[MQTT] Telemetry publish failed: {e}")
            self._force_reconnect()

    def _force_reconnect(self):
        """
        Force a reconnect
        """
        self.client.loop_stop()
        self.client.disconnect()
        self._connected = False

    def close(self):
        """
        Cleanly stop and disconnect
        """
        self.client.loop_stop()
        self.client.disconnect()


class AccUdpMqttForwarder:
    def __init__(self):
        cfg = Config()
        self.mqtt_enabled = cfg.get("mqtt.enabled")
        self.udp_enabled = cfg.get("udp.enabled")

        # UDP setup
        self.udp_host = cfg.get("udp.host", "127.0.0.1")
        self.udp_port = cfg.get("udp.port", 9002)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Shared memory
        self.asm = accSharedMemory()
        self.status = ACC_STATUS.ACC_OFF
        self.event = ACC_EVENTS.ACC_IDLE

        # MQTT setup
        mqtt_host = cfg.get("mqtt.host", "127.0.0.1")
        mqtt_port = cfg.get("mqtt.port", 9001)
        event_topic = cfg.get("mqtt.event_topic", "acc/events")
        telemetry_topic = cfg.get("mqtt.telemetry_topic", "acc/telemetry")

        self.mqtt_pub = MqttPublisher(
            host=mqtt_host,
            port=mqtt_port,
            event_topic=event_topic,
            telemetry_topic=telemetry_topic,
        )

    def run(self):
        """
        Main loop that handles:
          - Reading shared memory
          - Sending UDP messages (event + telemetry)
          - Attempting MQTT connections + publishing
        """
        try:
            while True:
                # Attempt connection
                if self.mqtt_enabled:
                    self.mqtt_pub.try_connect()

                prev_status = self.status
                sm = self.asm.read_shared_memory()

                # When no game is played, switch to idle mode
                if sm is None:
                    self.event = ACC_EVENTS.ACC_IDLE
                else:
                    # Keep track of status changes
                    self.status = sm.Graphics.status
                    if self.status != prev_status:
                        self.event = ACC_EVENTS.ACC_IDLE
                        if self.status == ACC_STATUS.ACC_OFF:
                            self.event = ACC_EVENTS.ACC_STOP_RACE
                        elif self.status == ACC_STATUS.ACC_LIVE:
                            if prev_status == ACC_STATUS.ACC_OFF:
                                self.event = ACC_EVENTS.ACC_START_RACE
                            elif prev_status == ACC_STATUS.ACC_PAUSE:
                                self.event = ACC_EVENTS.ACC_RESUME_RACE
                        elif self.status == ACC_STATUS.ACC_PAUSE:
                            self.event = ACC_EVENTS.ACC_PAUSE_RACE
                        elif self.status == ACC_STATUS.ACC_REPLAY:
                            self.event = ACC_EVENTS.ACC_REPLAY_EVENT

                    # Shared memory has some empty bits allocated
                    strip_nulls_from_dataclass(sm.Static)
                    strip_nulls_from_dataclass(sm.Graphics)
                    strip_nulls_from_dataclass(sm.Physics)
                    physics_info = sm.Physics.to_dict()
                    graphics_info = sm.Graphics.to_dict()
                    static_info = sm.Static.to_dict()

                    # If status changed, send an event message (UDP and/or MQTT)
                    if self.status != prev_status and sm is not None:
                        print("New status: ", self.status)
                        static_info["air_temp"] = physics_info.get("air_temp")
                        static_info["road_temp"] = physics_info.get("road_temp")
                        static_info["water_temp"] = physics_info.get("water_temp")
                        static_info["tyre_compound"] = graphics_info.get(
                            "tyre_compound"
                        )

                        data = {
                            "message_type": "event_change",
                            "event": str(self.event),
                            "static_info": static_info,
                        }

                        if self.udp_enabled:
                            # Send via UDP
                            msg_bytes = json.dumps(data).encode("utf-8")
                            self.sock.sendto(msg_bytes, (self.udp_host, self.udp_port))
                        if self.mqtt_enabled:
                            # Send via MQTT
                            self.mqtt_pub.publish_event(data)

                    # If live, send telemetry (UDP and/or MQTT)
                    if sm.Graphics.status == ACC_STATUS.ACC_LIVE:
                        data = {
                            "message_type": "telemetry",
                            "graphics_info": graphics_info,
                            "physics_info": physics_info,
                        }
                        if self.udp_enabled:
                            # Send via UDP
                            msg_bytes = json.dumps(data).encode("utf-8")
                            self.sock.sendto(msg_bytes, (self.udp_host, self.udp_port))
                        if self.mqtt_enabled:
                            # Send via MQTT
                            self.mqtt_pub.publish_telemetry(data)

                # Sleep to avoid busy-wait
                time.sleep(0.01)

        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

    def cleanup(self):
        """
        Cleanly shuts down resources on exit.
        """
        self.asm.close()
        self.sock.close()
        self.mqtt_pub.close()
        print("Exiting cleanly...")


if __name__ == "__main__":
    forwarder = AccUdpMqttForwarder()
    forwarder.run()
