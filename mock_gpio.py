# mock_gpio.py (improved version)
import threading


class GPIOMeta(type):
    """Metaclass to implement singleton pattern"""
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class GPIO(metaclass=GPIOMeta):
    BCM = "BCM"
    OUT = "OUT"
    IN = "IN"
    HIGH = 1
    LOW = 0

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.pin_states = {}
            self.pin_modes = {}
            self.initialized = True

    def setmode(self, mode):
        print(f"[MOCK GPIO] setmode({mode})")

    def setup(self, pin, mode):
        self.pin_states[pin] = 0
        self.pin_modes[pin] = mode
        print(f"[MOCK GPIO] setup(pin={pin}, mode={mode})")

    def output(self, pin, value):
        if self.pin_modes.get(pin) == self.OUT:
            self.pin_states[pin] = value
            print(f"[MOCK GPIO] output(pin={pin}, value={value})")
        else:
            print(f"[MOCK GPIO] Warning: trying to output to input pin {pin}")

    def input(self, pin):
        val = self.pin_states.get(pin, 0)
        return val

    def cleanup(self):
        print("[MOCK GPIO] cleanup()")

    def set_input_pin(self, pin, value):
        """Helper method to simulate input changes"""
        if self.pin_modes.get(pin) == self.IN:
            self.pin_states[pin] = value
            print(f"[MOCK GPIO] Simulated input: pin {pin} = {value}")
        else:
            print(f"[MOCK GPIO] Warning: pin {pin} is not configured as input")