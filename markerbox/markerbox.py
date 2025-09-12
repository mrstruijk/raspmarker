#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# markerbox.py

import sys

from MarkerMonitor import MarkerMonitor
from MarkerOut import MarkerOut
from MQTT_handler import MQTTHandler

# Toggle GUI
USE_GUI = False
if USE_GUI:
    from kivy.app import App as KivyApp
    from kivyGUI import MarkerWidget

# get input args from when running the app (e.g. python markerbox 1 (=use random markers)),
# default to 0 (=use real markers) if none are given.
args = int(sys.argv[1]) if len(sys.argv) > 1 else 0

marker_monitor = MarkerMonitor(args)
marker_out = MarkerOut()
mqtt_handler = MQTTHandler()


def start_services():
    marker_monitor.start_thread()
    marker_monitor.startTracking()

    mqtt_handler = MQTTHandler(
        broker="192.168.1.40",
        port=1883,
        username="SOLO",
        password="SOLO1B11",
        default_topic="raspmarker")

    mqtt_handler.subscribe(marker_out.send_marker_to_lpt)
    marker_monitor.subscribe_to_markers(mqtt_handler.publish_to_default_topic)

    mqtt_handler.connect()
    mqtt_handler.start()


def stop_services():
    marker_monitor.stopTracking()
    marker_monitor.kill()
    marker_out.cleanup()


def run():
    try:
        start_services()

        if USE_GUI:
            class MarkerBoxApp(KivyApp):
                def build(self):
                    return MarkerWidget(marker_monitor=marker_monitor, marker_out=marker_out)

                def on_stop(self):
                    stop_services()

            MarkerBoxApp().run()
        else:
            # Run headless until killed
            print("Running headless (no GUI). Press Ctrl+C to exit.")
            while True:
                pass

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received, shutting down...")
    finally:
        stop_services()
        sys.exit(0)


if __name__ == "__main__":
    run()
