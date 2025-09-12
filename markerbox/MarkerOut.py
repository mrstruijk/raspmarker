import platform

onRPi = (platform.system() == 'Linux')

if onRPi:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM) # Set pins to use common pin numbering system instead of physical pins

    # Default pin assignments for 74HC595 shift register
    PIN_DATA = 26 # carries the serial bit stream.
    PIN_LATCH = 19 # moves the shifted bits from the shift register’s internal buffer to its output pins once a full byte has been sent.
    PIN_CLOCK = 13 # steps the shift register forward one bit for each pulse.

    GPIO.setup(PIN_DATA, GPIO.OUT)
    GPIO.setup(PIN_LATCH, GPIO.OUT)
    GPIO.setup(PIN_CLOCK, GPIO.OUT)


class MarkerOut:
    """Utility for sending 8‑bit markers to a 74HC595 shift register. These are usually connected to a Biosemi/Biopac device, where these markers can be read / stored."""
    def __init__(self):
        pass

    def send_marker_to_lpt(self, value: int):
        """
             Send an 8‑bit integer (`0–255`) to the LPT attached hardware (Biosemi / Biopac).
         """
        if onRPi:
            GPIO.output(PIN_LATCH, 0) # Latch low: disconnect the storage register from the shift register, allowing us to update the bits safely.
            for x in range(8):
                bit = (value >> x) & 1 # extracts the x‑th bit (LSB first)...
                GPIO.output(PIN_DATA, bit) # ...put that bit on the data line
                GPIO.output(PIN_CLOCK, 1) # A quick high‑then‑low pulse on PIN_CLOCK (1 → 0) tells the shift register to read the data line and advance one position.
                GPIO.output(PIN_CLOCK, 0)
            GPIO.output(PIN_LATCH, 1) # Latch high: copies the newly shifted byte from the shift register to its output pins, making the new pattern visible the attached hardware
            print(f"Sending value {value} to the LPT attached hardware.")
        else:
            print(f"Mock send_marker_to_lpt with value {value}.")

    @staticmethod
    def cleanup():
        if onRPi:
            GPIO.cleanup()


if __name__ == "__main__":
    import time

    marker = MarkerOut()

    def demo():
        for value in (0xAA, 0x55, 0xFF, 0x00):
            marker.send_marker_to_lpt(value)
            time.sleep(1)                 # Pause so you can see the change

    try:
        demo()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        marker.cleanup()
        print("GPIO cleaned up.")