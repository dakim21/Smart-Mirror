import time
import board
import adafruit_dotstar as dotstar

# Set up DotStar strip
dots = dotstar.DotStar(board.D10, board.D11, 144, brightness=1.0, auto_write=True)

# Light up all LEDs white
dots.fill((255, 255, 255))

# Wait for 2 seconds
time.sleep(2)

# Turn off all LEDs
dots.fill((0, 0, 0))
