import time
import board
import digitalio
import adafruit_dotstar

# Set up manual GPIO pins
data_pin = digitalio.DigitalInOut(board.D23)
clock_pin = digitalio.DigitalInOut(board.D24)

# Initialize DotStar strip
dots = adafruit_dotstar.DotStar(
    clock_pin, data_pin,
    144, brightness=1.0, auto_write=True
)

try:
    # Turn all LEDs white
    dots.fill((255, 255, 255))
    time.sleep(2)

    # Turn all LEDs off
    dots.fill((0, 0, 0))
    dots.show()
    time.sleep(1)

finally:
    dots.deinit()
