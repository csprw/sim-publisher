import time
import json
import copy
import socket
import logging
from src.mqtt import MqttPublisher
from src.pyacsharedmemory import (
    acSharedMemory,
    AC_STATUS,
    PhysicsMap,
    read_physic_map,
    read_graphics_map,
    read_static_map,
)
from src.schemas import AC_EVENTS
from src.utils import strip_nulls_from_dataclass, Config

logging.getLogger().setLevel(logging.INFO)


class AcUdpMqttForwarder:
    def __init__(self):
        cfg = Config()
        self.physics_interval = 0.01
        self.static_interval = 1.0
        self.mqtt_enabled = cfg.get("mqtt.enabled")
        self.udp_enabled = cfg.get("udp.enabled")
        self.save_output = cfg.get("output.save", True)

        # UDP setup
        self.udp_host = cfg.get("udp.host", "127.0.0.1")
        self.udp_port = cfg.get("udp.port", 9002)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Shared memory
        self.asm = acSharedMemory()
        self.status = AC_STATUS.AC_OFF
        self.event = AC_EVENTS.AC_IDLE

        # MQTT setup
        mqtt_host = cfg.get("mqtt.host", "127.0.0.1")
        mqtt_port = cfg.get("mqtt.port", 9001)
        event_topic = cfg.get("mqtt.event_topic", "ac/events")
        telemetry_topic = cfg.get("mqtt.telemetry_topic", "ac/telemetry")

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
            last_physics_read = 0.0
            last_static_read = 0.0

            while True:
                # Attempt connection
                if self.mqtt_enabled:
                    self.mqtt_pub.try_connect()

                prev_status = self.status
                now = time.time()

                if (now - last_physics_read) >= self.physics_interval:
                    physics = read_physic_map(self.asm.physicSM)
                    graphics = read_graphics_map(self.asm.graphicSM)

                if (now - last_static_read) >= self.static_interval:
                    statics = read_static_map(self.asm.staticSM)

                if physics.packed_id == self.asm.last_physicsID or (
                    self.asm.physics_old is not None
                    and PhysicsMap.is_equal(self.asm.physics_old, physics)
                ):
                    physics = None

                else:
                    self.asm.physics_old = copy.deepcopy(physics)

                # When no game is played, switch to idle mode
                if physics is None:
                    self.event = AC_EVENTS.AC_IDLE
                else:
                    # Keep track of status changes
                    self.status = graphics.status
                    if self.status != prev_status:
                        self.event = AC_EVENTS.AC_IDLE
                        if self.status == AC_STATUS.AC_OFF:
                            self.event = AC_EVENTS.AC_STOP_RACE
                        elif self.status == AC_STATUS.AC_LIVE:
                            if prev_status == AC_STATUS.AC_OFF:
                                self.event = AC_EVENTS.AC_START_RACE
                            elif prev_status == AC_STATUS.AC_PAUSE:
                                self.event = AC_EVENTS.AC_RESUME_RACE
                        elif self.status == AC_STATUS.AC_PAUSE:
                            self.event = AC_EVENTS.AC_PAUSE_RACE
                        elif self.status == AC_STATUS.AC_REPLAY:
                            self.event = AC_EVENTS.AC_REPLAY_EVENT
                        else:
                            logging.warning(f"unk status: {prev_status}-{self.status}")
                            self.event = AC_EVENTS.AC_UNKNOWN

                    # Shared memory has some empty bits allocated
                    strip_nulls_from_dataclass(statics)
                    strip_nulls_from_dataclass(graphics)
                    strip_nulls_from_dataclass(physics)
                    physics_info = physics.to_dict()
                    graphics_info = graphics.to_dict()
                    static_info = statics.to_dict()

                    # If status changed, send an event message (UDP and/or MQTT)
                    if self.status != prev_status and physics is not None:
                        logging.info(f"Status change {self.status}")
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
                    if graphics.status == AC_STATUS.AC_LIVE:
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

                        if self.save_output:
                            with open("telemetry.json", "w") as fp:
                                json.dump(data, fp, indent=4)

                # Sleep to avoid busy-wait
                time.sleep(0.001)

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
        logging.info("Exiting cleanly...")


if __name__ == "__main__":
    forwarder = AcUdpMqttForwarder()
    forwarder.run()
