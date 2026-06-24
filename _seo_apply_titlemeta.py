#!/usr/bin/env python3
"""_seo_apply_titlemeta.py — aplică DETERMINIST fix-uri de title/meta verificate adversarial.
Input: JSON [{slug, field:'title'|'meta', value, reason}].
- title: rescrie <title> păstrând sufixul " — Clubul Financiar"; sincronizează og:title + twitter:title (versiunea fără sufix).
- meta : rescrie <meta name=description> + og:description + twitter:description + JSON-LD Article "description".
NU atinge nimic altceva. Idempotent. Rulează: python3 _seo_apply_titlemeta.py approved.json
"""
import re, json, sys, html, os

SUFFIX = " — Clubul Financiar"

def esc(s): return html.escape(s, quote=True)

def apply_title(h, val):
    val = val.strip()
    new_title = esc(val) + SUFFIX
    h = re.sub(r'(<title>)[^<]*(</title>)', lambda m: m.group(1)+new_title+m.group(2), h, count=1)
    # og/twitter title = fără sufix
    h = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1)+esc(val)+m.group(2), h, count=1)
    h = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")', lambda m: m.group(1)+esc(val)+m.group(2), h, count=1)
    return h

def apply_meta(h, val):
    val = val.strip(); v = esc(val)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1)+v+m.group(2), h, count=1)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1)+v+m.group(2), h, count=1)
    h = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")', lambda m: m.group(1)+v+m.group(2), h, count=1)
    # JSON-LD Article description (first occurrence in Article block)
    def ld(m):
        block = m.group(0)
        block2 = re.sub(r'("description":\s*")(?:[^"\\]|\\.)*(")', lambda x: x.group(1)+val.replace('"','\\"')+x.group(2), block, count=1)
        return block2
    h = re.sub(r'\{"@context":\s*"https://schema.org",\s*"@type":\s*"Article".*?\}</script>', ld, h, count=1, flags=re.S)
    return h

def main(path):
    changes = json.load(open(path, encoding='utf-8'))
    by_slug = {}
    for c in changes:
        by_slug.setdefault(c['slug'], []).append(c)
    applied = 0; missing = []
    for slug, cs in by_slug.items():
        f = f"docs/articole/{slug}.html"
        if not os.path.exists(f):
            missing.append(slug); continue
        h = open(f, encoding='utf-8').read(); orig = h
        for c in cs:
            if c['field'] == 'title': h = apply_title(h, c['value'])
            elif c['field'] == 'meta': h = apply_meta(h, c['value'])
        if h != orig:
            open(f, 'w', encoding='utf-8').write(h); applied += 1
    print(f"applied to {applied} files | changes: {len(changes)} | missing slugs: {len(missing)}")
    if missing: print("  missing:", missing[:10])

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'approved.json')
