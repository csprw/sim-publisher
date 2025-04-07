import json
import csv
import time
import threading
import logging
import os
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
from src.utils import Config

cfg = Config()


plot_telemetry = cfg.get("client.plot_telemetry", False)
save_csv = cfg.get("client.save_csv", False)

car_positions = []
stop_event = threading.Event()
print(f"Plot: {plot_telemetry}")
print(f"Save: {save_csv}")

csv_file = "telemetry_data.csv"
csv_header_written = False
csv_lock = threading.Lock()


# Ensure CSV file exists and header is written
def initialize_csv():
    global csv_header_written
    if not os.path.exists(csv_file):
        with open(csv_file, mode="w", newline="") as file:
            pass


def write_to_csv(data):
    global csv_header_written
    with csv_lock:
        with open(csv_file, mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["timestamp"] + list(data.keys()))
            if not csv_header_written:
                writer.writeheader()
                csv_header_written = True
            writer.writerow({"timestamp": time.time(), **data})


def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected with result code {rc}")
    event_topic = cfg.get("mqtt.event_topic", "ac/events")
    telemetry_topic = cfg.get("mqtt.telemetry_topic", "ac/telemetry")
    print("Subscribing to: ", event_topic, telemetry_topic)

    if cfg.get("client.subscribe_events", False):
        client.subscribe(event_topic)

    if cfg.get("client.subscribe_telemetry", False):
        client.subscribe(telemetry_topic)


def on_message(client, userdata, msg):
    payload_str = msg.payload.decode()
    print("new message on topic: ", msg.topic)

    if "event" in msg.topic:
        print(f"{msg.topic} {payload_str}\n")

    # If we are plotting, parse telemetry from 'acc/telemetry'
    if "telemetry" in msg.topic:
        try:
            data = json.loads(payload_str)
        except json.JSONDecodeError:
            logging.error("Error decoding telemetry JSON.")
            return

        graphics_info = data.get("graphics_info", {})

        if save_csv:
            write_to_csv(graphics_info)

        if plot_telemetry:
            graphics_info = data.get("graphics_info", {})
            car_coordinates = graphics_info.get("car_coordinates", {})
            x = -car_coordinates.get("z")
            z = -car_coordinates.get("x")

            if x is not None and z is not None:
                car_positions.append((x, z))


def live_plotter():
    """
    Continuously plots car_positions in a non-blocking fashion,
    until stop_event is set.
    """
    plt.ion()
    fig, ax = plt.subplots()
    (line,) = ax.plot([], [], marker="o", linestyle="-")

    while not stop_event.is_set():
        if car_positions:
            xs, ys = zip(*car_positions)
            line.set_xdata(xs)
            line.set_ydata(ys)

            ax.relim()
            ax.autoscale_view()
            plt.draw()
            plt.pause(0.01)
        else:
            time.sleep(0.01)

    # Clean close
    plt.close(fig)


# Set up MQTT client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, transport="websockets")
mqttc.on_connect = on_connect
mqttc.on_message = on_message

host = cfg.get("mqtt.host", "127.0.0.1")
port = cfg.get("mqtt.port", 9001)
mqttc.connect(host, port, 60)
print(f"Listening for MQTT messages on {host}:{port}")

try:
    if plot_telemetry:
        mqttc.loop_start()
        plot_thread = threading.Thread(target=live_plotter, daemon=False)
        plot_thread.start()
        while True:
            time.sleep(1)
    else:
        mqttc.loop_forever()
except KeyboardInterrupt:
    print("Shutting down...")
    stop_event.set()

    if plot_telemetry:
        plot_thread.join()
    mqttc.loop_stop()
    mqttc.disconnect()
    print("Exited cleanly.")
