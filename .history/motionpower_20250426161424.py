import RPi.GPIO as GPIO
import time
import os
import board
import adafruit_dotstar

# --- GPIO Setup ---
GPIO.setmode(GPIO.BCM)

# --- Pin Setup ---
TRIG = 17
ECHO = 4

# --- LED Setup ---
LED_PIN_DATA = board.D23
LED_PIN_CLOCK = board.D24
LED_COUNT = 72
LED_BRIGHTNESS = 0.05
leds = adafruit_dotstar.DotStar(LED_PIN_DATA, LED_PIN_CLOCK, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

# --- Config ---
TRIGGER_DISTANCE = 20  # cm
STAND_TIME_REQUIRED = 3  # seconds
DISPLAY_ON_DURATION = 600  # 10 minutes

# --- State Variables ---
start_time = None
display_on = False
on_timer_start = None
blinking = False
blink_start_time = None
blink_count = 0
blinking_now = False

# --- GPIO Setup ---
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.05)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = None
    pulse_end = None

    timeout = time.time() + 2

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if time.time() > timeout:
            return None

    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if time.time() > timeout:
            return None

    if pulse_start is not None and pulse_end is not None:
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        return round(distance, 2)
    return None

def set_all_leds(color):
    for i in range(LED_COUNT):
        leds[i] = color
    leds.show()

def blink_leds_once():
    set_all_leds((255, 255, 255))  # Full white
    time.sleep(0.2)
    set_all_leds((0, 0, 0))        # Full off
    time.sleep(0.8)

def increase_brightness():
    current_brightness = int(LED_BRIGHTNESS * 255)
    increment = 255 // 5

    while current_brightness < 255:
        current_brightness += increment
        set_all_leds((current_brightness, current_brightness, current_brightness))
        time.sleep(0.5)

# --- Initialize LEDs all off ---
set_all_leds((0, 0, 0))

try:
    while True:
        distance = get_distance()
        now = time.time()

        if distance is not None and distance <= TRIGGER_DISTANCE:
            if not blinking and not display_on:
                print("Person detected: starting blinking.")
                blinking = True
                blink_start_time = now
                blink_count = 0
                start_time = now

            if blinking and blink_count < 5:
                if not blinking_now and now - blink_start_time >= blink_count:
                    blink_leds_once()
                    blinking_now = True
                    blink_count += 1
                    print(f"Blink {blink_count}")
                elif blinking_now and now - blink_start_time >= blink_count:
                    blinking_now = False

            if blink_count >= 5:
                blinking = False
                set_all_leds((0, 0, 0))

            if not display_on and now - start_time >= STAND_TIME_REQUIRED:
                print("Person stayed 3s: turning display ON.")
                os.system("xrandr --output HDMI-1 --mode 2560x1440 --rotate right")
                display_on = True
                on_timer_start = now
                increase_brightness()

        else:
            if blinking:
                print("Person left: stopping blinking.")
                blinking = False
                blink_count = 0
                blinking_now = False
                set_all_leds((0, 0, 0))
            start_time = None

        if display_on and now - on_timer_start >= DISPLAY_ON_DURATION:
            print("10 minutes passed: turning display OFF.")
            os.system("xrandr --output HDMI-1 --off")
            display_on = False
            start_time = None
            blinking = False
            blink_count = 0
            blinking_now = False
            set_all_leds((0, 0, 0))

        time.sleep(0.05)

except KeyboardInterrupt:
    print("KeyboardInterrupt: Exiting...")

finally:
    leds.deinit()
    GPIO.cleanup()