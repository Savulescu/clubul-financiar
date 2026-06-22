#!/bin/bash
# Assemble all 9 reels into "postari pro/N_key/" with reel.mp4 + text.txt
cd ~/clubul-financiar
OUT="postari pro"
mkdir -p "$OUT"

# index:key:mp4_source
ENTRIES=(
  "1:dobanda_compusa:media/reels/reel_dobanda_compusa.mp4"
  "2:titluri_stat:media/reels/reel_titluri_stat.mp4"
  "3:card_minim:media/reels/reel_card_minim.mp4"
  "4:regula72:media/reels/reel_regula72.mp4"
  "5:pilon3:media/reels/reel_pilon3.mp4"
  "6:fire:media/reels/reel_fire.mp4"
  "7:datorie_buna_rea:media/reels/reel_datorie_buna_rea.mp4"
  "8:masina_rate:media/reels/reel_masina_rate.mp4"
  "9:scor_credit:media/reels/reel_scor_credit.mp4"
)

for e in "${ENTRIES[@]}"; do
  IFS=':' read -r n key src <<< "$e"
  d="$OUT/${n}_${key}"
  mkdir -p "$d"
  # video
  if [ -f "$src" ]; then cp "$src" "$d/reel.mp4"; vid="OK"; else vid="--lipsește (se randează)"; fi
  # caption
  if [ -f "captions/$key.txt" ]; then cp "captions/$key.txt" "$d/text.txt"; cap="OK"; else cap="--"; fi
  printf "%-22s video:%-22s text:%s\n" "${n}_${key}" "$vid" "$cap"
done
echo "---"
echo "Folder: $(pwd)/$OUT"
