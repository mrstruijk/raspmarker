#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# markermonitor.py

import platform
import random
import threading
import time

onRPi = (platform.system() == 'Linux')

if onRPi:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)

import GS_timing as timing


class MarkerMonitor(threading.Thread):
    """ Utility for monitoring markers received on logic (LPT/TTL) ports. These usually consists of markers from devices like Biopac/Biosemi that are being sent to the Pi. Marker 0 can be used to end a previous marker, or by sending a new marker. There cannot be two simultaneous markers (unless you use sending the same marker twice as a kind of start-stop marker). """

    def start_thread(self):
        self.start()

    def __init__(self, use_random_markers : bool,
                 input_pins=[21, 20, 16, 12, 7, 8, 25, 24],
                 pollInterval_ms=1
                 ):
        # Constructor.
        super().__init__()

        self.use_random_markers = use_random_markers

        # Set all ports as GPIO inputs
        if onRPi:
            for pin in input_pins:
                GPIO.setup(pin, GPIO.IN)

        # Marker params:
        self.pollInterval_ms = pollInterval_ms
        self.input_pins = input_pins

        # Flag to enable marker tracking. Markers will always be read, and the
        # curValue will always be updated when the thread is running.
        # However, the markerList will only be updated when the flag is set to
        # true.
        self.trackMarkers = False

        self.isAlive = True

        # List and dictionary to track markers and their occurrences:
        self.markerList = list()
        self.markerList = []
        self.markerOccurDict = {}

        # Callbacks to be executed when the value changes:
        self.marker_callbacks = []

        # Tracking parameters:
        self.lastValue = 0
        self.curValue = 0

        # Add startTime prop:
        self.startTime = 0.0

        # Variable for faking a marker signal:
        self.valueSpoofer = 0

        self.resetMarkers()

    def subscribe(self, callback):
        # subscribe to list of callbacks
        self.marker_callbacks.append(callback)

    def callback(self, value : int = 0):
        if self.marker_callbacks is not None and len(self.marker_callbacks) > 0:
            for callback in self.marker_callbacks:
                callback(value)

    def run(self):

        # Initialize vars:
        markerBeingReceived = {}
        self.lastValue = self.readCurValue()
        self.startTime = timing.millis()

        # TODO: make lastValue and curValue local, not dyn props.

        print("running")
        while self.isAlive:
            # Read out latest marker value:
            self.curValue = self.readCurValue()

            if self.trackMarkers:
                if self.curValue != self.lastValue: # If the value has changed...
                    # print(f"current value ({self.curValue} != last value ({self.lastValue}))")

                    self.callback(value=self.curValue) # Let every interested party know that a marker has been received. This includes a 0 marker.

                    self.lastValue = self.curValue # Store current value as the last value

                    if markerBeingReceived != {}:
                        # If a marker was being received and the value changed,
                        # end the marker, and push it into the marker list:
                        markerBeingReceived["endTime"] = self.getCurTime()
                        self.addNewMarker(**markerBeingReceived)

                        # Reset current marker:
                        markerBeingReceived = {}

                    if self.curValue != 0:
                        # If the new marker sent is not zero, we want to create a new marker:
                        markerBeingReceived = {'value': self.curValue,
                                               'startTime': self.getCurTime()}



                        # print(f"MarkerBeingReceived: {markerBeingReceived}")
                        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
                        # RUN NEW MARKER CALLBACKS
                        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX



            # Sleep until the next poll:
            time.sleep(self.pollInterval_ms / 1000.0)

    def getCurTime(self):
        return round(timing.millis() - self.startTime)

    def startTracking(self):
        self.trackMarkers = True
        self.startTime = timing.millis()
        self.resetMarkers()
        pass

    def stopTracking(self):
        self.trackMarkers = False
        pass

    def kill(self):
        self.isAlive = False
        pass

    def resetMarkers(self):
        self.markerList = list()
        self.markerOccurDict = {}
        pass

    def addNewMarker(self, value, startTime, endTime):
        """ Adds a new marker to the marker list. This happens when the marker has 'finished': so it has started and stopped """

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
            'startTime': startTime,
            'endTime': endTime,
            'duration': endTime - startTime,
            'occurrence': occurrence})

        # print(f"MarkerReceived: {self.markerList[-1]}")

    def get_marker_occurrence(self, value):
        return self.markerOccurDict.get(value)

    def readCurValue(self):
        if self.use_random_markers == False and onRPi:
                return sum([int(GPIO.input(p)) * (2 ** i) for i, p in enumerate(self.input_pins)])
        elif self.use_random_markers: # Use random markers
            N = 100  # Make this dependent on the polling interval.

            curMark = self.valueSpoofer
            # Have a 1 in N chance to change the current marker:
            if random.randint(0, N) == 1:
                # Have a 1 in N/4 chance to go to a non-zero marker:
                if random.randint(0, round(N / 4)) == 1:
                    curMark = random.randint(0, 255)
                else: # in most cases marker '0' will be sent out.
                    curMark = 0

            self.valueSpoofer = curMark
            # print("DEBUG: Current value:", curMark)
            return curMark
        elif not self.use_random_markers:
            return 0
        return None

        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        # MAKE GENERATOR TO RETURN PARSED MARKERS!
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
