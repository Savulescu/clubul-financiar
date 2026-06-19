#!/bin/bash
cd /Users/savulescucristian/clubul-financiar || exit 1
/Users/savulescucristian/stockmarketcap/stockmarketcap/venv/bin/python news_external.py >> /tmp/cf_externe.log 2>&1
git add docs/stiri-externe.html _external_store.json
if ! git diff --cached --quiet; then
  git commit -q -m "auto: știri externe (explainer RO)" >> /tmp/cf_externe.log 2>&1
  git pull --rebase -X theirs origin main -q >> /tmp/cf_externe.log 2>&1
  git push origin main >> /tmp/cf_externe.log 2>&1
fi
echo "$(date) trigger_externe done" >> /tmp/cf_externe.log
