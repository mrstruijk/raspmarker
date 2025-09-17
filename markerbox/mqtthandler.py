#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mqtt_handler.py

import paho.mqtt.client as mqtt
import threading


class MQTTHandler:
    def __init__(self, broker="localhost", port=1883,
                 username=None, password=None, default_topic=None):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.default_topic = default_topic

        self._callbacks = []  # list of subscribed callables

        self.client = mqtt.Client()
        if username and password:
            self.client.username_pw_set(username, password)

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT broker {self.broker}:{self.port}, with username {self.username} and password {self.password}, and default_topic {self.default_topic}")
            client.subscribe(self.default_topic)
        else:
            print(f"Failed to connect, return code {rc}")

    def _on_message(self, client, userdata, msg):
        try:
            payload = int(msg.payload.decode().strip())
            for callback in self._callbacks:
                callback(payload)
        except Exception as e:
            print(f"Error handling message: {e}")

    def start(self):
        # thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        # thread.start()
        self.client.loop_start()

    def publish_to_default_topic(self, payload):
        print(f"Publishing to default topic: {self.default_topic}, payload: {payload}")
        self.publish(self.default_topic, payload)

    def publish(self, topic, payload):
        if topic is None or len(topic) == 0:
            print(f"Invalid topic: {topic}")
            #return
        print(f"Publishing to topic: {topic}, payload: {payload}")
        self.client.publish(topic, payload)

    def subscribe(self, callback):
        """Register a Python function to be called with the int payload."""
        if callable(callback):
            self._callbacks.append(callback)
        else:
            raise ValueError("subscribe() requires a callable")

    def connect(self):
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            print(f"Trying to connect to {self.broker}:{self.port} ...")
        except Exception as e:
            print(f"MQTT connection failed: {e}")

    def disconnect(self):
        try:
            self.client.disconnect()
            print(f"Disconnected from {self.broker}:{self.port} ...")
        except Exception as e:
            print(f"MQTT disconnection failed: {e}")
