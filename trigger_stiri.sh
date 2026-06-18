#!/bin/zsh
# Declanșează workflow-ul de știri pe GitHub (backstop fiabil pentru cron-ul GitHub care întârzie).
cd "$HOME/clubul-financiar" || exit 1
TOKEN=$(printf "protocol=https\nhost=github.com\n\n" | git credential fill 2>/dev/null | sed -n 's/^password=//p')
[ -z "$TOKEN" ] && { echo "fără token"; exit 1; }
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/Savulescu/clubul-financiar/actions/workflows/stiri.yml/dispatches" \
  -d '{"ref":"main"}' -o /dev/null -w "stiri dispatch: HTTP %{http_code}\n"
