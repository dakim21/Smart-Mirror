import RPi.GPIO as GPIO
import time

# Pin Setup
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

    timeout = time.time() + 1  # Timeout of 1 second
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if time.time() > timeout:
            return None

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if time.time() > timeout:
            return None

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Calculate the distance in cm
    return round(distance, 2)

try:
    while True:
        distance = get_distance()
        if distance is not None:
            print(f"Distance: {distance} cm")
        else:
            print("Failed to read distance.")
        time.sleep(0.5)

except KeyboardInterrupt:
    print("Program stopped by user.")

finally:
    GPIO.cleanup()
