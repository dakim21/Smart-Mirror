'''
Motion Sensor Detection and LED Control Script
1. Initializes distance sensor and LED strip; GPIO for motion sensor and SPI for LEDs
2. Constantly monitors distance to detect presence (similar to test distance script)
3. Blinks LEDs white 5 times when motion detected within trigger distance
4. Turns on HDMI display if a person stays for 3 seconds, and breaks if they move away
5. Increases LED brightness gradually when display turns on
6. Turns off HDMI display after 10 minutes of inactivity
7. Listens for manual color override from Flask via color.txt file for /remote LED slider control
8. Restores LED state appropriately based on motion and override
9. Cleans up GPIO and LED resources on exit for no clutter and unwanted LED flashing
'''

import RPi.GPIO as GPIO
import time
import os
import board
import adafruit_dotstar

'''
Motion Sensor Setup (GPIO)
'''
GPIO.setwarnings(False)  # Silence "already in use" warnings
GPIO.setmode(GPIO.BCM)
TRIG = 17
ECHO = 4

'''
LED Setup (SPI)
'''
LED_COUNT = 72
LED_BRIGHTNESS = 0.05
#SCLK for Clock, MOSI for Data
leds = adafruit_dotstar.DotStar(board.SCLK, board.MOSI, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

'''
Config Vars: distance in cm, time in seconds
'''
TRIGGER_DISTANCE = 20
STAND_TIME_REQUIRED = 3
DISPLAY_ON_DURATION = 600

COLOR_FILE = "/home/pi/smart-mirror/color.txt"
last_color = (0, 0, 0)
manual_override = False #VERY IMPORTANT: Need for /remote override

start_time = None
display_on = False
on_timer_start = None
blinking = False
blink_start_time = None
blink_count = 0
blinking_now = False

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

'''
get_distance

1. Measure distance from motion sensor
2. Sends trigger pulse and listens for echo
3. returns distance in cm or none if fail
'''
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
        #converstion factor for cm is 17150
        distance = pulse_duration * 17150
        return round(distance, 2)
    return None

'''
set_all_leds

sets all leds in the strip to a specific color
'''
def set_all_leds(color):
    for i in range(LED_COUNT):
        leds[i] = color
    leds.show()

'''
blink_leds_once

blink all LEDs to white briefly then turn off.
white is 255 255 255
black(off) is 0 0 0
'''
def blink_leds_once():
    set_all_leds((255, 255, 255))
    time.sleep(0.2)
    set_all_leds((0, 0, 0))
    time.sleep(0.8)

'''
increase_brightness

Gradually increase brightness of LEDs to max
Used when display is turning on
'''
def increase_brightness():
    current_brightness = int(LED_BRIGHTNESS * 255)
    increment = 255 // 5

    while current_brightness < 255:
        current_brightness += increment
        if current_brightness > 255:
            current_brightness = 255
        set_all_leds((current_brightness, current_brightness, current_brightness))
        time.sleep(0.5)

#turn off all LEDs on boot/startup
set_all_leds((0, 0, 0))

try:
    while True:
        #check for manual color ovverride from /remote
        try:
            with open(COLOR_FILE, 'r') as f:
                color_hex = f.read().strip()
                if color_hex:
                    color_hex = color_hex.lstrip('#')
                    rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
                    if rgb != last_color:
                        set_all_leds(rgb)
                        last_color = rgb
                        manual_override = True
        #if color.txt is not found, pass
        except FileNotFoundError:
            pass

        '''
        Distance Sensor and Motion Logic
        '''
        distance = get_distance()
        now = time.time()

        if distance is not None and distance <= TRIGGER_DISTANCE:
            #if person is detected within trigger distance, start blinking
            if not blinking and not display_on:
                blinking = True
                blink_start_time = now
                blink_count = 0
                start_time = now

            #blink 5 times, set while loop to true
            if blinking and blink_count < 5:
                if not blinking_now and now - blink_start_time >= blink_count:
                    blink_leds_once()
                    blinking_now = True
                    blink_count += 1
                    print(f"Blink {blink_count}")
                elif blinking_now and now - blink_start_time >= blink_count:
                    blinking_now = False

            #after blinking 5 times, break loop
            if blink_count >= 5:
                blinking = False
                #restore manual color if needed from /remote
                if manual_override:
                    try:
                        with open(COLOR_FILE, 'r') as f:
                            color_hex = f.read().strip()
                            if color_hex:
                                color_hex = color_hex.lstrip('#')
                                rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
                                set_all_leds(rgb)
                                last_color = rgb
                    except FileNotFoundError:
                        set_all_leds((0, 0, 0))
                else:
                    set_all_leds((0, 0, 0))

            #if person stands for 3 seconds, turn display on
            if not display_on and now - start_time >= STAND_TIME_REQUIRED:
                os.system("xrandr --output HDMI-1 --mode 2560x1440 --rotate right")
                display_on = True
                on_timer_start = now
                if not manual_override:
                    increase_brightness()

        else:
            if blinking:
                print("Person left: stopping blinking.")
                blinking = False
                blink_count = 0
                blinking_now = False
                if not manual_override:
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
            if not manual_override:
                set_all_leds((0, 0, 0))

        time.sleep(0.05)

except KeyboardInterrupt:
    print("KeyboardInterrupt: Exiting...")

finally:
    leds.deinit()
    GPIO.cleanup()