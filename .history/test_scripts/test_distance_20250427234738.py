'''
***OUTDATED - USING SPI PINS
Script to test distance readings

1. sends one trigger pulse
2. waits for one echo
3. measures one round-trip time
4. converts that single time into a distance value
5. prints it
'''

import RPi.GPIO as GPIO
import time

#pin Setup
TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.05)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = time.time()
    pulse_end = time.time()

    timeout = time.time() + 1
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if time.time() > timeout:
            return None

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if time.time() > timeout:
            return None

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

try:
    while True:
        distance = get_distance()
        if distance is not None:
            print(f"Distance: {distance} cm")
        else:
            print("Distance failed to read")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    GPIO.cleanup()
