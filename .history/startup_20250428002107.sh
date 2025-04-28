#!/bin/bash

#wait for the desktop environment to load
sleep 5

#export display for xrandr
export DISPLAY=:0

#first immediate LED clear
python3 /home/pi/smart-mirror/test_scripts/clear_leds.py &

#turn off the display initially using xrandr
xrandr --output HDMI-1 --off

#hide cursor using unclutter
unclutter &

#navigate to Flask app directory and run the server
cd /home/pi/smart-mirror
python3 app.py &

#wait for Flask to start
sleep 5

#kill and restart Chromium with cache-clearing options
pkill chromium-browser

sleep 1

rm -rf ~/.cache/chromium

chromium-browser \
  --kiosk \
  --incognito \
  --disk-cache-size=1 \
  --disable-application-cache \
  --disable-offline-load-stale-cache \
  --disable-gpu-program-cache \
  http://localhost:5000/mirror &

#start motionpower.py script
python3 /home/pi/smart-mirror/motionpower.py &

#clear LEDS again just in case
sleep 2
python3 /home/pi/smart-mirror/test_scripts/clear_leds.py &