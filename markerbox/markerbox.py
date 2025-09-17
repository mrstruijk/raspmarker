#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# markerbox.py

import sys
import argparse
import threading

from markermonitor import MarkerMonitor
from markerout import MarkerOut

# Parse CLI arguments
parser = argparse.ArgumentParser(description="MarkerBox Application")

parser.add_argument("--gui", action="store_true", help="Enable Kivy GUI")
parser.add_argument("--no-gui", dest="gui", action="store_false", help="Run headless without GUI")
parser.set_defaults(gui=True)

parser.add_argument("--random", action="store_true", help="Generate random markers to mimic LPT connection")
parser.add_argument("--no-random", dest= "random", action="store_false", help="Get real markers from LPT")
parser.set_defaults(random=False)

parser.add_argument("--mqtt", action="store_true", help="Enable MQTT handler")
parser.add_argument("--no-mqtt", dest="mqtt", action="store_false", help="Disable MQTT handler")
parser.set_defaults(mqtt=True)

args = parser.parse_args()

# Conditional imports (only if GUI enabled)
if args.gui:
    from kivy.app import App as KivyApp
    from kivygui import MarkerWidget

# Create shared objects
marker_monitor = MarkerMonitor(args.random)
marker_out = MarkerOut()
stop_event = threading.Event()

# mqtt_handler = None

def start_services():
    marker_monitor.start_thread()
    marker_monitor.startTracking()

    if args.mqtt:
        from mqtthandler import MQTTHandler
        global mqtt_handler
        mqtt_handler = MQTTHandler(
            broker="145.118.221.36",
            port=1883,
            username="SOLO",
            password="SOLO1B11",
            default_topic="raspmarker")

        marker_out.subscribe(mqtt_handler.publish_to_default_topic)
        marker_out.subscribe(
            lambda value: mqtt_handler.publish(mqtt_handler.default_topic + "/from-GUI", value)
        )

        marker_monitor.subscribe(
            lambda value: mqtt_handler.publish(mqtt_handler.default_topic + "/from-LPT", value)
        )

        mqtt_handler.connect()
        mqtt_handler.start()


def stop_services():
    marker_monitor.stopTracking()
    marker_monitor.kill()
    marker_out.cleanup()
    if mqtt_handler:
        mqtt_handler.disconnect()
        print("This reference is not safe: it can lead to a None type if it's not initialized.")


def run():
    try:
        start_services()

        if args.gui:
            class MarkerBoxApp(KivyApp):
                def build(self):
                    return MarkerWidget(marker_monitor=marker_monitor, marker_out=marker_out)

                def on_stop(self):
                    stop_services()

            MarkerBoxApp().run()
        else:
            print("Running headless (no GUI). Press Ctrl+C to exit.")
            stop_event.wait()

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received, shutting down...")
    finally:
        stop_services()
        sys.exit(0)


if __name__ == "__main__":
    run()
