'''
Script to turn off LEDS
'''

import time
import board
import adafruit_dotstar

#initialize LEDS
dots = adafruit_dotstar.DotStar(board.SCLK, board.MOSI, 72, brightness=0.05, auto_write=False)

#000 for black
for i in range(72):
    dots[i] = (0, 0, 0)
dots.show()

time.sleep(0.5)