import time
import board
import adafruit_dotstar

# Use hardware SPI now: Clock = SCLK, Data = MOSI
dots = adafruit_dotstar.DotStar(board.SCLK, board.MOSI, 72, brightness=0.05, auto_write=False)

# Set all LEDs to black (off)
for i in range(72):
    dots[i] = (0, 0, 0)
dots.show()

time.sleep(0.5)  # Give it time to fully send