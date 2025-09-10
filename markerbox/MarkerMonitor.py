# -*- coding: utf-8 -*-
"""
Created on Sun Nov  4 19:51:39 2018

@author: Elio
"""

import platform
import random
import threading
import time

import GS_timing as timing

onRPi = (platform.system() == 'Linux')

if onRPi:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)


# Class for monitoring markers received on logic (LPT/TTL) ports.
class MarkerMonitor(threading.Thread):

    def __init__(self, test_markers, \
                 ports=[21, 20, 16, 12, 7, 8, 25, 24], \
                 pollInterval_ms=1 \
                 ):
        # Constructor.
        super().__init__()

        self.test_markers = test_markers

        # Set all ports as GPIO inputs
        if onRPi:
            for port in ports:
                GPIO.setup(port, GPIO.IN)

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

    def run(self):

        # Initialize vars:
        markerBeingRecieved = {}
        self.lastValue = self.readCurValue()
        self.startTime = timing.millis()

        # TODO: make lastValue and curValue local, not dyn props.

        while self.isAlive:

            # Read out latest marker value:
            self.curValue = self.readCurValue()

            if self.trackMarkers:
                # If tracking is enabled:

                if self.curValue != self.lastValue:
                    # If the value has changed...
                    self.lastValue = self.curValue

                    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
                    # RUN NEW VALUE CALLBACKS
                    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

                    if markerBeingRecieved != {}:
                        # If a marker was being recieved and the value changed,
                        # end the marker, and push it into the marker list:

                        markerBeingRecieved["endTime"] = self.getCurTime()
                        self.addNewMarker(**markerBeingRecieved)

                        # Reset current marker:
                        markerBeingRecieved = {}

                    if self.curValue != 0:
                        # If the new value is not zero, create a new marker:

                        # Make new marker:
                        markerBeingRecieved = {'value': self.curValue, \
                                               'startTime': self.getCurTime()}

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
        ''' Adds a new marker to the marker list. '''

        # Calculate the occurrence:
        if self.markerOccurDict.get(value) == None:
            occurrence = 1
        else:
            occurrence = self.markerOccurDict.get(value) + 1

        # Save the current occurrence so that it can be easily tracked:
        self.markerOccurDict[value] = occurrence

        # Make marker, and append it to the list:
        self.markerList.append({ \
            'value': value, \
            'startTime': startTime, \
            'endTime': endTime, \
            'duration': endTime - startTime, \
            'occurrence': occurrence})

    def getMarkerOccurence(self, value):
        return self.markerOccurDict.get(value)

    def readCurValue(self):
        if self.test_markers == 1 and onRPi:
            # curMark = 0

            # for i, port in enumerate(self.ports):
            #     if GPIO.input(port):
            #         curMark = curMark + 2 ** i
            # return curMark
            return sum([int(GPIO.input(p)) * (2 ** i) for i, p in enumerate(self.ports)])
        else:
            N = 10  # Make this dependent on the polling interval.

            # Have a 1 in N chance to change the current marker:
            curMark = self.valueSpoofer
            if random.randint(0, N) == 1:

                # Have a 1 in N/4 chance to go to a non zero marker:
                if random.randint(0, round(N / 4)) == 1:
                    curMark = random.randint(0, 255)
                else:
                    curMark = 0
            # if self.trackMarkers:
            # print("TRACK: %.2f: %i." % (self.getCurTime(),curMark))
            # else:
            #    #print("%.2f: %i." % (self.getCurTime(),curMark))
            self.valueSpoofer = curMark
            return curMark

        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        # MAKE GENERATOR TO RETURN PARSED MARKERS!
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
