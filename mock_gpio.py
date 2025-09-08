# mock_gpio.py
import random


class GPIO:
    BCM = "BCM"
    OUT = "OUT"
    IN = "IN"
    HIGH = 1
    LOW = 0

    def __init__(self):
        self.pin_states = {}

    def setmode(self, mode):
        print(f"[MOCK GPIO] setmode({mode})")

    def setup(self, pin, mode):
        self.pin_states[pin] = 0
        print(f"[MOCK GPIO] setup(pin={pin}, mode={mode})")

    def output(self, pin, value):
        self.pin_states[pin] = value
        print(f"[MOCK GPIO] output(pin={pin}, value={value})")

    def input(self, pin):
        val = self.pin_states.get(pin, 0)
        # simulate random input changes for testing
        val = random.randint(0, 1)
        print(f"[MOCK GPIO] input({pin}) -> {val}")
        return val

    def cleanup(self):
        print("[MOCK GPIO] cleanup()")
