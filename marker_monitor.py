# marker_monitor.py

import platform
import random
import threading
import time

onRPi = platform.system() == "Linux"

if onRPi:
    import GS_timing as timing
    from gpiozero import InputDevice
    from gpiozero.pins.pigpio import PiGPIOFactory
else:
    import mock_GS_timing as timing
    from mock_gpiozero import MockInputDevice as InputDevice, MockPiGPIOFactory as PiGPIOFactory
print(f"Marker_monitor is on Pi: {onRPi}")


# Class for monitoring markers received on logic (LPT/TTL) ports.
class MarkerMonitor(threading.Thread):

    def __init__(self, random_test_markers,
                 ports=[21, 20, 16, 12, 7, 8, 25, 24],
                 pollInterval_ms=1
                 ):
        # Constructor.
        super().__init__()

        self.factory = PiGPIOFactory()  # connect to pigpio daemon

        self.random_test_markers = random_test_markers

        # Marker params:
        self.pollInterval_ms = pollInterval_ms
        self.ports = ports

        # Flag to enable marker tracking. Markers will always be read, and the
        # curValue will always be updated when the thread is running.
        # However, the markerList will only be updated when the flag is set to
        # true.
        self.trackMarkers = False

        self.isAlive = True

        # List and dictionary to track markers and their occurrences:
        self.markerList = list()
        self.markerOccurDict = {}

        # Callbacks to be executed when the value changes:
        self.valueChangeCallbacks = {}

        # Tracking parameters:
        self.lastValue = 0
        self.curValue = 0

        # Add startTime prop:
        self.startTime = 0.0

        # Variable for faking a marker signal:
        self.valueSpoofer = 0

        # Initialize ports via factorio
        self.ports = [InputDevice(p, pin_factory=self.factory) for p in ports]

    def run(self):

        # Initialize vars:
        marker_being_received = {}
        self.lastValue = self.read_cur_value()
        self.startTime = timing.millis()

        # TODO: make lastValue and curValue local, not dyn props.

        while self.isAlive:

            # Read out latest marker value:
            self.curValue = self.read_cur_value()

            if self.trackMarkers:
                # If tracking is enabled:

                if self.curValue != self.lastValue:
                    # If the value has changed...
                    self.lastValue = self.curValue

                    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
                    # RUN NEW VALUE CALLBACKS
                    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

                    if marker_being_received != {}:
                        # If a marker was being received and the value changed,
                        # end the marker, and push it into the marker list:

                        marker_being_received['end_time'] = self.get_cur_time()
                        self.add_new_marker(**marker_being_received)

                        # Reset current marker:
                        marker_being_received = {}

                    if self.curValue != 0:
                        # If the new value is not zero, create a new marker:

                        # Make new marker:
                        marker_being_received = {'value': self.curValue, 'start_time': self.get_cur_time()}

                        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
                        # RUN NEW MARKER CALLBACKS
                        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

            # Sleep until the next poll:
            time.sleep(self.pollInterval_ms / 1000.0)

    def get_cur_time(self):
        return round(timing.millis() - self.startTime)

    def start_tracking(self):
        self.trackMarkers = True
        self.startTime = timing.millis()
        self.reset_markers()
        pass

    def stop_tracking(self):
        self.trackMarkers = False
        pass

    def kill(self):
        self.isAlive = False
        pass

    def reset_markers(self):
        self.markerList = list()
        self.markerOccurDict = {}
        pass

    def add_new_marker(self, value, start_time, end_time):
        """ Adds a new marker to the marker list. """

        # Calculate the occurrence:
        if self.markerOccurDict.get(value) is None:
            occurrence = 1
        else:
            occurrence = self.markerOccurDict.get(value) + 1

        # Save the current occurrence so that it can be easily tracked:
        self.markerOccurDict[value] = occurrence

        # Make marker, and append it to the list:
        self.markerList.append({
            'value': value,
            'startTime': start_time,
            'endTime': end_time,
            'duration': end_time - start_time,
            'occurrence': occurrence})

    def get_marker_occurrence(self, value):
        return self.markerOccurDict.get(value)

    def read_cur_value(self):
        if self.random_test_markers == 0:
            val = sum([int(dev.value) * (2 ** i) for i, dev in enumerate(self.ports)])
            return val
        if self.random_test_markers == 1:
            mock_polling_interval = 10  # Make this dependent on the polling interval.

            # Have a 1 in N chance to change the current marker:
            cur_mark = self.valueSpoofer
            if random.randint(0, mock_polling_interval) == 1:

                # Have a 1 in N/4 chance to go to a non-zero marker:
                if random.randint(0, round(mock_polling_interval / 4)) == 1:
                    cur_mark = random.randint(0, 255)
                else:
                    cur_mark = 0
            self.valueSpoofer = cur_mark
            return cur_mark
        else:
            print("Unexpected value. 1 = use random markers (for testing), 0 = use real markers.")
            return None

        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        # MAKE GENERATOR TO RETURN PARSED MARKERS!
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
