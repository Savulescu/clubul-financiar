#!/bin/bash
# Distinct SFX per reel, synced to the 15s timeline (riser 2.3-9.2s, impact 9.2s, CTA 11.6s).
# Re-muxes new audio onto the SOURCE mp4 (drops old audio).
set -e
cd ~/clubul-financiar

fc_for(){
case "$1" in
dobanda) echo "
aevalsrc='0.16*sin(2*PI*(300*t+60*t*t))':d=6.9:s=44100[ris0];[ris0]lowpass=f=2200,afade=t=in:st=0:d=0.6,afade=t=out:st=6.3:d=0.6,adelay=2300[ris];
aevalsrc='0.55*sin(2*PI*66*t)*exp(-3.2*t)':d=1.3:s=44100[bo0];[bo0]adelay=9200[bo];
anoisesrc=d=0.4:c=pink:a=0.5:s=44100[th0];[th0]lowpass=f=380,afade=t=out:st=0:d=0.4,adelay=9200,volume=0.4[th];
aevalsrc='0.2*(sin(2*PI*880*t)+sin(2*PI*1320*t))*exp(-5*t)':d=0.9:s=44100[sh0];[sh0]aecho=0.8:0.7:55:0.3,adelay=9340[sh];
aevalsrc='0.28*sin(2*PI*620*t)*exp(-22*t)':d=0.3:s=44100[ck0];[ck0]adelay=11600[ck];
anoisesrc=d=15:c=pink:a=1:s=44100[ai0];[ai0]lowpass=f=600,volume=0.014[ai];
[ai][ris][bo][th][sh][ck]amix=inputs=6:duration=longest:normalize=0,volume=0.78,afade=t=out:st=14.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
titluri_stat) echo "
aevalsrc='0.14*sin(2*PI*(220*t+30*t*t))':d=6.9:s=44100[ris0];[ris0]lowpass=f=1500,afade=t=in:st=0:d=1.0,afade=t=out:st=6.2:d=0.7,adelay=2300[ris];
aevalsrc='0.4*sin(2*PI*80*t)*exp(-3.0*t)':d=1.3:s=44100[bo0];[bo0]adelay=9200[bo];
aevalsrc='0.22*sin(2*PI*660*t)*exp(-3*t)':d=1.3:s=44100[ch0];[ch0]aecho=0.8:0.8:90:0.4,adelay=9300[ch];
aevalsrc='0.2*sin(2*PI*520*t)*exp(-18*t)':d=0.3:s=44100[ck0];[ck0]adelay=11600[ck];
anoisesrc=d=15:c=pink:a=1:s=44100[ai0];[ai0]lowpass=f=450,volume=0.016[ai];
[ai][ris][bo][ch][ck]amix=inputs=5:duration=longest:normalize=0,volume=0.8,afade=t=out:st=14.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
card_minim) echo "
aevalsrc='0.03*sin(2*PI*70*t)':d=15:s=44100[dr];
aevalsrc='0.10*sin(2*PI*(200*t+25*t*t))+0.10*sin(2*PI*(206*t+25*t*t))':d=6.9:s=44100[ris0];[ris0]lowpass=f=1200,afade=t=in:st=0:d=0.8,afade=t=out:st=6.3:d=0.6,adelay=2300[ris];
aevalsrc='0.7*sin(2*PI*48*t)*exp(-2.6*t)':d=1.6:s=44100[bo0];[bo0]adelay=9200[bo];
anoisesrc=d=0.5:c=brown:a=0.6:s=44100[th0];[th0]lowpass=f=300,afade=t=out:st=0:d=0.5,adelay=9200,volume=0.5[th];
aevalsrc='0.22*sin(2*PI*180*t)*exp(-10*t)':d=0.4:s=44100[ck0];[ck0]adelay=11600[ck];
[dr][ris][bo][th][ck]amix=inputs=5:duration=longest:normalize=0,volume=0.8,afade=t=out:st=14.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
regula72) echo "
aevalsrc='0.3*sin(2*PI*440*t)*exp(-6*t)':d=0.5:s=44100[b1];[b1]adelay=3000[bb1];
aevalsrc='0.3*sin(2*PI*660*t)*exp(-6*t)':d=0.5:s=44100[b2];[b2]adelay=4800[bb2];
aevalsrc='0.3*sin(2*PI*880*t)*exp(-6*t)':d=0.5:s=44100[b3];[b3]adelay=6600[bb3];
aevalsrc='0.32*sin(2*PI*1100*t)*exp(-6*t)':d=0.5:s=44100[b4];[b4]adelay=8400[bb4];
aevalsrc='0.5*sin(2*PI*90*t)*exp(-3.2*t)':d=1.2:s=44100[bo0];[bo0]adelay=9200[bo];
aevalsrc='0.22*(sin(2*PI*1320*t)+sin(2*PI*1760*t))*exp(-6*t)':d=0.7:s=44100[sh0];[sh0]aecho=0.8:0.7:50:0.3,adelay=9300[sh];
aevalsrc='0.26*sin(2*PI*880*t)*exp(-20*t)':d=0.3:s=44100[ck0];[ck0]adelay=11600[ck];
anoisesrc=d=15:c=pink:a=1:s=44100[ai0];[ai0]lowpass=f=700,volume=0.012[ai];
[ai][bb1][bb2][bb3][bb4][bo][sh][ck]amix=inputs=8:duration=longest:normalize=0,volume=0.74,afade=t=out:st=14.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
pilon3) echo "
aevalsrc='0.15*sin(2*PI*(400*t+70*t*t))':d=6.9:s=44100[ris0];[ris0]lowpass=f=2600,afade=t=in:st=0:d=0.6,afade=t=out:st=6.3:d=0.5,adelay=2300[ris];
aevalsrc='0.5*sin(2*PI*82*t)*exp(-3.2*t)':d=1.2:s=44100[bo0];[bo0]adelay=9200[bo];
aevalsrc='0.2*sin(2*PI*1318*t)*exp(-9*t)':d=0.4:s=44100[c1];[c1]adelay=9250[cc1];
aevalsrc='0.2*sin(2*PI*1568*t)*exp(-9*t)':d=0.4:s=44100[c2];[c2]adelay=9400[cc2];
aevalsrc='0.22*sin(2*PI*2093*t)*exp(-9*t)':d=0.5:s=44100[c3];[c3]aecho=0.8:0.7:40:0.3,adelay=9550[cc3];
aevalsrc='0.26*sin(2*PI*700*t)*exp(-18*t)':d=0.3:s=44100[ck0];[ck0]adelay=11600[ck];
anoisesrc=d=15:c=pink:a=1:s=44100[ai0];[ai0]lowpass=f=650,volume=0.013[ai];
[ai][ris][bo][cc1][cc2][cc3][ck]amix=inputs=7:duration=longest:normalize=0,volume=0.76,afade=t=out:st=14.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
fire) echo "
aevalsrc='0.05*sin(2*PI*110*t)':d=15:s=44100[pad0];[pad0]afade=t=in:st=2:d=6[pad];
aevalsrc='0.18*sin(2*PI*(250*t+90*t*t))':d=6.9:s=44100[ris0];[ris0]lowpass=f=2800,afade=t=in:st=0:d=0.6,afade=t=out:st=6.4:d=0.5,adelay=2300[ris];
aevalsrc='0.7*sin(2*PI*55*t)*exp(-2.8*t)':d=1.6:s=44100[bo0];[bo0]adelay=9200[bo];
aevalsrc='0.16*(sin(2*PI*523*t)+sin(2*PI*659*t)+sin(2*PI*784*t))*exp(-2.2*t)':d=2.2:s=44100[chd0];[chd0]aecho=0.8:0.8:80:0.4,adelay=9250[chd];
aevalsrc='0.26*sin(2*PI*784*t)*exp(-16*t)':d=0.3:s=44100[ck0];[ck0]adelay=11600[ck];
[pad][ris][bo][chd][ck]amix=inputs=5:duration=longest:normalize=0,volume=0.72,afade=t=out:st=14.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
datorie_buna_rea) echo "
aevalsrc='0.12*sin(2*PI*(160*t+15*t*t))':d=3.5:s=44100[lo0];[lo0]lowpass=f=900,afade=t=out:st=3:d=0.5,adelay=2300[lo];
aevalsrc='0.13*sin(2*PI*(500*t+50*t*t))':d=3.4:s=44100[hi0];[hi0]afade=t=in:st=0:d=0.6,adelay=5800[hi];
aevalsrc='0.45*sin(2*PI*52*t)*exp(-3*t)':d=1.3:s=44100[bl0];[bl0]adelay=9200[bl];
aevalsrc='0.22*(sin(2*PI*988*t)+sin(2*PI*1319*t))*exp(-6*t)':d=0.7:s=44100[dg0];[dg0]aecho=0.8:0.7:50:0.3,adelay=9320[dg];
aevalsrc='0.26*sin(2*PI*660*t)*exp(-18*t)':d=0.3:s=44100[ck0];[ck0]adelay=11600[ck];
anoisesrc=d=15:c=pink:a=1:s=44100[ai0];[ai0]lowpass=f=550,volume=0.013[ai];
[ai][lo][hi][bl][dg][ck]amix=inputs=6:duration=longest:normalize=0,volume=0.77,afade=t=out:st=14.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
masina_rate) echo "
anoisesrc=d=15:c=brown:a=1:s=44100[rmb0];[rmb0]lowpass=f=120,volume=0.07[rmb];
aevalsrc='0.13*sin(2*PI*(180*t+30*t*t))':d=6.9:s=44100[ris0];[ris0]lowpass=f=1000,afade=t=in:st=0:d=0.6,afade=t=out:st=6.3:d=0.5,adelay=2300[ris];
aevalsrc='0.6*sin(2*PI*60*t)*exp(-3.4*t)':d=1.3:s=44100[bo0];[bo0]adelay=9200[bo];
aevalsrc='0.25*sin(2*PI*(820*t-200*t*t))*exp(-3.5*t)':d=0.9:s=44100[fa0];[fa0]adelay=9300[fa];
aevalsrc='0.24*sin(2*PI*500*t)*exp(-20*t)':d=0.3:s=44100[ck0];[ck0]adelay=11600[ck];
[rmb][ris][bo][fa][ck]amix=inputs=5:duration=longest:normalize=0,volume=0.78,afade=t=out:st=14.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
scor_credit) echo "
aevalsrc='0.13*sin(2*PI*(300*t+85*t*t))':d=6.9:s=44100[sw0];[sw0]lowpass=f=2400,afade=t=in:st=0:d=0.4,afade=t=out:st=6.6:d=0.3,adelay=2300[sw];
aevalsrc='0.4*sin(2*PI*75*t)*exp(-3.4*t)':d=1.1:s=44100[bo0];[bo0]adelay=9200[bo];
aevalsrc='0.24*(sin(2*PI*1047*t)+sin(2*PI*1568*t))*exp(-7*t)':d=0.6:s=44100[lk0];[lk0]aecho=0.8:0.7:45:0.3,adelay=9260[lk];
aevalsrc='0.26*sin(2*PI*880*t)*exp(-20*t)':d=0.3:s=44100[ck0];[ck0]adelay=11600[ck];
anoisesrc=d=15:c=pink:a=1:s=44100[ai0];[ai0]lowpass=f=700,volume=0.012[ai];
[ai][sw][bo][lk][ck]amix=inputs=5:duration=longest:normalize=0,volume=0.78,afade=t=out:st=14.4:d=0.6,aformat=channel_layouts=stereo[a]" ;;
esac
}

# key:source_mp4
SRC=(
  "dobanda:media/reel_dobanda/reel_dobanda.mp4"
  "titluri_stat:media/reels/reel_titluri_stat.mp4"
  "card_minim:media/reels/reel_card_minim.mp4"
  "regula72:media/reels/reel_regula72.mp4"
  "pilon3:media/reels/reel_pilon3.mp4"
  "fire:media/reels/reel_fire.mp4"
  "datorie_buna_rea:media/reels/reel_datorie_buna_rea.mp4"
  "masina_rate:media/reels/reel_masina_rate.mp4"
  "scor_credit:media/reels/reel_scor_credit.mp4"
)
for e in "${SRC[@]}"; do
  IFS=':' read -r key src <<< "$e"
  FC="$(fc_for "$key")"
  ffmpeg -y -i "$src" -filter_complex "$FC" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest "${src%.mp4}_tmp.mp4" >/dev/null 2>&1
  mv "${src%.mp4}_tmp.mp4" "$src"
  echo "audio nou -> $key"
done
echo "DONE"
