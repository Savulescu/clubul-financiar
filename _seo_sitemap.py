#!/usr/bin/env python3
"""_seo_sitemap.py — sitemap.xml comprehensiv, scan-based, URL-uri curate, lastmod per fișier.
Acoperă: homepage, landing, calculatoare, articole, masterclass, manual, glosar, unelte, ultra(public).
Exclude: noindex, login/account/reset/statistici/dezabonare, newsletter/preview, _src/_quiz.
Rulează ULTIMUL (după orice build). Înlocuiește sitemap-ul parțial cu dată uniformă.
"""
import os, re, glob, datetime

ROOT = "/Users/savulescucristian/clubul-financiar/docs"
BASE = "https://clubulfinanciar.ro"

EXCLUDE_SUBSTR = ("/login", "/account", "/reset", "/statistici", "/dezabonare",
                  "/newsletter/preview", "/_src", "/_quiz", "/_")

def clean_url(rel):
    rel = re.sub(r"/index\.html$", "/", rel)
    rel = re.sub(r"\.html$", "", rel)
    return BASE + rel

def priority(rel):
    if rel == "/index.html": return "1.0"
    base = rel.strip("/")
    if base in ("educatie","incepe-aici","calculatoare","teste","glosar","masterclass","manual"): return "0.8"
    if base.startswith("calculatoare/"): return "0.7"
    if base.startswith("articole/"): return "0.6"
    if base.startswith(("masterclass/","manual/","cursuri/","unelte/","instrumente/")): return "0.6"
    if base in ("terms","privacy","contact","feedback","despre","dezabonare"): return "0.3"
    return "0.5"

def changefreq(rel):
    if rel.strip("/").startswith(("stiri","newsletter")) or rel == "/index.html": return "daily"
    if rel.strip("/").startswith("articole/"): return "monthly"
    return "weekly"

def main():
    urls = []
    seen = set()
    for p in sorted(glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True)):
        rel = "/" + os.path.relpath(p, ROOT).replace("\\", "/")
        if any(x in rel for x in EXCLUDE_SUBSTR):
            continue
        t = open(p, encoding="utf-8").read()
        if re.search(r'name="robots"[^>]*content="[^"]*noindex', t):
            continue
        loc = clean_url(rel)
        if loc in seen:
            continue
        seen.add(loc)
        mtime = datetime.date.fromtimestamp(os.path.getmtime(p)).isoformat()
        urls.append((loc, mtime, changefreq(rel), priority(rel)))
    # homepage prima
    urls.sort(key=lambda u: (u[0] != BASE + "/", u[0]))
    body = "\n".join(
        f'<url><loc>{loc}</loc><lastmod>{lm}</lastmod><changefreq>{cf}</changefreq><priority>{pr}</priority></url>'
        for loc, lm, cf, pr in urls)
    out = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n"
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(out)
    print(f"sitemap.xml: {len(urls)} URL-uri (curate, lastmod per fișier)")

if __name__ == "__main__":
    main()
