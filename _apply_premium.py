#!/usr/bin/env python3
"""Aplică gating-ul premium pe articolele din setul premium (free_premium_split.json):
  1. <article class="article">  ->  <article class="article" data-premium="1">
  2. JSON-LD: adaugă isAccessibleForFree:false + hasPart (.premium-rest)
Idempotent: sare peste articolele care au deja data-premium. SEO-safe (conținut rămâne în DOM)."""
import json, os, re

ROOT = "/Users/savulescucristian/clubul-financiar"
ART = os.path.join(ROOT, "docs", "articole")
SPLIT = os.path.join(ROOT, "_audits", "free_premium_split.json")

split = json.load(open(SPLIT, encoding="utf-8"))
PREMIUM = set()
for s in split:
    for sl in s.get("premium", []):
        PREMIUM.add(sl)

applied, already, missing = 0, 0, 0
for slug in sorted(PREMIUM):
    path = os.path.join(ART, slug + ".html")
    if not os.path.exists(path):
        missing += 1
        continue
    t = open(path, encoding="utf-8").read()
    if 'data-premium="1"' in t:
        already += 1
        continue
    changed = False
    # 1. marchează <article>
    new = t.replace('<article class="article">', '<article class="article" data-premium="1">', 1)
    if new != t:
        t = new; changed = True
    # 2. JSON-LD: injectează isAccessibleForFree + hasPart în obiectul Article
    m = re.search(r'(<script type="application/ld\+json">)(\{.*?\})(</script>)', t, re.S)
    if m:
        try:
            d = json.loads(m.group(2))
            if not d.get("isAccessibleForFree") is False or "hasPart" not in d:
                d["isAccessibleForFree"] = False
                d["hasPart"] = {"@type": "WebPageElement", "isAccessibleForFree": False, "cssSelector": ".premium-rest"}
                newld = m.group(1) + json.dumps(d, ensure_ascii=False) + m.group(3)
                t = t[:m.start()] + newld + t[m.end():]
                changed = True
        except Exception as e:
            print("  ld parse skip", slug, e)
    if changed:
        open(path, "w", encoding="utf-8").write(t)
        applied += 1

print(f"Premium gating aplicat: {applied} | aveau deja: {already} | lipsă fișier: {missing} | total set premium: {len(PREMIUM)}")
