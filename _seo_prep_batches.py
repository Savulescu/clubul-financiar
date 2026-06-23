#!/usr/bin/env python3
"""_seo_prep_batches.py — pregătește fișiere-batch pentru pasul cu agenți (in-body links + meta).
Scrie SCRATCH/_seo_batch_NNN.json. Fiecare item conține tot ce-i trebuie agentului.
"""
import json, re, html, os, glob

ROOT = "/Users/savulescucristian/clubul-financiar/docs"
ART = os.path.join(ROOT, "articole")
CAND = "/Users/savulescucristian/clubul-financiar/_seo_candidates.json"
SCRATCH = "/private/tmp/claude-501/-Users-savulescucristian/2fc4c138-be21-4ac2-a94b-f866e8bfe4e1/scratchpad"
BATCH = 8
SHORT_WORDS = 950

def strip(s): return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()

cands = json.load(open(CAND, encoding="utf-8"))
items = []
for slug, cs in cands.items():
    p = os.path.join(ART, slug + ".html")
    if not os.path.exists(p): continue
    t = open(p, encoding="utf-8").read()
    bm = re.search(r"</h1>(.*?)<div class=\"disc\"", t, re.S)
    body = bm.group(1) if bm else ""
    # paragrafe text (fără secțiunea Pe scurt / related)
    body_wo_rel = re.split(r'<section class="related"', body)[0]
    paras = [strip(x) for x in re.findall(r"<p[^>]*>(.*?)</p>", body_wo_rel, re.S)]
    paras = [x for x in paras if len(x) > 40][:14]
    md = re.search(r'<meta name="description" content="([^"]*)"', t)
    title_m = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    words = len(strip(body_wo_rel).split())
    items.append({
        "slug": slug,
        "title": strip(title_m.group(1)) if title_m else slug,
        "cur_desc": html.unescape(md.group(1)) if md else "",
        "words": words,
        "may_expand": words < SHORT_WORDS,
        "paragraphs": paras,
        "candidates": [{"slug": c["slug"], "title": c["title"]} for c in cs[:10]],
    })

items.sort(key=lambda x: x["slug"])
nb = 0
for i in range(0, len(items), BATCH):
    chunk = items[i:i+BATCH]
    fn = os.path.join(SCRATCH, f"_seo_batch_{nb:03d}.json")
    json.dump(chunk, open(fn, "w", encoding="utf-8"), ensure_ascii=False)
    nb += 1
print(f"articole: {len(items)} | batch-uri: {nb} (size {BATCH}) | may_expand: {sum(x['may_expand'] for x in items)}")
print(f"scris în {SCRATCH}/_seo_batch_NNN.json")
