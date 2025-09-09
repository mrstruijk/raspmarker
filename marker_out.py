# marker_out.py
import platform

onRPi = platform.system() == "Linux"

if onRPi:
    from gpiozero import OutputDevice
    from gpiozero.pins.pigpio import PiGPIOFactory
else:
    from mock_gpiozero import MockOutputDevice as OutputDevice, MockPiGPIOFactory as PiGPIOFactory

PIN_DATA = 26
PIN_LATCH = 19
PIN_CLOCK = 13


class MarkerOut:
    def __init__(self):
        self.factory = PiGPIOFactory() if onRPi else None

        self.data = OutputDevice(PIN_DATA, pin_factory=self.factory)
        self.latch = OutputDevice(PIN_LATCH, pin_factory=self.factory)
        self.clock = OutputDevice(PIN_CLOCK, pin_factory=self.factory)

    def send_marker(self, value):
        """Send a marker by setting the 8-bit value on the pins."""
        self.latch.off()
        for bit in range(8):
            self.data.value = (value >> bit) & 1
            self.clock.on()
            self.clock.off()
        self.latch.on()
        if not onRPi:
            print(f"[MOCK MarkerOut] sendMarker({value})")
