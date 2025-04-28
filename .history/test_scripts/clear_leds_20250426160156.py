import time
import board
import adafruit_dotstar

dots = adafruit_dotstar.DotStar(board.D23, board.D24, 72, brightness=0.05, auto_write=False)

for i in range(72):
    dots[i] = (0, 0, 0)
dots.show()

time.sleep(0.5)  # Give it time to fully send