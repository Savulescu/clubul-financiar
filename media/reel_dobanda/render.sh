#!/bin/bash
# Render scene.html -> reel_dobanda.mp4 (1080x1920, 30fps, 15s) deterministic via ?t= param
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
FPS=30
DUR=15000
N=$(( DUR*FPS/1000 ))
rm -rf frames && mkdir -p frames

echo "Rendering $N frames @ ${FPS}fps ..."
seq 0 $((N-1)) | xargs -P 6 -n 1 "$DIR/renderframe.sh"

CNT=$(ls frames/*.png 2>/dev/null | wc -l | tr -d ' ')
echo "Captured $CNT/$N frames. Encoding MP4 ..."

ffmpeg -y -framerate $FPS -i frames/f%04d.png \
  -c:v libx264 -pix_fmt yuv420p -crf 18 \
  -vf "scale=1080:1920:flags=lanczos" -movflags +faststart \
  reel_dobanda.mp4 >/dev/null 2>&1

echo "DONE -> $DIR/reel_dobanda.mp4"
ls -la reel_dobanda.mp4
rm -rf frames
