#!/usr/bin/env python3
# pi_marker_sender.py

import RPi.GPIO as GPIO
import time
import sys

MARKER_PINS = [21, 20, 16, 12, 7, 8, 25, 24]  # bit 0 to bit 7

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    for pin in MARKER_PINS:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

def start_marker(value):
    """Set the marker pins to represent the value and leave them on"""
    if not (0 <= value <= 255):
        print(f"Error: Value {value} out of range (0-255)")
        return
    print(f"Starting marker {value} (binary: {format(value, '08b')})")
    for i, pin in enumerate(MARKER_PINS):
        bit_value = (value >> i) & 1
        GPIO.output(pin, GPIO.HIGH if bit_value else GPIO.LOW)
        if bit_value:
            print(f"  Pin {pin} (bit {i}) = HIGH")

def stop_marker():
    """Clear all marker pins"""
    for pin in MARKER_PINS:
        GPIO.output(pin, GPIO.LOW)
    print("Marker cleared")

def send_marker(value, duration=1.0):
    """Send a marker for a specific duration"""
    start_marker(value)
    time.sleep(duration)
    stop_marker()

def interactive_mode():
    setup_gpio()
    try:
        print("Pi Marker Sender - Interactive Mode")
        print("Commands:")
        print("  <number>         - Send marker (0-255) for 1 second")
        print("  <number> <time>  - Send marker for specific duration")
        print("  start <number>   - Start marker (leave it on)")
        print("  stop             - Stop/clear current marker")
        print("  'quit' or 'q'    - Exit")
        print()
        while True:
            try:
                cmd = input("Enter command: ").strip()
                if cmd.lower() in ['quit', 'q', 'exit']:
                    break
                if not cmd:
                    continue
                parts = cmd.split()
                if parts[0].lower() == 'start':
                    if len(parts) < 2:
                        print("Usage: start <marker_value>")
                        continue
                    marker_val = int(parts[1])
                    start_marker(marker_val)
                elif parts[0].lower() == 'stop':
                    stop_marker()
                else:
                    marker_val = int(parts[0])
                    duration = float(parts[1]) if len(parts) > 1 else 1.0
                    send_marker(marker_val, duration)
            except (ValueError, IndexError):
                print("Invalid input. Commands:")
                print("  <marker_value> [duration]")
                print("  start <marker_value>")
                print("  stop")
            except KeyboardInterrupt:
                break
    finally:
        cleanup()

def cleanup():
    print("Cleaning up GPIO...")
    stop_marker()
    GPIO.cleanup()

def main():
    if len(sys.argv) == 1:
        interactive_mode()
    elif len(sys.argv) >= 2:
        try:
            setup_gpio()
            marker_val = int(sys.argv[1])
            duration = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
            send_marker(marker_val, duration)
        except ValueError:
            print("Usage: python3 pi_marker_sender.py <marker_value> [duration]")
            print("   or: python3 pi_marker_sender.py  (for interactive mode)")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            cleanup()

if __name__ == "__main__":
    main()
