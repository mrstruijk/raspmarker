"""
GS_timing.py
Arduino-like millis() and micros() timing functions for Python
Now supports Windows, Linux, and macOS.
"""

import ctypes
import os
import sys
import time

VERSION = '0.3.0'

# -------------------------------------------------------------------
# FUNCTIONS:
# -------------------------------------------------------------------
if os.name == 'nt':  # Windows
    def micros():
        tics = ctypes.c_int64()
        freq = ctypes.c_int64()
        ctypes.windll.Kernel32.QueryPerformanceCounter(ctypes.byref(tics))
        ctypes.windll.Kernel32.QueryPerformanceFrequency(ctypes.byref(freq))
        return tics.value * 1e6 / freq.value

    def millis():
        tics = ctypes.c_int64()
        freq = ctypes.c_int64()
        ctypes.windll.Kernel32.QueryPerformanceCounter(ctypes.byref(tics))
        ctypes.windll.Kernel32.QueryPerformanceFrequency(ctypes.byref(freq))
        return tics.value * 1e3 / freq.value

elif os.name == 'posix':
    if sys.platform.startswith("linux"):  # Linux
        CLOCK_MONOTONIC_RAW = 4  # from <linux/time.h>

        class timespec(ctypes.Structure):
            _fields_ = [
                ('tv_sec', ctypes.c_long),
                ('tv_nsec', ctypes.c_long)
            ]

        librt = ctypes.CDLL('librt.so.1', use_errno=True)
        clock_gettime = librt.clock_gettime
        clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]

        def monotonic_time():
            t = timespec()
            if clock_gettime(CLOCK_MONOTONIC_RAW, ctypes.pointer(t)) != 0:
                errno_ = ctypes.get_errno()
                raise OSError(errno_, os.strerror(errno_))
            return t.tv_sec + t.tv_nsec * 1e-9

        def micros():
            return monotonic_time() * 1e6

        def millis():
            return monotonic_time() * 1e3

    elif sys.platform == "darwin":  # macOS
        try:
            CLOCK_MONOTONIC_RAW = time.CLOCK_MONOTONIC_RAW
        except AttributeError:
            CLOCK_MONOTONIC_RAW = time.CLOCK_MONOTONIC

        def micros():
            return time.clock_gettime_ns(CLOCK_MONOTONIC_RAW) / 1000.0

        def millis():
            return time.clock_gettime_ns(CLOCK_MONOTONIC_RAW) / 1e6


# Other timing functions
def delay(delay_ms):
    t_start = millis()
    while millis() - t_start < delay_ms:
        pass


def delayMicroseconds(delay_us):
    t_start = micros()
    while micros() - t_start < delay_us:
        pass


# -------------------------------------------------------------------
# TESTS
# -------------------------------------------------------------------
if __name__ == "__main__":
    print("Testing micros:")
    tStart = micros()
    for _ in range(5):
        tNow = micros()
        print(f"dt(us) = {tNow - tStart}")
        tStart = tNow

    print("\nTesting millis:")
    tStart = millis()
    for _ in range(5):
        tNow = millis()
        print(f"dt(ms) = {tNow - tStart}")
        tStart = tNow

    print("\nDelay test (ms):")
    for i in range(3):
        delay(1000)
        print(i + 1)
