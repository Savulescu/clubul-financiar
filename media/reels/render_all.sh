#!/bin/bash
# Render one or more reels: bash render_all.sh [key1 key2 ...]  (default: all 5)
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
KEYS=("$@")
[ ${#KEYS[@]} -eq 0 ] && KEYS=(fond_urgenta buget_503020 inflatie credit_dae diversificare)

AUDIO_FC="
aevalsrc='0.16*sin(2*PI*(300*t+60*t*t))':d=6.9:s=44100[ris0];
[ris0]lowpass=f=2200,afade=t=in:st=0:d=0.6,afade=t=out:st=6.3:d=0.6,adelay=2300[ris];
aevalsrc='0.55*sin(2*PI*66*t)*exp(-3.2*t)':d=1.3:s=44100[boom0];
[boom0]adelay=9200[boom];
anoisesrc=d=0.4:c=pink:a=0.5:s=44100[thud0];
[thud0]lowpass=f=380,afade=t=out:st=0:d=0.4,adelay=9200,volume=0.4[thud];
aevalsrc='0.2*(sin(2*PI*880*t)+sin(2*PI*1320*t))*exp(-5*t)':d=0.9:s=44100[shim0];
[shim0]aecho=0.8:0.7:55:0.3,adelay=9340[shim];
aevalsrc='0.28*sin(2*PI*620*t)*exp(-22*t)':d=0.3:s=44100[clk0];
[clk0]adelay=11600[clk];
anoisesrc=d=15:c=pink:a=1:s=44100[air0];
[air0]lowpass=f=600,volume=0.014[air];
[air][ris][boom][thud][shim][clk]amix=inputs=6:duration=longest:normalize=0,volume=0.78,afade=t=out:st=14.4:d=0.6,aformat=channel_layouts=stereo[a]
"

for K in "${KEYS[@]}"; do
  echo ">>> $K"
  node render_cdp.js "$K" "frames_$K"
  ffmpeg -y -framerate 30 -i "frames_$K/f%04d.png" -c:v libx264 -pix_fmt yuv420p -crf 18 \
    -vf "scale=1080:1920:flags=lanczos" -movflags +faststart "_sil_$K.mp4" >/dev/null 2>&1
  ffmpeg -y -i "_sil_$K.mp4" -filter_complex "$AUDIO_FC" -map 0:v -map "[a]" \
    -c:v copy -c:a aac -b:a 192k -shortest "reel_$K.mp4" >/dev/null 2>&1
  rm -rf "frames_$K" "_sil_$K.mp4"
  echo "    -> reel_$K.mp4 ($(du -h reel_$K.mp4 | cut -f1))"
done
echo "ALL DONE"
