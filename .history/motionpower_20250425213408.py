import RPi.GPIO as GPIO
import time
import os
import board
import adafruit_dotstar

# --- GPIO Setup ---
GPIO.setmode(GPIO.BCM)  # Set GPIO to BCM pin numbering (must be done at the start)

# --- Pin Setup ---
TRIG = 17  # GPIO 17 (Pin 11) for Trigger
ECHO = 4   # GPIO 4 (Pin 7) for Echo

# --- LED Setup ---
LED_PIN_DATA = board.D23   # GPIO 23 for data (Pin 16)
LED_PIN_CLOCK = board.D24  # GPIO 24 for clock (Pin 18)
LED_COUNT = 72             # Number of LEDs in the strip
LED_BRIGHTNESS = 0.05      # Initial dimmed brightness (5%)
leds = adafruit_dotstar.DotStar(LED_PIN_DATA, LED_PIN_CLOCK, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

# --- Config ---
TRIGGER_DISTANCE = 20  # cm
STAND_TIME_REQUIRED = 3  # seconds
DISPLAY_ON_DURATION = 600  # 10 minutes in seconds

# --- State Variables ---
start_time = None
display_on = False
on_timer_start = None

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
    """
    Set the brightness of the LED strip (0 to 255).
    """
    brightness = max(0, min(brightness, 255))  # Ensure brightness is within the range 0-255
    for i in range(LED_COUNT):
        leds[i] = (brightness, brightness, brightness)  # White color (R=G=B)
    leds.show()

def blink_leds():
    """
    Blink the LEDs white every second (on for 1 second, off for 0.1 seconds).
    """
    leds.fill((255, 255, 255))  # White
    leds.show()
    time.sleep(1)

    leds.fill((0, 0, 0))  # Off
    leds.show()
    time.sleep(0.1)

def increase_brightness_and_blink():
    """
    Gradually increase the LED brightness and blink white LEDs.
    """
    current_brightness = int(LED_BRIGHTNESS * 255)  # Scale initial brightness to 255
    increment = 255 // 5  # Each increment is 1/5 of the max brightness (51 per second)

    while current_brightness < 255:
        current_brightness += increment
        set_led_brightness(current_brightness)
        blink_leds()  # Blink white LEDs
        time.sleep(1)  # Wait 1 second before increasing brightness again

# Initialize the LEDs to a dimmed white state on startup
set_led_brightness(50)  # Dimmed state (5% brightness)

try:
    while True:
        distance = get_distance()
        now = time.time()

        if distance is not None:
            print(f"Distance: {distance} cm")

            if distance <= TRIGGER_DISTANCE:
                if not display_on:
                    if start_time is None:
                        start_time = now
                        print("Person detected. Starting 3s timer...")
                    elif now - start_time >= STAND_TIME_REQUIRED:
                        print("Person stayed 3s. Turning on display for 10 minutes.")
                        os.system("xrandr --output HDMI-1 --mode 2560x1440 --rotate left")  # Turn on display
                        display_on = True
                        on_timer_start = now
                        increase_brightness_and_blink()  # Gradually increase the LED brightness and blink white LEDs
                # else: do nothing if already on
            else:
                start_time = None  # person walked away before 3s

        # Check if display has been on for 10 minutes
        if display_on and (now - on_timer_start >= DISPLAY_ON_DURATION):
            print("10 minutes passed. Turning display off.")
            os.system("xrandr --output HDMI-1 --off")  # Turn off display
            display_on = False
            start_time = None
            # Dim the LEDs back down after 10 minutes
            set_led_brightness(50)  # Dimmed state

        time.sleep(0.25)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    # Cleanup LEDs first
    leds.deinit()   # Reset the LED strip when the script ends
    # Then cleanup GPIO
    GPIO.cleanup()  # Ensure proper GPIO cleanup
