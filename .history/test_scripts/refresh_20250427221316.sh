#!/bin/bash
echo "Freeing port 5000"
fuser -k 5000/tcp > /dev/null 2>&1

echo "Killing all Chromium Processes"
pkill chromium-browser

sleep 1

echo "Clearing cache"
rm -rf ~/.cache/chromium

echo "Killing current Flask"
pkill -f "flask run"

sleep 1

echo "Exporting Flask"
cd /home/pi/smart-mirror
export FLASK_APP=app

echo "Starting Flask"
flask run --host=0.0.0.0 > /home/pi/smart-mirror/flask.log 2>&1 &

sleep 2

echo "Restarting Chromium (no cache)"
DISPLAY=:0 chromium-browser \
  --kiosk \
  --incognito \
  --disk-cache-size=1 \
  --disable-application-cache \
  --disable-cache \
  --disable-offline-load-stale-cache \
  --disable-gpu-program-cache \
  http://localhost:5000/mirror &