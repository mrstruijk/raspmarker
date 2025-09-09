# mock_gpiozero.py
import threading


class PinRegistry:
    """Singleton registry for pin states"""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.pin_states = {}
        return cls._instance

    def set_pin(self, pin, value):
        self.pin_states[pin] = value

    def get_pin(self, pin):
        return self.pin_states.get(pin, 0)


class MockInputDevice:
    def __init__(self, pin, pin_factory=None):
        self.pin = pin
        self.registry = PinRegistry()
        self.registry.set_pin(pin, 0)
        print(f"[MOCK gpiozero] InputDevice(pin={pin}) initialized")

    @property
    def value(self):
        return self.registry.get_pin(self.pin)

    def set_value(self, val):
        self.registry.set_pin(self.pin, 1 if val else 0)


class MockOutputDevice:
    def __init__(self, pin, pin_factory=None):
        self.pin = pin
        self.registry = PinRegistry()
        self.registry.set_pin(pin, 0)
        print(f"[MOCK gpiozero] OutputDevice(pin={pin}) initialized")

    def on(self):
        self.registry.set_pin(self.pin, 1)
        print(f"[MOCK gpiozero] OutputDevice(pin={self.pin}).on()")

    def off(self):
        self.registry.set_pin(self.pin, 0)
        print(f"[MOCK gpiozero] OutputDevice(pin={self.pin}).off()")

    @property
    def value(self):
        return self.registry.get_pin(self.pin)

    @value.setter
    def value(self, new_val):
        self.registry.set_pin(self.pin, 1 if new_val else 0)
        print(f"[MOCK gpiozero] OutputDevice(pin={self.pin}).value = {new_val}")


class MockPiGPIOFactory:
    """Mock factory for gpiozero PiGPIOFactory."""

    def __init__(self):
        self.registry = PinRegistry()
        print("[MOCK gpiozero] PiGPIOFactory initialized")
