import time
import board
import adafruit_dotstar

# Setup LEDs using GPIO 23 (data) and GPIO 24 (clock)
LED_PIN_DATA = board.D23
LED_PIN_CLOCK = board.D24
LED_COUNT = 72
LED_BRIGHTNESS = 0.05  # match your smart mirror startup brightness
leds = adafruit_dotstar.DotStar(LED_PIN_DATA, LED_PIN_CLOCK, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

try:
    # Light all LEDs white
    for i in range(LED_COUNT):
        leds[i] = (255, 255, 255)  # White color
    leds.show()
    time.sleep(2)

    # Turn off all LEDs
    for i in range(LED_COUNT):
        leds[i] = (0, 0, 0)  # Black (off)
    leds.show()
    time.sleep(0.5)

finally:
    leds.deinit()
