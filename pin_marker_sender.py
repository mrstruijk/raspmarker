#!/usr/bin/env python3

# pin_marker_sender.py

import platform
import sys
import time

onRPi = platform.system() == "Linux"

if onRPi:
    from gpiozero import OutputDevice
    from gpiozero.pins.pigpio import PiGPIOFactory
else:
    from mock_gpiozero import MockOutputDevice as OutputDevice, MockPiGPIOFactory as PiGPIOFactory


class PinMarkerSender:
    MARKER_PINS = [21, 20, 16, 12, 7, 8, 25, 24]

    def __init__(self):
        self.pins = {pin: None for pin in self.MARKER_PINS}
        self.factory = PiGPIOFactory()
        self.setup_gpio()

    def setup_gpio(self):
        for pin in self.MARKER_PINS:
            self.pins[pin] = OutputDevice(pin, pin_factory=self.factory)
            self.pins[pin].off()

    def start_marker(self, value: int):
        if not (0 <= value <= 255):
            print(f"Error: Value {value} out of range (0-255)")
            return
        print(f"Starting marker {value} (binary: {format(value, '08b')})")
        for i, pin in enumerate(self.MARKER_PINS):
            bit_value = (value >> i) & 1
            if bit_value:
                self.pins[pin].on()
            else:
                self.pins[pin].off()

    def stop_marker(self):
        for pin in self.MARKER_PINS:
            self.pins[pin].off()
        print("Marker cleared")

    def send_marker(self, value: int, duration: float = 1.0):
        self.start_marker(value)
        time.sleep(duration)
        self.stop_marker()

    def interactive_mode(self):
        try:
            print("Pi Marker Sender - Interactive Mode")
            print("Commands: <number> [duration], start <number>, stop, quit/q")
            while True:
                try:
                    cmd = input("Enter command: ").strip()
                    if cmd.lower() in ['quit', 'q', 'exit']:
                        break
                    if not cmd:
                        continue
                    parts = cmd.split()
                    if parts[0].lower() == 'start':
                        marker_val = int(parts[1])
                        self.start_marker(marker_val)
                    elif parts[0].lower() == 'stop':
                        self.stop_marker()
                    else:
                        marker_val = int(parts[0])
                        duration = float(parts[1]) if len(parts) > 1 else 1.0
                        self.send_marker(marker_val, duration)
                except (ValueError, IndexError):
                    print("Invalid input. Commands: <number> [duration], start <number>, stop, quit/q")
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received.")
        finally:
            self.cleanup()

    def cleanup(self):
        print("Cleaning up GPIO...")
        self.stop_marker()


def main():
    sender = PinMarkerSender()
    try:
        if len(sys.argv) == 1:
            sender.interactive_mode()
        else:
            marker_val = int(sys.argv[1])
            duration = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
            sender.send_marker(marker_val, duration)
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received in main.")
    finally:
        sender.cleanup()


if __name__ == "__main__":
    main()
