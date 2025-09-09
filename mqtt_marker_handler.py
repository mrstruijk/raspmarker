# mqtt_marker_handler.py

import sys
import threading
import paho.mqtt.client as mqtt

class MQTTMarkerHandler:
    def __init__(self, marker_widget, broker="192.168.1.40", port=1883,
                 username="SOLO", password="SOLO1B11", topic="raspmarker"):
        self.marker_widget = marker_widget
        self.topic = topic

        self.client = mqtt.Client(protocol=mqtt.MQTTv311,
                                  callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        try:
            self.client.connect(broker, port, 60)
        except ConnectionRefusedError:
            print(f"Could not connect to MQTT broker at {broker}:{port}")
            sys.exit(1)

        self.thread = threading.Thread(target=self._mqtt_loop, daemon=True)
        self.thread.start()

    def _mqtt_loop(self):
        try:
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received.")

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        if reason_code == 0:
            print(f"Connected to MQTT broker, subscribing to '{self.topic}'")
            client.subscribe(self.topic)
        else:
            print(f"Failed to connect, return code {reason_code}")

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode("utf-8").strip()
            marker_val = int(payload)
            if 0 <= marker_val <= 255:
                self.marker_widget.output_marker(marker_val)
                #print(f"Output marker: {marker_val}")
            else:
                print(f"Payload {marker_val} out of range 0-255")
        except ValueError:
            print(f"Invalid payload '{payload}', must be integer 0-255")