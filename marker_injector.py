# marker_injector.py
"""
Simple script to inject markers into the MarkerMonitor system
Run this while your main application is running to simulate marker inputs
"""

import time
import sys
import os

# Import the mock GPIO
sys.path.append(os.path.dirname(__file__))
from mock_gpio import GPIO


def inject_marker(marker_value, duration=1.0):
    """
    Inject a marker value by setting GPIO pins

    Args:
        marker_value: 8-bit value (0-255) to simulate
        duration: how long to hold the marker in seconds
    """
    # Pin mapping from your MarkerMonitor
    pins = [21, 20, 16, 12, 7, 8, 25, 24]

    # Get the singleton GPIO instance
    gpio = GPIO()

    print(f"Injecting marker {marker_value} for {duration} seconds")

    # Set pins based on the binary representation
    for i, pin in enumerate(pins):
        bit_value = (marker_value >> i) & 1
        gpio.pin_states[pin] = bit_value
        if bit_value:
            print(f"  Pin {pin} (bit {i}) = ON")

    # Hold the marker
    time.sleep(duration)

    # Clear all pins
    for pin in pins:
        gpio.pin_states[pin] = 0

    print(f"Marker {marker_value} cleared")


def interactive_mode():
    """Interactive mode to send markers manually"""
    print("Marker Injector - Interactive Mode")
    print("Commands:")
    print("  <number>         - Send marker (0-255)")
    print("  <number> <time>  - Send marker for specific duration")
    print("  'quit' or 'exit' - Exit")
    print()

    while True:
        try:
            cmd = input("Enter marker value (or 'quit'): ").strip().lower()

            if cmd in ['quit', 'exit', 'q']:
                break

            if not cmd:
                continue

            # Parse command
            parts = cmd.split()
            marker_val = int(parts[0])
            duration = float(parts[1]) if len(parts) > 1 else 1.0

            if not (0 <= marker_val <= 255):
                print("Marker value must be between 0 and 255")
                continue

            inject_marker(marker_val, duration)

        except (ValueError, IndexError):
            print("Invalid input. Use: <marker_value> [duration]")
        except KeyboardInterrupt:
            break

    print("Marker injector stopped.")


def demo_sequence():
    """Run a demo sequence of markers"""
    print("Running demo marker sequence...")

    demo_markers = [
        (42, 1.0),
        (100, 0.5),
        (255, 1.5),
        (1, 0.8),
        (128, 1.2),
    ]

    for marker_val, duration in demo_markers:
        print(f"Waiting 2 seconds before next marker...")
        time.sleep(2)
        inject_marker(marker_val, duration)

    print("Demo sequence complete!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            demo_sequence()
        elif sys.argv[1] == "interactive":
            interactive_mode()
        else:
            # Single marker mode
            try:
                marker_val = int(sys.argv[1])
                duration = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
                inject_marker(marker_val, duration)
            except (ValueError, IndexError):
                print("Usage: python marker_injector.py <marker_value> [duration]")
                print("   or: python marker_injector.py demo")
                print("   or: python marker_injector.py interactive")
    else:
        # Default to interactive mode
        interactive_mode()