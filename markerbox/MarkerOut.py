import platform

onRPi = (platform.system() == 'Linux')

if onRPi:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)

    PIN_DATA = 26 # carries the serial bit stream.
    PIN_LATCH = 19 # moves the shifted bits from the shift register’s internal buffer to its output pins once a full byte has been sent.
    PIN_CLOCK = 13 # steps the shift register forward one bit for each pulse.
    "These pin numbers (26, 1913) match a typical wiring for a 74HC595 (or similar) 8‑bit shift register, which is often used to expand the number of digital outputs."

    GPIO.setup(PIN_DATA, GPIO.OUT)
    GPIO.setup(PIN_LATCH, GPIO.OUT)
    GPIO.setup(PIN_CLOCK, GPIO.OUT)


class MarkerOut:
    def __init__(self):
        super().__init__()

    "This method sends an 8‑bit value out to the shift register. It takes an 8-bit value as the input"
    def send_marker_to_raspmarker(self, bit_value):
        if onRPi:
            GPIO.output(PIN_LATCH, 0) # Latch low: disconnect the storage register from the shift register, allowing us to update the bits safely.
            for x in range(8):
                bit = (bit_value >> x) & 1 # extracts the x‑th bit (LSB first)...
                GPIO.output(PIN_DATA, bit) # ...put that bit on the data line
                GPIO.output(PIN_CLOCK, 1) # A quick high‑then‑low pulse on PIN_CLOCK (1 → 0) tells the shift register to read the data line and advance one position.
                GPIO.output(PIN_CLOCK, 0)
            GPIO.output(PIN_LATCH, 1) # Latch high: copies the newly shifted byte from the shift register to its output pins, making the new pattern visible the attached hardware
