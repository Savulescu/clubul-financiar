#!/usr/bin/env python3
"""Migrație #2 — pe cele 400 articole existente:
  - JSON-LD complet: datePublished (din git), dateModified (azi), author, image
  - dată vizibilă în .meta
  - timp de citire real (din nr. cuvinte)
Idempotentă."""
import re, glob, os, json, subprocess

ROOT = "/Users/savulescucristian/clubul-financiar"
ART = os.path.join(ROOT, "docs", "articole")
TODAY = "2026-06-19"
RO_LUNI = {"01":"ian.","02":"feb.","03":"mar.","04":"apr.","05":"mai","06":"iun.",
           "07":"iul.","08":"aug.","09":"sep.","10":"oct.","11":"nov.","12":"dec."}
def ro_date(iso):
    iso = iso[:10]; y, m, d = iso.split("-"); return f"{int(d)} {RO_LUNI[m]} {y}"

# data de creare per fișier din git (commit care a adăugat fișierul)
def git_create_dates():
    out = subprocess.run(["git","-C",ROOT,"log","--diff-filter=A","--name-only",
                          "--format=@@%aI","--","docs/articole"],
                         capture_output=True, text=True).stdout
    cur, mp = None, {}
    for line in out.splitlines():
        if line.startswith("@@"):
            cur = line[2:].strip()
        elif line.strip().endswith(".html") and cur:
            base = os.path.basename(line.strip())
            mp.setdefault(base, cur)  # prima apariție (newest-first) — dar A apare o singură dată
    return mp

DATES = git_create_dates()

def reading_minutes(t):
    body = re.search(r'</h1>(.*?)<div class="disc"', t, flags=re.S)
    txt = re.sub(r"<[^>]+>", " ", body.group(1) if body else t)
    n = len(txt.split())
    return max(3, round(n / 200))

changed = 0
for f in glob.glob(os.path.join(ART, "*.html")):
    base = os.path.basename(f)
    t = open(f, encoding="utf-8").read(); o = t
    pub = (DATES.get(base) or TODAY)[:10]

    # 1) JSON-LD: încarcă, completează, rescrie
    m = re.search(r'(<script type="application/ld\+json">)(\{.*?\})(</script>)', t, flags=re.S)
    if m:
        try:
            ld = json.loads(m.group(2))
            ld.setdefault("datePublished", pub)
            ld["dateModified"] = TODAY
            ld.setdefault("author", {"@type":"Organization","name":"Clubul Financiar",
                                     "url":"https://clubulfinanciar.ro/despre.html"})
            ld.setdefault("image", "https://clubulfinanciar.ro/og-image.png")
            # ordine: pune datele după inLanguage dacă există (cosmetic, json e neordonat oricum)
            newld = json.dumps(ld, ensure_ascii=False)
            t = t[:m.start()] + m.group(1) + newld + m.group(3) + t[m.end():]
        except Exception as e:
            print("LD skip", base, e)

    # 2) dată vizibilă în .meta + timp de citire real (dacă nu există deja "Actualizat")
    mins = reading_minutes(t)
    def fix_meta(mm):
        inner = mm.group(1)
        # actualizează minutele
        inner = re.sub(r'\d+\s*min citire', f'{mins} min citire', inner)
        if "Actualizat" not in inner:
            inner = inner.rstrip() + f' · <span class="meta-date">Actualizat {ro_date(pub)}</span>'
        return f'<p class="meta">{inner}</p>'
    t2 = re.sub(r'<p class="meta">(.*?)</p>', fix_meta, t, count=1, flags=re.S)
    if t2: t = t2

    if t != o:
        open(f, "w", encoding="utf-8").write(t); changed += 1

print(f"Articole actualizate: {changed}/{len(glob.glob(os.path.join(ART,'*.html')))}")
print(f"Date din git: {len(DATES)} fișiere mapate")
