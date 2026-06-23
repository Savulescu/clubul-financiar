#!/usr/bin/env python3
"""_seo_all.py — orchestrator SEO. Rulează DUPĂ orice build de conținut (articole/manual/glosar/masterclass).
Reaplică, idempotent, toate optimizările SEO deterministe + regenerează sitemap-ul comprehensiv.

  python3 _seo_all.py

Pași: 1) _seo_optimize.py  (related semantic + breadcrumb + trim pe articole; rescrie _seo_candidates.json)
      2) _seo_pages.py     (schema/meta pe calculatoare/landing/static)
      3) _seo_pages2.py    (masterclass + despre/glosar/educatie + trim universal)
      4) _seo_sitemap.py   (sitemap.xml curat, lastmod per fișier — RULEAZĂ ULTIMUL)
      5) seo_audit.py      (raport final)

NOTĂ: NU rulează _build_site.py (acela ar regenera search-index.json fără glosar — vezi GLOS_SRC stale).
Pasul cu agenți (in-body links + meta calitativ) se face separat via workflow + _seo_apply_inbody.py.
"""
import subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["_seo_optimize.py", "_seo_pages.py", "_seo_pages2.py", "_seo_sitemap.py", "seo_audit.py"]
for s in STEPS:
    print(f"\n===== {s} =====")
    r = subprocess.run([sys.executable, os.path.join(HERE, s)])
    if r.returncode != 0:
        print(f"!! {s} a eșuat (cod {r.returncode})"); sys.exit(r.returncode)
print("\n✅ SEO reaplicat complet.")
