import platform

onRPi = platform.system() == "Linux"

if onRPi:
    import RPi.GPIO as GPIO
else:
    from mock_gpio import GPIO

    GPIO = GPIO()  # instantiate the mock

GPIO.setmode(GPIO.BCM)

PIN_DATA = 26
PIN_LATCH = 19
PIN_CLOCK = 13

if not onRPi:
    GPIO.setup(PIN_DATA, GPIO.OUT)
    GPIO.setup(PIN_LATCH, GPIO.OUT)
    GPIO.setup(PIN_CLOCK, GPIO.OUT)


class MarkerOut:
    def __init__(self):
        super().__init__()

    def sendMarker(self, value):
        if onRPi:
            GPIO.output(PIN_LATCH, 0)
            for x in range(8):
                GPIO.output(PIN_DATA, (value >> x) & 1)
                GPIO.output(PIN_CLOCK, 1)
                GPIO.output(PIN_CLOCK, 0)
            GPIO.output(PIN_LATCH, 1)
        else:
            # Optional: log the value in mock mode
            print(f"[MOCK MarkerOut] sendMarker({value})")
