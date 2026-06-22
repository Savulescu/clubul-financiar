#!/bin/bash
# Render ALL 9 reels (engine reel.html) with distinct sound family each. Run between engine edits.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"
fc(){
case "$1" in
dobanda_compusa) echo "
aevalsrc='0.18*sin(2*PI*(260+22*t)*t)*exp(-9*mod(t,1.5))':d=12.5:s=44100[pk0];[pk0]adelay=3500,volume=0.6[pk];
aevalsrc='0.42*sin(2*PI*120*t)*exp(-3*t)':d=1.5:s=44100[bo0];[bo0]adelay=16600[bo];
aevalsrc='0.22*(sin(2*PI*880*t)+sin(2*PI*1320*t))*exp(-4*t)':d=1.2:s=44100[sh0];[sh0]aecho=0.8:0.7:60:0.3,adelay=16650[sh];
aevalsrc='0.24*sin(2*PI*620*t)*exp(-18*t)':d=0.3:s=44100[ck0];[ck0]adelay=18600[ck];
anoisesrc=d=22:c=pink:a=1:s=44100[ai0];[ai0]lowpass=f=600,volume=0.012[ai];
aevalsrc='0.05*(sin(2*PI*146.83*t)+sin(2*PI*220*t))':d=22:s=44100[pad0];[pad0]lowpass=f=500,afade=t=in:st=3:d=3,afade=t=out:st=17:d=3[pad];
[ai][pad][pk][bo][sh][ck]amix=inputs=6:duration=longest:normalize=0,volume=0.8,afade=t=out:st=21.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
card_minim) echo "
aevalsrc='0.42*sin(2*PI*55*t)*exp(-26*mod(t,0.95))':d=11:s=44100[h1];[h1]lowpass=f=180,adelay=3500[hb1];
aevalsrc='0.30*sin(2*PI*48*t)*exp(-26*mod(t+0.2,0.95))':d=11:s=44100[h2];[h2]lowpass=f=180,adelay=3500[hb2];
aevalsrc='0.04*sin(2*PI*73*t)':d=20:s=44100[dr];
aevalsrc='0.6*sin(2*PI*47*t)*exp(-2.6*t)':d=1.6:s=44100[bo0];[bo0]adelay=14600[bo];
anoisesrc=d=0.5:c=brown:a=0.5:s=44100[th0];[th0]lowpass=f=300,afade=t=out:st=0:d=0.5,adelay=14600,volume=0.4[th];
aevalsrc='0.2*sin(2*PI*150*t)*exp(-12*t)':d=0.4:s=44100[ck0];[ck0]adelay=16600[ck];
[dr][hb1][hb2][bo][th][ck]amix=inputs=6:duration=longest:normalize=0,volume=0.82,afade=t=out:st=19.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
pilon3) echo "
aevalsrc='0.16*sin(2*PI*2400*t)*exp(-42*mod(t,1.0))':d=10:s=44100[co0];[co0]adelay=3500,volume=0.5[co];
aevalsrc='0.45*sin(2*PI*90*t)*exp(-3*t)':d=1.2:s=44100[bo0];[bo0]adelay=14600[bo];
aevalsrc='0.24*sin(2*PI*1318*t)*exp(-7*t)':d=0.5:s=44100[c1];[c1]adelay=14650[cc1];
aevalsrc='0.26*sin(2*PI*1760*t)*exp(-7*t)':d=0.7:s=44100[c2];[c2]aecho=0.8:0.7:50:0.3,adelay=14850[cc2];
aevalsrc='0.22*sin(2*PI*700*t)*exp(-16*t)':d=0.3:s=44100[ck0];[ck0]adelay=16600[ck];
anoisesrc=d=20:c=pink:a=1:s=44100[ai0];[ai0]lowpass=f=650,volume=0.012[ai];
aevalsrc='0.05*(sin(2*PI*174.61*t)+sin(2*PI*261.63*t))':d=20:s=44100[pad0];[pad0]lowpass=f=520,afade=t=in:st=3:d=3,afade=t=out:st=15:d=3[pad];
[ai][pad][co][bo][cc1][cc2][ck]amix=inputs=7:duration=longest:normalize=0,volume=0.8,afade=t=out:st=19.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
fire) echo "
aevalsrc='0.06*sin(2*PI*110*t)':d=22:s=44100[pad0];[pad0]afade=t=in:st=2:d=10[pad];
aevalsrc='0.16*sin(2*PI*(240*t+50*t*t))':d=13.5:s=44100[ris0];[ris0]lowpass=f=2800,afade=t=in:st=0:d=1,afade=t=out:st=12.8:d=0.6,adelay=3500[ris];
aevalsrc='0.7*sin(2*PI*52*t)*exp(-2.6*t)':d=1.8:s=44100[bo0];[bo0]adelay=16600[bo];
aevalsrc='0.16*(sin(2*PI*523*t)+sin(2*PI*659*t)+sin(2*PI*784*t))*exp(-2*t)':d=2.6:s=44100[chd0];[chd0]aecho=0.8:0.8:80:0.4,adelay=16650[chd];
aevalsrc='0.24*sin(2*PI*784*t)*exp(-16*t)':d=0.3:s=44100[ck0];[ck0]adelay=18600[ck];
[pad][ris][bo][chd][ck]amix=inputs=5:duration=longest:normalize=0,volume=0.72,afade=t=out:st=21.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
datorie_buna_rea) echo "
aevalsrc='0.12*sin(2*PI*(150*t+12*t*t))':d=5:s=44100[lo0];[lo0]lowpass=f=800,afade=t=out:st=4.5:d=0.5,adelay=3500[lo];
aevalsrc='0.13*sin(2*PI*(520*t+40*t*t))':d=4.5:s=44100[hi0];[hi0]afade=t=in:st=0:d=0.6,adelay=9500[hi];
aevalsrc='0.4*sin(2*PI*52*t)*exp(-3*t)':d=1.2:s=44100[bad0];[bad0]adelay=14600[bad];
aevalsrc='0.22*(sin(2*PI*988*t)+sin(2*PI*1319*t))*exp(-5*t)':d=0.9:s=44100[dg0];[dg0]aecho=0.8:0.7:50:0.3,adelay=14650[dg];
aevalsrc='0.24*sin(2*PI*660*t)*exp(-16*t)':d=0.3:s=44100[ck0];[ck0]adelay=16600[ck];
anoisesrc=d=20:c=pink:a=1:s=44100[ai0];[ai0]lowpass=f=550,volume=0.012[ai];
[ai][lo][hi][bad][dg][ck]amix=inputs=6:duration=longest:normalize=0,volume=0.78,afade=t=out:st=19.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
masina_rate) echo "
anoisesrc=d=20:c=brown:a=1:s=44100[rmb0];[rmb0]lowpass=f=110,volume=0.08[rmb];
aevalsrc='0.18*sin(2*PI*1400*t)*exp(-55*mod(t,0.9))':d=11:s=44100[bk0];[bk0]highpass=f=800,adelay=3500,volume=0.4[bk];
aevalsrc='0.6*sin(2*PI*58*t)*exp(-3.2*t)':d=1.4:s=44100[bo0];[bo0]adelay=14600[bo];
aevalsrc='0.25*sin(2*PI*(820*t-200*t*t))*exp(-3.5*t)':d=0.9:s=44100[fa0];[fa0]adelay=14700[fa];
aevalsrc='0.22*sin(2*PI*500*t)*exp(-18*t)':d=0.3:s=44100[ck0];[ck0]adelay=16600[ck];
[rmb][bk][bo][fa][ck]amix=inputs=5:duration=longest:normalize=0,volume=0.78,afade=t=out:st=19.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
scor_credit) echo "
aevalsrc='0.06*(sin(2*PI*130.81*t)+sin(2*PI*196*t))':d=21:s=44100[pad0];[pad0]lowpass=f=420,afade=t=in:st=0.5:d=2,afade=t=out:st=18:d=2.5[pad];
aevalsrc='0.16*sin(2*PI*392*t)*exp(-9*t)':d=0.5:s=44100[t1];[t1]lowpass=f=1100,adelay=4000[tt1];
aevalsrc='0.16*sin(2*PI*440*t)*exp(-9*t)':d=0.5:s=44100[t2];[t2]lowpass=f=1100,adelay=7000[tt2];
aevalsrc='0.16*sin(2*PI*494*t)*exp(-9*t)':d=0.5:s=44100[t3];[t3]lowpass=f=1100,adelay=10500[tt3];
aevalsrc='0.16*sin(2*PI*587*t)*exp(-9*t)':d=0.5:s=44100[t4];[t4]lowpass=f=1100,adelay=13500[tt4];
aevalsrc='0.2*(sin(2*PI*523.25*t)+sin(2*PI*659.25*t))*exp(-3.2*t)':d=1.6:s=44100[lk0];[lk0]lowpass=f=1500,aecho=0.8:0.7:70:0.35,adelay=15600[lk];
aevalsrc='0.3*sin(2*PI*70*t)*exp(-3.4*t)':d=1.3:s=44100[bo0];[bo0]adelay=15600[bo];
aevalsrc='0.16*sin(2*PI*440*t)*exp(-16*t)':d=0.3:s=44100[ck0];[ck0]lowpass=f=1100,adelay=17600[ck];
anoisesrc=d=21:c=pink:a=1:s=44100[ai0];[ai0]lowpass=f=440,volume=0.01[ai];
[ai][pad][tt1][tt2][tt3][tt4][lk][bo][ck]amix=inputs=9:duration=longest:normalize=0,volume=0.85,afade=t=out:st=20.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
titluri_stat) echo "
aevalsrc='0.17*sin(2*PI*1900*t)*exp(-55*mod(t,1.2))':d=13.7:s=44100[tk0];[tk0]highpass=f=1000,adelay=3500,volume=0.55[tk];
aevalsrc='0.13*sin(2*PI*650*t)*exp(-45*mod(t+0.6,1.2))':d=13.7:s=44100[to0];[to0]adelay=3500,volume=0.55[to];
aevalsrc='0.05*sin(2*PI*120*t)':d=24:s=44100[hum0];[hum0]afade=t=out:st=16:d=3,volume=1[hum];
aevalsrc='0.32*sin(2*PI*92*t)*exp(-3*t)':d=1.3:s=44100[bo0];[bo0]adelay=18600[bo];
aevalsrc='0.26*(sin(2*PI*660*t)+sin(2*PI*990*t))*exp(-2.4*t)':d=2.2:s=44100[ch0];[ch0]aecho=0.8:0.8:90:0.4,adelay=18650[ch];
aevalsrc='0.22*sin(2*PI*560*t)*exp(-18*t)':d=0.3:s=44100[ck0];[ck0]adelay=20600[ck];
anoisesrc=d=24:c=pink:a=1:s=44100[ai0];[ai0]lowpass=f=480,volume=0.012[ai];
[ai][hum][tk][to][bo][ch][ck]amix=inputs=7:duration=longest:normalize=0,volume=0.82,afade=t=out:st=23.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
regula72) echo "
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
[ai][kk1][kk2][kk3][kk4][dd1][dd2][dd3][fd][ck]amix=inputs=10:duration=longest:normalize=0,volume=0.8,afade=t=out:st=21.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
esac
}
for K in ${@:-dobanda_compusa titluri_stat card_minim regula72 pilon3 fire datorie_buna_rea masina_rate scor_credit}; do
  echo ">>> $K"
  node render_cdp.js "$K" "frames_$K"
  ffmpeg -y -framerate 30 -i "frames_$K/f%04d.png" -c:v libx264 -pix_fmt yuv420p -crf 18 -vf "scale=1080:1920:flags=lanczos" -movflags +faststart "_sil_$K.mp4" >/dev/null 2>&1
  ffmpeg -y -i "_sil_$K.mp4" -filter_complex "$(fc "$K")" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest "reel_$K.mp4" >/dev/null 2>&1
  rm -rf "frames_$K" "_sil_$K.mp4"
  echo "    -> reel_$K.mp4 ($(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 reel_$K.mp4)s)"
done
echo ALL9_DONE
