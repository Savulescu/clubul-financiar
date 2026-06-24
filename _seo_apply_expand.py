#!/usr/bin/env python3
"""_seo_apply_expand.py — inserează DETERMINIST secțiuni de extindere (verificate) în articole.
Input JSON: [{slug, html}] — html = unul/mai multe blocuri <h2>...</h2> deja validate.
Inserare HTML-aware ÎNAINTE de <div class="disc"> (disclaimerul de la finalul articolului).
Idempotent: marchează cu <!--cf-expand:slug--> și sare dacă deja prezent. NU atinge restul.
Rulează: python3 _seo_apply_expand.py approved_expand.json
"""
import json, re, sys, os, glob

ROOT = "/Users/savulescucristian/clubul-financiar/docs/articole"
VALID = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(ROOT, "*.html"))}

def main(path):
    items = json.load(open(path, encoding="utf-8"))
    applied = 0; skipped = 0; missing = []
    for it in items:
        slug = it["slug"]; html = (it.get("html") or "").strip()
        if slug not in VALID: missing.append(slug); continue
        if not html: skipped += 1; continue
        f = os.path.join(ROOT, slug + ".html")
        h = open(f, encoding="utf-8").read()
        marker = f"<!--cf-expand:{slug}-->"
        if marker in h: skipped += 1; continue            # idempotent
        block = f'\n{marker}\n{html}\n'
        # inserează înainte de disclaimerul final
        m = re.search(r'<div class="disc">', h)
        if not m:
            # fallback: înainte de </article>
            m = re.search(r'</article>', h)
            if not m: skipped += 1; continue
        h2 = h[:m.start()] + block + h[m.start():]
        open(f, "w", encoding="utf-8").write(h2)
        applied += 1
    print(f"expanded {applied} | skipped {skipped} | missing {len(missing)} {missing[:5]}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "approved_expand.json")
