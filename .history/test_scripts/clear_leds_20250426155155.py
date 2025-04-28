import time
import board
import adafruit_dotstar

# Setup LED strip (EXACT same as your mirror app)
dots = adafruit_dotstar.DotStar(board.D23, board.D24, 72, brightness=0.05, auto_write=False)

# First flush attempt
for i in range(72):
    dots[i] = (0, 0, 0)
dots.show()

# Wait a bit
time.sleep(0.5)

# SECOND flush attempt (double-send just in case)
for i in range(72):
    dots[i] = (0, 0, 0)
dots.show()

# Stay alive briefly so data fully sends
time.sleep(1)

# Shutdown cleanly
dots.deinit()
