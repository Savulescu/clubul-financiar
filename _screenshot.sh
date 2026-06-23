#!/usr/bin/env bash
# Clubul Financiar — serve docs/ locally and screenshot pages headless.
# Usage:  ./_screenshot.sh [label] [page1 page2 ...]
#   label   : subfolder name for this batch (default: timestamp-less "shot")
#   pages   : page paths relative to docs/ (default: a representative set)
# Output:   SHOTDIR/<label>/<page>__<width>.png  (desktop 1440 + mobile 390)
# Requires: python3, Google Chrome.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DOCS="$ROOT/docs"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SHOTDIR="${CF_SHOTDIR:-/private/tmp/claude-501/-Users-savulescucristian/164f0cba-a983-42c1-b0b3-2ecb290ca3d2/scratchpad/shots}"
PORT="${CF_PORT:-8765}"

LABEL="${1:-shot}"; shift || true
PAGES=("$@")
if [ ${#PAGES[@]} -eq 0 ]; then
  PAGES=(index.html premium.html educatie.html calculatoare.html instrumente.html masterclass.html stiri.html glosar.html incepe-aici.html login.html)
fi

OUT="$SHOTDIR/$LABEL"; mkdir -p "$OUT"

# start server
lsof -ti:"$PORT" 2>/dev/null | xargs kill -9 2>/dev/null || true
( cd "$DOCS" && exec python3 -m http.server "$PORT" >/tmp/cf_server.log 2>&1 ) &
SRV=$!
cleanup(){ kill -9 "$SRV" 2>/dev/null || true; lsof -ti:"$PORT" 2>/dev/null | xargs kill -9 2>/dev/null || true; }
trap cleanup EXIT
# wait until the server actually answers (max ~6s)
for _ in $(seq 1 30); do
  curl -s -o /dev/null "http://localhost:$PORT/index.html" && break
  sleep 0.2
done

shoot(){ # url out width height
  "$CHROME" --headless=new --use-angle=swiftshader --disable-gpu --hide-scrollbars \
    --window-size="$3,$4" --screenshot="$2" "$1" >/dev/null 2>&1 || echo "  ! failed $1"
}

for p in "${PAGES[@]}"; do
  name="${p//\//_}"; name="${name%.html}"
  url="http://localhost:$PORT/$p"
  code=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo 000)
  echo "$p -> HTTP $code"
  [ "$code" = "200" ] || continue
  shoot "$url" "$OUT/${name}__1440.png" 1440 2600
  shoot "$url" "$OUT/${name}__390.png"  390  1900
done
echo "==> $OUT"
ls -1 "$OUT"
