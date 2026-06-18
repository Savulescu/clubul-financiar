#!/usr/bin/env python3
"""Normalizează cache-busting la v10 pe toate paginile, injectează article.js (pe articole) și tilt.js (peste tot)."""
import re, os, glob

ROOT = "/Users/savulescucristian/clubul-financiar/docs"
V = "10"
changed = 0
for p in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
    if "/_src/" in p:
        continue
    t = open(p, encoding="utf-8").read()
    orig = t
    for asset in ("style.css", "upgrade.css", "site.js", "article.js", "tilt.js", "three3d.js"):
        t = re.sub(rf'({re.escape(asset)})\?v=\d+', rf'\1?v={V}', t)
    site_tag = f'<script src="/assets/site.js?v={V}"></script>'
    # injectează article.js în paginile de articol
    if "/articole/" in p and "article.js" not in t:
        t = t.replace(site_tag, f'<script src="/assets/article.js?v={V}"></script>' + site_tag)
    # injectează tilt.js pe toate paginile (înainte de site.js)
    if "tilt.js" not in t and site_tag in t:
        t = t.replace(site_tag, f'<script src="/assets/tilt.js?v={V}"></script>' + site_tag)
    if t != orig:
        open(p, "w", encoding="utf-8").write(t)
        changed += 1
print(f"Normalizate {changed} fișiere la v{V}")
