import RPi.GPIO as GPIO
import time
import os

# --- Pin Setup ---
TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# --- Config ---
TRIGGER_DISTANCE = 40  # cm
STAND_TIME_REQUIRED = 3  # seconds
DISPLAY_ON_DURATION = 600  # 10 minutes in seconds

# --- State Variables ---
start_time = None
display_on = False
on_timer_start = None

def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.05)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = None  # Initialize pulse_start variable
    pulse_end = None    # Initialize pulse_end variable

    timeout = time.time() + 2  # Increase timeout to 2 seconds to handle slow echoes

    # Wait for ECHO to go HIGH
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if time.time() > timeout:
            return None  # Timeout exceeded

    # Wait for ECHO to go LOW
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if time.time() > timeout:
            return None  # Timeout exceeded

    # Calculate distance if both pulse_start and pulse_end are set
    if pulse_start is not None and pulse_end is not None:
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150  # cm
        return round(distance, 2)
    else:
        return None  # Return None if pulses are not valid

def get_average_distance(readings=5):
    distances = []
    for _ in range(readings):
        dist = get_distance()
        if dist is not None:
            distances.append(dist)
        time.sleep(0.1)  # Short delay to avoid quick multiple readings

    if len(distances) > 0:
        return sum(distances) / len(distances)
    else:
        return None  # Return None if no valid readings

try:
    while True:
        distance = get_average_distance()  # Get an average distance from 5 readings
        now = time.time()

        if distance is not None:
            print(f"Distance: {distance} cm")

            if distance <= TRIGGER_DISTANCE:
                if not display_on:
                    if start_time is None:
                        start_time = now
                        print("Person detected. Starting 5s timer...")
                    elif now - start_time >= STAND_TIME_REQUIRED:
                        print("Person stayed 5s. Turning on display for 10 minutes.")
                        os.system("xrandr --output HDMI-1 --mode 2560x1440 --rotate left")  # Turn on display
                        display_on = True
                        on_timer_start = now
                # else: do nothing if already on
            else:
                start_time = None  # person walked away before 5s

        # Check if display has been on for 10 minutes
        if display_on and (now - on_timer_start >= DISPLAY_ON_DURATION):
            print("10 minutes passed. Turning display off.")
            os.system("xrandr --output HDMI-1 --off")  # Turn off display
            display_on = False
            start_time = None

        time.sleep(0.25)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    GPIO.cleanup()
