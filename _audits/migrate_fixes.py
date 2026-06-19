#!/usr/bin/env python3
"""Migrație deterministică #1 — fix-uri sistemice peste fișierele statice.
Idempotentă. Raportează ce a schimbat. NU atinge conjugări/diacritice (alea = agent)."""
import re, glob, os, json

ROOT = "/Users/savulescucristian/clubul-financiar"
DOCS = os.path.join(ROOT, "docs")

CYR = {  # homoglife chirilice -> latin (niciun uz legitim pe site RO)
    'А':'A','В':'B','Е':'E','К':'K','М':'M','Н':'H','О':'O','Р':'P','С':'C','Т':'T','Х':'X',
    'а':'a','е':'e','о':'o','р':'p','с':'c','у':'y','х':'x','і':'i','І':'I','ј':'j','м':'m',
    'ф':'f','ѕ':'s','Ѕ':'S',
}
CYR_TT = {ord(k): v for k, v in CYR.items()}

def transform(t):
    n = {}
    # 1) cache-busting unificat -> v=21
    t2 = re.sub(r'\?v=\d+', '?v=21', t); n['cache'] = (t2 != t); t = t2
    # 2) săgeată dublă: scoate ' →' literal din .more (păstrăm ::after-ul animat din CSS)
    t2 = re.sub(r'(class="more"[^>]*>)([^<]*?)\s*→</span>', r'\1\2</span>', t); n['arrow'] = (t2 != t); t = t2
    # 3) titlu dublat
    t2 = t.replace('— Clubul Financiar — Clubul Financiar', '— Clubul Financiar'); n['title'] = (t2 != t); t = t2
    # 4) homoglife chirilice
    t2 = t.translate(CYR_TT); n['cyr'] = (t2 != t); t = t2
    # 5) emoji foarfecă -> card (categoria Datorii)
    t2 = t.replace('✂️', '💳').replace('✂', '💳'); n['scissors'] = (t2 != t); t = t2
    # 6) font variabil range (450 devine valid) — doar segmentul Jakarta
    t2 = t.replace('Plus+Jakarta+Sans:wght@400;500;600;700;800', 'Plus+Jakarta+Sans:wght@400..800'); n['font'] = (t2 != t); t = t2
    return t, n

def run():
    files = glob.glob(os.path.join(DOCS, "**", "*.html"), recursive=True)
    files += [os.path.join(DOCS, "search-index.json"), os.path.join(ROOT, "_records.json")]
    tally = {}
    changed = 0
    for f in files:
        if not os.path.exists(f):
            continue
        orig = open(f, encoding="utf-8").read()
        new, n = transform(orig)
        if new != orig:
            open(f, "w", encoding="utf-8").write(new)
            changed += 1
            for k, v in n.items():
                if v:
                    tally[k] = tally.get(k, 0) + 1
    print(f"Fișiere modificate: {changed}/{len(files)}")
    print("Pe categorie (nr. fișiere):", tally)

if __name__ == "__main__":
    run()
