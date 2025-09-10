#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# main.py

"""
Bootstrap script for the MarkerBox application.

It creates the two shared objects (MarkerMonitor and MarkerOut) once
and hands them to the Kivy GUI (MarkerWidget) via the MarkerBoxApp.
"""

import sys
from kivy.app import App as KivyApp
from MarkerMonitor import MarkerMonitor      # ← your monitor class
from MarkerOut import MarkerOut              # ← your output class
from kivyGUI import MarkerWidget             # ← UI & App


# get input args from when running the app (e.g. python markerbox 1), but default to 0 if none are given
args = int(sys.argv[1]) if len(sys.argv) > 1 else 0

marker_monitor = MarkerMonitor(args)
marker_out = MarkerOut()


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

# ----------------------------------------------------------------------
# Run the program.
# ----------------------------------------------------------------------
if __name__ == "__main__":
    try:
        marker_monitor.start_thread()
        marker_monitor.startTracking()
        MarkerBoxApp().run()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received, shutting down...")
    finally:
        marker_monitor.stopTracking()
        marker_monitor.kill()
        marker_out.cleanup()
        sys.exit(0)