#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# markerbox.py

"""
Bootstrap script for the MarkerBox application.

It creates the two shared objects (MarkerMonitor and MarkerOut) once
and hands them to the Kivy GUI (MarkerWidget) via the MarkerBoxApp.
"""

import sys

from kivy.app import App as KivyApp
from kivyGUI import MarkerWidget

from MarkerMonitor import MarkerMonitor
from MarkerOut import MarkerOut

from MQTT_handler import MQTTHandler

# get input args from when running the app (e.g. python markerbox 1 (=use random markers)), but default to 0 (=use real markers) if none are given.
args = int(sys.argv[1]) if len(sys.argv) > 1 else 0

marker_monitor = MarkerMonitor(args)
marker_out = MarkerOut()

mqtt_handler = MQTTHandler()


def run():
    class MarkerBoxApp(KivyApp):
        """
            Sub‑class the original app, so we can override ``build`` and
            supply the pre‑created objects.
            """
        def build(self):
            return MarkerWidget(marker_monitor=marker_monitor, marker_out=marker_out)

        def on_stop(self):
            marker_monitor.stopTracking()
            marker_monitor.kill()

    try:
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
        mqtt_handler.start() # All pub/sub should be done before this, because it spawns the thread in a parallel universe.

        MarkerBoxApp().run()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received, shutting down...")
    finally:
        marker_monitor.stopTracking()
        marker_monitor.kill()
        marker_out.cleanup()
        sys.exit(0)


if __name__ == "__main__":
    run()