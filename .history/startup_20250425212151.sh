#!/bin/bash

# Wait for the desktop environment to load
sleep 5

# Set display environment
export DISPLAY=:0

# Turn off the display initially using xrandr
xrandr --output HDMI-1 --off

# Navigate to Flask app directory and run the server
cd /home/pi/smart-mirror
python3 app.py &

# Wait for Flask to start
sleep 5

# Kill and restart Chromium with cache-clearing options
echo "Killing Chromium..."
pkill chromium-browser

sleep 1

echo "Clearing Chromium cache..."
rm -rf ~/.cache/chromium

echo "Restarting Chromium with cache disabled..."
chromium-browser \
  --kiosk \
  --incognito \
  --disk-cache-size=1 \
  --disable-application-cache \
  --disable-cache \
  --disable-offline-load-stale-cache \
  --disable-gpu-program-cache \
  http://localhost:5000/mirror &

# Run motionpower.py to control display based on sensor input
# python3 /home/pi/smart-mirror/motionpower.py &
