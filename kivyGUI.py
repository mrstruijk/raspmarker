# -*- coding: utf-8 -*-
"""
Created on Fri Nov 16 22:43:49 2018

@author: 
"""
# Config.set ('graphics', 'resizable', 0)

# Config.set('graphics', 'position', 'custom')
# Config.set('graphics', 'left', 0)
# Config.set('graphics', 'top',  0)

import sys

import datetime
import threading
import time

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import MeshLinePlot

import MarkerMonitor as m
import MarkerOut
import platform

onRPi = platform.system() == "Linux"

if onRPi:
    import GS_timing as timing
    import RPi.GPIO as GPIO
else:
    import mock_GS_timing as timing
    from mock_gpio import GPIO
    GPIO = GPIO()  # This now gets the singleton instance

GPIO.setmode(GPIO.BCM)

INTERVAL = 0.1  # clock interval in seconds

Window.show_cursor = True
# Window.borderless = True # not working ?
Window.size = (800, 480)

arg = 1  # 0 = random values, 1 = real input from GPIO
if len(sys.argv) > 1:
    arg = int(sys.argv[1])

MM = m.MarkerMonitor(arg)

MM.markerList = []
MM.start()
MM.startTracking()

MO = MarkerOut.MarkerOut()

tableHeader = [{'value': '[b]Value[/b]', 'start': '[b]Start time (s)[/b]', 'end': '[b]End time (s)[/b]', 'duration': '[b]Duration (s)[/b]', 'occurences': '[b]Occurences[/b]'}]
summaryHeader = [{'value': '[b]Value[/b]', 'occurences': '[b]Occurences[/b]'}]


