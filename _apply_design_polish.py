#!/usr/bin/env python3
"""Mass-patch design polish 2026-07-02 (rulat pe docs/, idempotent):
1. Google Fonts non-render-blocking: preload + media="print" onload swap + noscript
   (cel mai mare cost de LCP mobil — audit perf P1). CSP permite inline handlers.
2. Articole: strip emoji din meta-row (<a href="/educatie#cat">📈 Investiții</a> → text sobru).
3. Calculatoare + ultra/profil: label-uri asociate programatic (for="id") — audit a11y P1.
4. theme-color verde vechi #10b981 → navy brand #0f2540 (bara browserului mobil).
"""
import glob, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")

FONT_RE = re.compile(
    r'<link href="(https://fonts\.googleapis\.com/css2\?[^"]+)" rel="stylesheet">')

def patch_fonts(t):
    def rep(m):
        url = m.group(1)
        return (f'<link rel="preload" as="style" href="{url}">'
                f'<link href="{url}" rel="stylesheet" media="print" onload="this.media=\'all\'">'
                f'<noscript><link href="{url}" rel="stylesheet"></noscript>')
    if 'rel="stylesheet" media="print"' in t:   # deja patch-uit
        return t, 0
    return FONT_RE.subn(rep, t)

# emoji la începutul textului anchor-ului de categorie din meta-row articol
META_EMOJI_RE = re.compile(
    r'(<a href="/educatie#[a-z]+">)[←-⯿☀-➿️\U0001F000-\U0001FAFF]+\s*')

LABEL_RE = re.compile(r'<label>([^<]+)</label>')

def patch_labels(t):
    """<label>X</label> ... <input id=y> → <label for="y">X</label> (primul input care urmează)."""
    out, n, pos = [], 0, 0
    for m in LABEL_RE.finditer(t):
        nxt = re.search(r'<(?:input|select)[^>]*\bid=["\']?([A-Za-z0-9_-]+)', t[m.end():m.end() + 400])
        out.append(t[pos:m.start()])
        if nxt:
            out.append(f'<label for="{nxt.group(1)}">{m.group(1)}</label>')
            n += 1
        else:
            out.append(m.group(0))
        pos = m.end()
    out.append(t[pos:])
    return "".join(out), n

stats = {"fonts": 0, "meta": 0, "labels": 0, "theme": 0, "files": 0}
for f in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
    rel = os.path.relpath(f, ROOT)
    with open(f, encoding="utf-8") as fh:
        t = fh.read()
    orig = t
    t, nf = patch_fonts(t)
    stats["fonts"] += nf
    if '<meta name="theme-color" content="#10b981">' in t:
        t = t.replace('<meta name="theme-color" content="#10b981">',
                      '<meta name="theme-color" content="#0f2540">')
        stats["theme"] += 1
    if rel.startswith("articole" + os.sep):
        t, nm = META_EMOJI_RE.subn(r"\1", t)
        stats["meta"] += nm
    if rel.startswith("calculatoare" + os.sep) or rel == os.path.join("ultra", "profil.html"):
        t, nl = patch_labels(t)
        stats["labels"] += nl
    if t != orig:
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(t)
        stats["files"] += 1

print(stats)
