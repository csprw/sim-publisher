import logging
import json
import time
import paho.mqtt.client as mqtt


class MqttPublisher:
    def __init__(self, host: str, port: int, event_topic: str, telemetry_topic: str):
        """
        Manages MQTT connections
        """
        logging.info("Initalizing MQTT")
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
            logging.info("[MQTT] Connected successfully.")
        else:
            self._connected = False
            logging.info(f"[MQTT] Connection failed with code {rc}.")

    def _on_disconnect(self, client, userdata, flags, rc, properties=None):
        """
        Callback or when the client disconnects from the broker.
        """
        self._connected = False
        logging.info("[MQTT] Disconnected. Will retry...")

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
                logging.info("[MQTT] Attempting connection...")
            except Exception as e:
                logging.info(f"[MQTT] MQTT connection failed: {e}")
                time.sleep(10)

    def publish_event(self, data: dict):
        """
        Publishes an event message to the MQTT broker.
        """
        if not self._connected:
            return
        try:
            payload = json.dumps(data)
            print("Publishing: ", self.event_topic)
            self.client.publish(self.event_topic, payload)
        except Exception as e:
            logging.info(f"[MQTT] Event publish failed: {e}")
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
            logging.info(f"[MQTT] Telemetry publish failed: {e}")
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
