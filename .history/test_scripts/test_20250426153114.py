import time
import board
import adafruit_dotstar as dotstar

# Set up DotStar strip
dots = dotstar.DotStar(board.D10, board.D11, 144, brightness=1.0, auto_write=True)

try:
    # Light up all LEDs white
    dots.fill((255, 255, 255))
    time.sleep(2)

    # Turn off all LEDs
    dots.fill((0, 0, 0))
    dots.show()  # Force an update immediately
    time.sleep(1)  # Make sure data is latched BEFORE exit

finally:
    dots.deinit()  # Clean up
