#!/usr/bin/env python3
"""Fix split-brain design pe articolele premium: adaugă <main class="u-page"> în jurul
<article> pe cele 692 de articole care nu-l au (cele 308 gratuite îl au deja, de la
template-ul nou din _build_site.py). Patch chirurgical pe docs/ — NU rebuild
(_build_site.py integral e interzis: GLOS_SRC mort → regresie search-index).

Idempotent: sare peste fișierele care au deja <main. Guard: exact un </article> per fișier.
"""
import glob, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
files = sorted(glob.glob(os.path.join(ROOT, "docs", "articole", "*.html")))

patched, skipped, errors = 0, 0, []
for f in files:
    with open(f, encoding="utf-8") as fh:
        t = fh.read()
    if "<main" in t:
        skipped += 1
        continue
    open_tag = '<article class="article" data-premium="1">'
    if open_tag not in t:
        # articol fără main și fără data-premium — nu ar trebui să existe
        errors.append((f, "no premium article tag"))
        continue
    if t.count(open_tag) != 1 or t.count("</article>") != 1:
        errors.append((f, f"unexpected counts open={t.count(open_tag)} close={t.count('</article>')}"))
        continue
    t = t.replace(open_tag, '<main class="u-page">' + open_tag, 1)
    t = t.replace("</article>", "</article></main>", 1)
    # articolele premium vechi aveau deja un </main> orfan (strip vechi al tagului
    # de deschidere) → după wrap rezultă dublu close; îl deduplicăm
    t = t.replace("</article></main></main>", "</article></main>", 1)
    with open(f, "w", encoding="utf-8") as fh:
        fh.write(t)
    patched += 1

print(f"patched={patched} skipped(main deja)={skipped} errors={len(errors)}")
for f, why in errors[:20]:
    print("  ERR", os.path.basename(f), "->", why)
sys.exit(1 if errors else 0)
