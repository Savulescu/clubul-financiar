#!/bin/bash
# Render a single frame: $1 = frame index
i="$1"
FPS=30
t=$(( i*1000/FPS ))
idx=$(printf "%04d" "$i")
DIR="$(cd "$(dirname "$0")" && pwd)"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless=new --use-angle=swiftshader --disable-gpu --hide-scrollbars \
  --window-size=1080,1920 --force-device-scale-factor=1 \
  --user-data-dir="/tmp/cf_chrome_$i" \
  --screenshot="$DIR/frames/f$idx.png" "file://$DIR/scene.html?t=$t" >/dev/null 2>&1
rm -rf "/tmp/cf_chrome_$i"
