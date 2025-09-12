#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# mqtt_handler.py

import paho.mqtt.client as mqtt
import threading


class MQTTHandler:
    def __init__(self, broker="localhost", port=1883,
                 username=None, password=None, topic="SOSXR"):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.topic = topic

        self._callbacks = []  # list of subscribed callables

        self.client = mqtt.Client()
        if username and password:
            self.client.username_pw_set(username, password)

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT broker {self.broker}:{self.port}")
            client.subscribe(self.topic)
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
        thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        thread.start()

    def publish(self, topic, message):
        self.client.publish(topic, message)

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
