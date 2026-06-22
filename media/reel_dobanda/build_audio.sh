#!/bin/bash
# Build tasteful SFX bed synced to the reel timeline and mux into the video.
set -e
cd "$(dirname "$0")"

FC="
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

ffmpeg -y -i _video_silent.mp4 -filter_complex "$FC" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest \
  reel_dobanda.mp4 >/dev/null 2>&1

echo "muxed -> reel_dobanda.mp4"
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name -of default=noprint_wrappers=1 reel_dobanda.mp4 2>/dev/null
