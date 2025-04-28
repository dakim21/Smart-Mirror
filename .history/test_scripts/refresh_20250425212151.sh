#!/bin/bash

echo "Freeing up port 5000..."
fuser -k 5000/tcp > /dev/null 2>&1

echo "Killing Chromium..."
pkill chromium-browser

sleep 1

echo "Clearing Chromium cache..."
rm -rf ~/.cache/chromium

echo "Stopping Flask (if running)..."
pkill -f "flask run"

sleep 1

echo "Exporting Flask app..."
cd /home/pi/smart-mirror
export FLASK_APP=app

echo "Starting Flask app..."
flask run --host=0.0.0.0 > /home/pi/smart-mirror/flask.log 2>&1 &

sleep 2

echo "Restarting Chromium with cache disabled..."
DISPLAY=:0 chromium-browser \
  --kiosk \
  --incognito \
  --disk-cache-size=1 \
  --disable-application-cache \
  --disable-cache \
  --disable-offline-load-stale-cache \
  --disable-gpu-program-cache \
  http://localhost:5000/mirror &