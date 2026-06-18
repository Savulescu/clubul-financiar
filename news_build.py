#!/usr/bin/env python3
"""Agregator știri financiare RO pentru Clubul Financiar.
Adună din mai multe ziare (RSS), ordonează după importanță (sursă + recență + relevanță),
și generează docs/stiri.html. Rulează în GitHub Actions (cron). Doar titlu + scurt rezumat
+ link către sursă (agregator, nu republică articole întregi)."""
import os, re, time, html, datetime
import requests, feedparser

ROOT = os.path.dirname(os.path.abspath(__file__))

# (nume, url, greutate sursă, necesită filtru de relevanță financiară)
SOURCES = [
    ("Ziarul Financiar", "https://www.zf.ro/rss", 1.0, False),
    ("ZF Companii", "https://www.zf.ro/rss/companii", 0.9, False),
    ("Economica.net", "https://www.economica.net/rss", 0.9, False),
    ("Financial Intelligence", "https://financialintelligence.ro/feed/", 0.85, False),
    ("Mediafax Economic", "https://www.mediafax.ro/rss/economic.xml", 0.8, False),
    ("Digi24 Economie", "https://www.digi24.ro/rss/economie", 0.85, False),
    ("Curs de guvernare", "https://cursdeguvernare.ro/feed", 0.8, False),
    ("HotNews", "https://hotnews.ro/feed", 0.75, True),
]
KW = ["ban", "leu", "euro", "dolar", "bnr", "inflați", "infla", "dobând", "dobanzi", "credit",
      "taxe", "taxă", "impozit", "anaf", "bursă", "bursa", "bvb", "acțiun", "investiți", "economi",
      "salari", "pensi", "preț", "pret", "buget", "pib", "bancă", "banca", "fisc", "tva", "energie",
      "piață", "piata", "datorie", "deficit", "criz", "scump", "ieftin", "randament", "etf", "imobiliar"]
MAX_ITEMS = 48
MAX_AGE_DAYS = 4

def clean(t):
    t = re.sub(r"<[^>]+>", "", t or "")
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()

def reltime(ts):
    if not ts: return ""
    d = int(time.time()) - ts
    if d < 3600: return f"acum {max(1, d // 60)} min"
    if d < 86400: return f"acum {d // 3600} h"
    return f"acum {d // 86400} zile"

def fetch(url):
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0 (ClubulFinanciar news aggregator)"})
        return feedparser.parse(r.content)
    except Exception as e:
        print("  fail", url, e); return None

def collect():
    items, seen = [], set()
    now = time.time()
    for name, url, w, need in SOURCES:
        f = fetch(url)
        if not f or not f.entries:
            print(f"  0  {name}"); continue
        cnt = 0
        for e in f.entries[:30]:
            title = clean(e.get("title", ""))
            link = e.get("link", "")
            if not title or not link: continue
            key = re.sub(r"[^a-z0-9]", "", title.lower())[:60]
            if key in seen: continue
            tp = e.get("published_parsed") or e.get("updated_parsed")
            ts = int(time.mktime(tp)) if tp else int(now)
            if (now - ts) > MAX_AGE_DAYS * 86400: continue
            summ = clean(e.get("summary", ""))[:200]
            text = (title + " " + summ).lower()
            kw_hit = any(k in text for k in KW)
            if need and not kw_hit: continue
            seen.add(key)
            age_h = (now - ts) / 3600
            score = w + max(0, 2.0 - age_h / 12) + (0.6 if kw_hit else 0)
            items.append({"title": title, "link": link, "source": name, "ts": ts,
                          "summary": summ, "score": score})
            cnt += 1
        print(f"  {cnt:2}  {name}")
    items.sort(key=lambda x: x["score"], reverse=True)
    return items[:MAX_ITEMS]

FONT = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">'

def build():
    items = collect()
    today = datetime.date.today().strftime("%d.%m.%Y")
    cards = ""
    for it in items:
        t = html.escape(it["title"]); s = html.escape(it["summary"])
        cards += f'''<a class="card reveal" href="{html.escape(it['link'])}" target="_blank" rel="noopener nofollow">
<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:8px">
<span class="pill">{html.escape(it['source'])}</span><span style="color:var(--muted);font-size:.8rem">{reltime(it['ts'])}</span></div>
<h3 style="font-size:1.05rem">{t}</h3>{f'<p>{s}</p>' if s else ''}<span class="more">Citește la sursă →</span></a>\n'''
    page = f'''<!DOCTYPE html><html lang="ro"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Știri financiare România — Clubul Financiar</title>
<meta name="description" content="Cele mai importante știri financiare și economice din România, agregate din mai multe surse și actualizate automat.">
<meta name="robots" content="index, follow"><meta name="theme-color" content="#10b981">
<link rel="canonical" href="https://clubulfinanciar.ro/stiri.html">
<link rel="icon" type="image/png" href="/favicon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website"><meta property="og:site_name" content="Clubul Financiar"><meta property="og:locale" content="ro_RO">
<meta property="og:title" content="Știri financiare România — Clubul Financiar"><meta property="og:description" content="Cele mai importante știri financiare din România, într-un singur loc."><meta property="og:url" content="https://clubulfinanciar.ro/stiri.html"><meta property="og:image" content="https://clubulfinanciar.ro/og-image.png">
<script>(function(){{var t=localStorage.getItem("cf-theme");if(t)document.documentElement.setAttribute("data-theme",t);}})();</script>
{FONT}
<link rel="stylesheet" href="/assets/style.css?v=5"><link rel="stylesheet" href="/assets/upgrade.css?v=5"></head><body>
<section class="section-sm" style="background:var(--bg-soft)"><div class="container center">
<p class="eyebrow">Știri · actualizat {today}</p><h1 class="title">Știri financiare România</h1>
<p class="lead" style="margin-inline:auto">Cele mai importante știri economice și financiare din România, adunate din mai multe surse și ordonate după relevanță.</p></div></section>
<section class="section"><div class="container"><div class="grid grid-3">
{cards}
</div>
<p style="color:var(--muted);font-size:.85rem;margin-top:30px;text-align:center">Știrile sunt agregate automat din surse externe (titlu + scurt rezumat + link). Drepturile aparțin publicațiilor sursă. Actualizat automat de mai multe ori pe zi.</p>
</div></section>
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script><script src="/assets/site.js?v=5"></script></body></html>'''
    open(os.path.join(ROOT, "docs", "stiri.html"), "w", encoding="utf-8").write(page)
    print(f"stiri.html scris cu {len(items)} știri")

if __name__ == "__main__":
    build()
