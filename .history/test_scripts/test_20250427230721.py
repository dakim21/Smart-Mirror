'''
***OUTDATED - USING SPI PINS
Script to test distance readings

1. sends one trigger pulse
2. waits for one echo
3. measures one round-trip time
4. converts that single time into a distance value
5. prints it
'''

import time
import board
import adafruit_dotstar

#initiallize LEDS (pins 19 and 23)
dots = adafruit_dotstar.DotStar(board.SCLK, board.MOSI, 72, brightness=0.5, auto_write=False)

#turn the leds to white
for i in range(72):
    dots[i] = (255, 255, 255)
dots.show()

#wait 2 seconds
time.sleep(2)

#turn to black (turn off)
for i in range(72):
    dots[i] = (0, 0, 0)
dots.show()
