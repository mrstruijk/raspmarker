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
print(f"Pin_marker_sender is on Pi: {onRPi}")

MARKER_PINS = [21, 20, 16, 12, 7, 8, 25, 24]  # bit 0 to bit 7
pins = {pin: None for pin in MARKER_PINS}


def setup_gpio():
    factory = PiGPIOFactory()
    for pin in MARKER_PINS:
        pins[pin] = OutputDevice(pin, pin_factory=factory)
        pins[pin].off()


def start_marker(value):
    if not (0 <= value <= 255):
        print(f"Error: Value {value} out of range (0-255)")
        return
    print(f"Starting marker {value} (binary: {format(value, '08b')})")
    for i, pin in enumerate(MARKER_PINS):
        bit_value = (value >> i) & 1
        if bit_value:
            pins[pin].on()
        else:
            pins[pin].off()


def stop_marker():
    for pin in MARKER_PINS:
        pins[pin].off()
    print("Marker cleared")


def send_marker(value, duration=1.0):
    start_marker(value)
    time.sleep(duration)
    stop_marker()


def interactive_mode():
    setup_gpio()
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
                    start_marker(marker_val)
                elif parts[0].lower() == 'stop':
                    stop_marker()
                else:
                    marker_val = int(parts[0])
                    duration = float(parts[1]) if len(parts) > 1 else 1.0
                    send_marker(marker_val, duration)
            except (ValueError, IndexError):
                print("Invalid input. Commands: <number> [duration], start <number>, stop, quit/q")
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received.")
    finally:
        cleanup()


def cleanup():
    print("Cleaning up GPIO...")
    stop_marker()


def main():
    try:
        if len(sys.argv) == 1:
            interactive_mode()
        else:
            setup_gpio()
            marker_val = int(sys.argv[1])
            duration = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
            send_marker(marker_val, duration)
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received in main.")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
