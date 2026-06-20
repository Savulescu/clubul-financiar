#!/usr/bin/env python3
"""Integrează cele 200 lecții premium noi (din _audits/premium200_plan.json):
  1. adaugă records (slug,title,metaDescription,category) în _records.json (fără duplicate)
  2. marchează slug-urile ca premium în _audits/free_premium_split.json (pe domeniul=category)
Rulează ÎNAINTE de _build_site.py / _build_manual.py / _apply_premium.py."""
import json, os

ROOT = "/Users/savulescucristian/clubul-financiar"
PLAN = os.path.join(ROOT, "_audits", "premium200_plan.json")
RECORDS = os.path.join(ROOT, "_records.json")
SPLIT = os.path.join(ROOT, "_audits", "free_premium_split.json")

plan = json.load(open(PLAN, encoding="utf-8"))
records = json.load(open(RECORDS, encoding="utf-8"))
existing_slugs = {r["slug"] for r in records}

added = 0
for p in plan:
    if p["slug"] in existing_slugs:
        continue
    records.append({
        "slug": p["slug"], "title": p["title"],
        "metaDescription": p["metaDescription"], "category": p["category"],
    })
    existing_slugs.add(p["slug"])
    added += 1

json.dump(records, open(RECORDS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"_records.json: +{added} records (total {len(records)})")

# marchează premium în split
split = json.load(open(SPLIT, encoding="utf-8"))
bydom = {s["domain"]: s for s in split}
prem_added = 0
for p in plan:
    dom = p["category"]
    if dom not in bydom:
        bydom[dom] = {"domain": dom, "free": [], "premium": []}
        split.append(bydom[dom])
    s = bydom[dom]
    s.setdefault("premium", [])
    if p["slug"] not in s["premium"] and p["slug"] not in s.get("free", []):
        s["premium"].append(p["slug"])
        prem_added += 1

json.dump(split, open(SPLIT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"free_premium_split.json: +{prem_added} slug-uri premium")
