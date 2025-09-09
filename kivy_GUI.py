# kivy_GUI.py

import datetime
import sys
import time

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy_garden.graph import MeshLinePlot

import marker_monitor as m
import marker_out

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
MM.start_tracking()

MO = marker_out.MarkerOut()

tableHeader = [{'value': '[b]Value[/b]', 'start': '[b]Start time (s)[/b]', 'end': '[b]End time (s)[/b]', 'duration': '[b]Duration (s)[/b]', 'occurrences': '[b]occurrences[/b]'}]
summaryHeader = [{'value': '[b]Value[/b]', 'occurrences': '[b]Occurrences[/b]'}]


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
        MM.reset_markers()
        # check marker thread every 100 milliseconds
        self.event = Clock.schedule_interval(self.clock_callback, INTERVAL)

    def switch_callback(self, switchValue):
        if switchValue:  # switched marker analysis ON
            self.tracking = True
            MM.reset_markers()  # clear markerList
            self.rv.data = []  # clear marker analysis table
            self.rv2.data = []  # clear marker summary table
            self.plot.points = []  # clear graph
            self.prev_marker_count = 0  # reset counters
            self.current_marker_count = 0  # reset counters
            self.num_markers_plotted = 0  # reset counter for marker plot
            self.starttimer = time.time()  # set timers
            self.restart_time = MM.get_cur_time()  # set timers

        else:  # marker analysis OFF
            self.tracking = False
            self.update_table()
            self.update_graph()
            self.create_summary_table()

    def clock_callback(self, dt):
        self.cur_value = MM.read_cur_value()
        self.cur_time = time.time() - self.starttimer

        if len(MM.markerList) > 0:  # show latest marker
            self.last_marker = "Last: " + str(MM.markerList[-1]['value']) + " (dur: " + str(MM.markerList[-1]['duration'] / 1000) + " s, occur: " + str(MM.markerList[-1]['occurrence']) + ")"

        if self.tracking:
            self.cur_time_string = str(datetime.timedelta(seconds=(round(self.cur_time, 0))))  # update timer
            if self.tab_num == 1:
                self.current_marker_count = len(MM.markerList)
                self.update_table()
                self.prev_marker_count = self.current_marker_count
            if self.tab_num == 4:
                self.update_graph()

        if self.tab_num == 3:
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

        self.xmax = round((MM.get_cur_time() - self.restart_time) / 1000, 0)

    def led_state(self, value, bit):
        bit_string = '{:08b}'.format(int(value))  # format value as 8-bit string
        return int(bit_string[-(bit + 1)]) == 1

    def update_table(self):
        new_markers = []
        for idx, curMark in enumerate(MM.markerList[self.prev_marker_count:][::-1]):
            new_markers += [{'value': str(curMark['value']),
                             'start': str((curMark['startTime'] - self.restart_time) / 1000),
                             'end': str((curMark['endTime'] - self.restart_time) / 1000),
                             'duration': str((curMark['duration']) / 1000),
                             'occurrences': str(curMark['occurrence'])
                             }]
        self.rv.data = tableHeader + new_markers + self.rv.data[1:]

    def create_summary_table(self):
        table = []

        for idx in range(0, 256):
            if MM.get_marker_occurrence(idx) is not None:
                table = table + [{'value': str(idx),
                                  'occurrences': str(MM.get_marker_occurrence(idx))
                                  }]
        self.rv2.data = summaryHeader + table

    def output_marker(self, mvalue):
        MO.send_marker(int(mvalue))

    def switch_mode(self, mode, collapsed):
        if mode == 'input' and collapsed == False:
            self.event = Clock.schedule_interval(self.clock_callback, INTERVAL)  #
        else:
            self.event.cancel()
        return True


class MarkerBoxApp(App):
    def on_stop(self):
        MM.stop_tracking()
        MM.kill()

    def build(self):
        return MarkerWidget()


if __name__ == "__main__":
    try:
        MarkerBoxApp().run()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received, shutting down...")
        MM.stop_tracking()
        MM.kill()
        sys.exit(0)