class MarkerWidget(BoxLayout):
    # KL Properties
    cur_time_string = StringProperty("HH:MM:SS")
    cur_value = NumericProperty(-1)
    bulb_value = NumericProperty(0)
    last_marker = StringProperty("Last: XX (dur: N.NNN s, occur: NNN)")
    marker_graph = ObjectProperty(None)
    # current_time = round(MM.getCurTime()/1000,0)
    xmax = NumericProperty(0)
    outputmarker = NumericProperty(42)

    color = ListProperty([1, 0, 0, 1])

    def __init__(self, **kwargs):  # initialize marker widget
        super(MarkerWidget, self).__init__(**kwargs)
        self.tab_num = 1
        self.tracking = False
        self.cur_time = 0
        self.restart_time = 0
        self.prev_marker_count = 0
        self.current_marker_count = 0
        self.num_markers_plotted = 0
        self.prev_value = 0
        # self.cur_value = 0
        self.initial_touch = 0  # initial touch position
        self.starttimer = 0
        self.plot = MeshLinePlot(color=[0.2, 0.8, 1, 1])  # graph
        # self.xmax = 0 # set graph x-axis range
        self.marker_graph.add_plot(self.plot)
        MM.resetMarkers()
        # check marker thread every 100 milliseconds
        self.event = Clock.schedule_interval(self.clock_callback, INTERVAL)
        Clock.schedule_once(lambda dt: self.start_console_injector(), 2.0)

    def switch_callback(self, switchValue):
        if switchValue:  # switched marker analysis ON
            self.tracking = True
            MM.resetMarkers()  # clear markerList
            self.rv.data = []  # clear marker analysis table
            self.rv2.data = []  # clear marker summary table
            self.plot.points = []  # clear graph
            self.prev_marker_count = 0  # reset counters
            self.current_marker_count = 0  # reset counters
            self.num_markers_plotted = 0  # reset counter for marker plot
            self.starttimer = time.time()  # set timers
            self.restart_time = MM.getCurTime()  # set timers

        else:  # marker analysis OFF
            self.tracking = False
            self.update_table()
            self.update_graph()
            self.create_summary_table()

    def clock_callback(self, dt):
        self.cur_value = MM.readCurValue()
        self.cur_time = time.time() - self.starttimer

        if len(MM.markerList) > 0:  # show latest marker
            self.last_marker = "Last: " + str(MM.markerList[-1]['value']) + " (dur: " + str(MM.markerList[-1]['duration'] / 1000) + " s, occur: " + str(MM.markerList[-1]['occurence']) + ")"

        if self.tracking:
            self.cur_time_string = str(datetime.timedelta(seconds=(round(self.cur_time, 0))))  # update timer
            if (self.tab_num == 1):
                self.current_marker_count = len(MM.markerList)
                self.update_table()
                self.prev_marker_count = self.current_marker_count
            if (self.tab_num == 4):
                self.update_graph()

        if (self.tab_num == 3):
            self.bulb_value = self.cur_value

        self.prev_value = self.cur_value

    def switch_tab(self, tab_num):
        self.tab_num = tab_num

    def on_touch_down_graph(self, touch):
        self.initial_touch = touch.x

    def on_touch_up_graph(self, touch):
        self.xmax = self.xmax + ((self.initial_touch - touch.x) / 100)

    def update_graph(self):
        cur_markers_plotted = self.num_markers_plotted
        for marker in MM.markerList[cur_markers_plotted:]:
            self.num_markers_plotted += 1
            starts = round((marker['startTime'] - self.restart_time) / 1000, 5)
            ends = round((marker['endTime'] - self.restart_time) / 1000, 5)
            self.plot.points.append((starts, 0))
            self.plot.points.append((starts, marker['value']))
            self.plot.points.append((ends, marker['value']))
            self.plot.points.append((ends, 0))

        self.xmax = round((MM.getCurTime() - self.restart_time) / 1000, 0)

    def led_state(self, value, bit):
        bit_string = '{:08b}'.format(int(value))  # format value as 8-bit string
        return (int(bit_string[-(bit + 1)]) == 1)

    def update_table(self):
        new_markers = []
        for idx, curMark in enumerate(MM.markerList[self.prev_marker_count:][::-1]):
            new_markers += [{'value': str(curMark['value']),
                             'start': str((curMark['startTime'] - self.restart_time) / 1000),
                             'end': str((curMark['endTime'] - self.restart_time) / 1000),
                             'duration': str((curMark['duration']) / 1000),
                             'occurences': str(curMark['occurence'])
                             }]
        self.rv.data = tableHeader + new_markers + self.rv.data[1:]

    def create_summary_table(self):
        table = []

        for idx in range(0, 256):
            if MM.getMarkerOccurence(idx) is not None:
                table = table + [{'value': str(idx),
                                  'occurences': str(MM.getMarkerOccurence(idx))
                                  }]
        self.rv2.data = summaryHeader + table

    def output_marker(self, mvalue):
        MO.sendMarker(int(mvalue))

    def switch_mode(self, mode, collapsed):
        if mode == 'input' and collapsed == False:
            self.event = Clock.schedule_interval(self.clock_callback, INTERVAL)  #
        else:
            self.event.cancel()
        return True

    def inject_test_marker(self, marker_value, duration=1.0):
        """Inject a test marker directly into the system"""

        def injection_sequence():
            print(f"Injecting marker {marker_value} for {duration} seconds")

            # Method 1: If using test_markers=1 (real GPIO simulation)
            if MM.test_markers == 1:
                pins = [21, 20, 16, 12, 7, 8, 25, 24]
                # Set the pins according to marker value
                for i, pin in enumerate(pins):
                    bit_value = (marker_value >> i) & 1
                    GPIO.pin_states[pin] = bit_value

                # Wait for duration
                time.sleep(duration)

                # Clear pins
                for pin in pins:
                    GPIO.pin_states[pin] = 0

            # Method 2: If using test_markers=0 (random values)
            else:
                # Temporarily override the spoofer
                original_spoofer = MM.valueSpoofer
                MM.valueSpoofer = marker_value
                time.sleep(duration)
                MM.valueSpoofer = 0

            print(f"Marker {marker_value} injection complete")

        # Run injection in a separate thread so it doesn't block the GUI
        injection_thread = threading.Thread(target=injection_sequence)
        injection_thread.daemon = True
        injection_thread.start()

    def start_console_injector(self):
        """Start a console-based marker injector"""

        def console_loop():
            print("\n" + "=" * 50)
            print("MARKER INJECTOR CONSOLE ACTIVE")
            print("Commands:")
            print("  <number>         - Inject marker (0-255)")
            print("  <number> <time>  - Inject marker for duration")
            print("  'help'           - Show this help")
            print("  'quit' or 'q'    - Stop injector")
            print("=" * 50)

            while True:
                try:
                    cmd = input("\nInject marker >>> ").strip()

                    if cmd.lower() in ['quit', 'q', 'exit']:
                        print("Console injector stopped.")
                        break
                    elif cmd.lower() == 'help':
                        print("Enter a number (0-255) to inject a marker")
                        print("Optional: add duration in seconds (e.g., '42 1.5')")
                        continue
                    elif not cmd:
                        continue

                    parts = cmd.split()
                    marker_val = int(parts[0])
                    duration = float(parts[1]) if len(parts) > 1 else 1.0

                    if not (0 <= marker_val <= 255):
                        print("ERROR: Marker value must be between 0 and 255")
                        continue

                    print(f"Injecting marker {marker_val} for {duration} seconds...")
                    self.inject_test_marker(marker_val, duration)

                except (ValueError, IndexError):
                    print("ERROR: Invalid input. Use: <marker_value> [duration]")
                except (KeyboardInterrupt, EOFError):
                    print("\nConsole injector stopped.")
                    break

        # Start console in daemon thread
        console_thread = threading.Thread(target=console_loop, daemon=True)
        console_thread.start()

    # Add a button or menu item to start the injector, or start it automatically:
    def on_start_injector_button(self):
        """Button callback to start the injector"""
        self.start_console_injector()

class MarkerBoxApp(App):
    def on_stop(self):
        MM.stopTracking()
        MM.kill()

    def build(self):
        return MarkerWidget()


if __name__ == "__main__":
    MarkerBoxApp().run()
