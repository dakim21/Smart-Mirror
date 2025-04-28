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
DISPLAY_ON_DURATION = 600  # 10 minutes in seconds

# --- State Variables ---
start_time = None
display_on = False
on_timer_start = None
blinking = False

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
        distance = pulse_duration * 17150  # cm
        return round(distance, 2)
    return None

def set_led_brightness(brightness):
    brightness = max(0, min(brightness, 255))
    for i in range(LED_COUNT):
        leds[i] = (brightness, brightness, brightness)
    leds.show()

def blink_leds():
    leds.fill((255, 255, 255))  # White
    leds.show()
    time.sleep(0.3)  # Faster blink
    leds.fill((0, 0, 0))  # Off
    leds.show()
    time.sleep(0.3)

def increase_brightness_and_blink():
    current_brightness = int(LED_BRIGHTNESS * 255)
    increment = 255 // 5

    while current_brightness < 255:
        current_brightness += increment
        set_led_brightness(current_brightness)
        blink_leds()
        time.sleep(1)

# --- Initialize LEDs dimmed ---
set_led_brightness(50)

try:
    while True:
        distance = get_distance()
        now = time.time()

        if distance is not None:
            print(f"Distance: {distance} cm")

            if distance <= TRIGGER_DISTANCE:
                if not blinking:
                    print("Person detected. Starting blinking immediately...")
                    blinking = True

                if not display_on:
                    if start_time is None:
                        start_time = now
                        print("Starting 3s countdown...")
                    elif now - start_time >= STAND_TIME_REQUIRED:
                        print("Person stayed 3s. Turning on display for 10 minutes.")
                        os.system("xrandr --output HDMI-1 --mode 2560x1440 --rotate right")
                        display_on = True
                        on_timer_start = now
                        increase_brightness_and_blink()
                # else: do nothing if already on
            else:
                start_time = None
                blinking = False
                set_led_brightness(50)  # Return to dimmed LEDs

        else:
            start_time = None
            blinking = False
            set_led_brightness(50)  # No reading, stay dimmed

        if blinking and not display_on:
            blink_leds()

        # Check if display has been on for 10 minutes
        if display_on and (now - on_timer_start >= DISPLAY_ON_DURATION):
            print("10 minutes passed. Turning display off.")
            os.system("xrandr --output HDMI-1 --off")
            display_on = False
            start_time = None
            blinking = False
            set_led_brightness(50)

        time.sleep(0.1)  # Faster checking interval

except KeyboardInterrupt:
    print("Exiting...")

finally:
    leds.deinit()
    GPIO.cleanup()