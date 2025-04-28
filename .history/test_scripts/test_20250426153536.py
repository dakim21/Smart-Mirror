import time
import board
import adafruit_dotstar

# Setup for bitbang mode using GPIO 23 (data) and 24 (clock)
dots = adafruit_dotstar.DotStar(
    board.D23, board.D24,
    72, brightness=1.0, auto_write=True
)

try:
    # Turn all LEDs white
    dots.fill((255, 255, 255))
    time.sleep(2)

    # Turn all LEDs off
    dots.fill((0, 0, 0))
    dots.show()
    time.sleep(0.5)

finally:
    dots.deinit()
