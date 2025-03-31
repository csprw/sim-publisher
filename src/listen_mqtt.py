"""
This is a small example script on how to listen to mqtt data.
"""

import paho.mqtt.client as mqtt
from src.utils import Config

cfg = Config()


def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected with result code {rc}")
    event_topic = cfg.get("mqtt.event_topic", "acc/events")
    telemetry_topic = cfg.get("mqtt.telemetry_topic", "acc/telemetry")
    client.subscribe(event_topic)
    client.subscribe(telemetry_topic)


def on_message(client, userdata, msg):
    print(f"{msg.topic} {msg.payload.decode()}\n")


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
mqttc.on_connect = on_connect
mqttc.on_message = on_message

host = cfg.get("mqtt.host", "127.0.0.1")
port = cfg.get("mqtt.port", 9001)
mqttc.connect(host, port, 60)
print(f"Listening for MQTT messages on {host}:{port}")
mqttc.loop_forever()
