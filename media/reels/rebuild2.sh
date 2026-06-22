#!/bin/bash
# Re-render titluri_stat (24s, clock SFX) & regula72 (22s, calculator SFX) with explainer steps.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"

# ---- titluri: ceas (timp care trece) + erodare + rezolvare calda. reveal 18.6s, cta 20.6s, total 24s ----
FC_TIT="
aevalsrc='0.17*sin(2*PI*1900*t)*exp(-55*mod(t,1.2))':d=13.7:s=44100[tk0];[tk0]highpass=f=1000,adelay=3500,volume=0.55[tk];
aevalsrc='0.13*sin(2*PI*650*t)*exp(-45*mod(t+0.6,1.2))':d=13.7:s=44100[to0];[to0]adelay=3500,volume=0.55[to];
aevalsrc='0.05*sin(2*PI*120*t)':d=24:s=44100[hum0];[hum0]afade=t=out:st=16:d=3,volume=1[hum];
aevalsrc='0.32*sin(2*PI*92*t)*exp(-3*t)':d=1.3:s=44100[bo0];[bo0]adelay=18600[bo];
aevalsrc='0.26*(sin(2*PI*660*t)+sin(2*PI*990*t))*exp(-2.4*t)':d=2.2:s=44100[ch0];[ch0]aecho=0.8:0.8:90:0.4,adelay=18650[ch];
aevalsrc='0.22*sin(2*PI*560*t)*exp(-18*t)':d=0.3:s=44100[ck0];[ck0]adelay=20600[ck];
anoisesrc=d=24:c=pink:a=1:s=44100[ai0];[ai0]lowpass=f=480,volume=0.012[ai];
[ai][hum][tk][to][bo][ch][ck]amix=inputs=7:duration=longest:normalize=0,volume=0.82,afade=t=out:st=23.4:d=0.6,aformat=channel_layouts=stereo[a]"

# ---- regula72: calculator (taste + rezultate). reveal 16.6s, cta 18.6s, total 22s ----
FC_REG="
aevalsrc='0.3*sin(2*PI*1200*t)*exp(-26*t)':d=0.25:s=44100[k1];[k1]adelay=3500[kk1];
aevalsrc='0.3*sin(2*PI*1200*t)*exp(-26*t)':d=0.25:s=44100[k2];[k2]adelay=7500[kk2];
aevalsrc='0.3*sin(2*PI*1200*t)*exp(-26*t)':d=0.25:s=44100[k3];[k3]adelay=11000[kk3];
aevalsrc='0.3*sin(2*PI*1200*t)*exp(-26*t)':d=0.25:s=44100[k4];[k4]adelay=14500[kk4];
aevalsrc='0.26*sin(2*PI*880*t)*exp(-7*t)':d=0.6:s=44100[d1];[d1]adelay=8600[dd1];
aevalsrc='0.26*sin(2*PI*660*t)*exp(-7*t)':d=0.6:s=44100[d2];[d2]adelay=12100[dd2];
aevalsrc='0.26*sin(2*PI*1100*t)*exp(-7*t)':d=0.6:s=44100[d3];[d3]adelay=15600[dd3];
aevalsrc='0.3*(sin(2*PI*1047*t)+sin(2*PI*1568*t))*exp(-6*t)':d=0.9:s=44100[fd0];[fd0]aecho=0.8:0.7:45:0.3,adelay=16650[fd];
aevalsrc='0.24*sin(2*PI*620*t)*exp(-18*t)':d=0.3:s=44100[ck0];[ck0]adelay=18600[ck];
anoisesrc=d=22:c=pink:a=1:s=44100[ai0];[ai0]lowpass=f=650,volume=0.011[ai];
[ai][kk1][kk2][kk3][kk4][dd1][dd2][dd3][fd][ck]amix=inputs=10:duration=longest:normalize=0,volume=0.8,afade=t=out:st=21.4:d=0.6,aformat=channel_layouts=stereo[a]"

render_one(){
  local key="$1" fc="$2"
  echo ">>> $key"
  node render_cdp.js "$key" "frames_$key"
  ffmpeg -y -framerate 30 -i "frames_$key/f%04d.png" -c:v libx264 -pix_fmt yuv420p -crf 18 \
    -vf "scale=1080:1920:flags=lanczos" -movflags +faststart "_sil_$key.mp4" >/dev/null 2>&1
  ffmpeg -y -i "_sil_$key.mp4" -filter_complex "$fc" -map 0:v -map "[a]" \
    -c:v copy -c:a aac -b:a 192k -shortest "reel_$key.mp4" >/dev/null 2>&1
  rm -rf "frames_$key" "_sil_$key.mp4"
  echo "    -> reel_$key.mp4 ($(du -h reel_$key.mp4 | cut -f1), $(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 reel_$key.mp4)s)"
}

render_one titluri_stat "$FC_TIT"
render_one regula72 "$FC_REG"
echo DONE
