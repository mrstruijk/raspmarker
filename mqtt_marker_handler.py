#!/usr/bin/env python3

# mqtt_marker_handler.py

# Usage: ./mqtt_marker_handler.py localhost 1883 SOLO SOLO1B11

import sys
import paho.mqtt.client as mqtt
from pin_marker_sender import PinMarkerSender


class MQTTMarkerHandler:
    def __init__(self, broker="192.168.1.40", port=1883, username="SOLO", password="SOLO1B11", topic="raspmarker"):
        self.sender = PinMarkerSender()
        self.topic = topic
        self.client = mqtt.Client(protocol=mqtt.MQTTv311, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:
            self.client.connect(broker, port, 60)
        except ConnectionRefusedError:
            print(f"\nCould not connect to MQTT broker at {broker}:{port}. Will quit.")
            sys.exit(1)

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            print(f"Connected to MQTT broker, subscribing to '{self.topic}'")
            client.subscribe(self.topic)
        else:
            print(f"Failed to connect, return code {reason_code}")

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode("utf-8").strip()
            print(f"Received message on {msg.topic}: {payload}")
            marker_val = int(payload)
            self.sender.send_marker(marker_val, 1.0)
        except ValueError:
            print(f"Invalid payload '{payload}', must be integer 0-255")

    def loop_forever(self):
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received.")
        finally:
            self.sender.cleanup()


def main():
    #if len(sys.argv) < 5:
    #    print(f"Usage: {sys.argv[0]} <broker> <port> <username> <password>")
    #    sys.exit(1)

    # broker, port, username, password = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    # handler = MQTTMarkerHandler(broker, port, username, password)
    handler = MQTTMarkerHandler()
    handler.loop_forever()


if __name__ == "__main__":
    main()