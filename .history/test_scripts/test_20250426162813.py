import time
import board
import adafruit_dotstar

# Initialize using hardware SPI (SCLK, MOSI)
dots = adafruit_dotstar.DotStar(board.SCLK, board.MOSI, 72, brightness=0.5, auto_write=False)

# Turn all LEDs white
for i in range(72):
    dots[i] = (255, 255, 255)
dots.show()

time.sleep(2)

# Turn all LEDs off
for i in range(72):
    dots[i] = (0, 0, 0)
dots.show()
