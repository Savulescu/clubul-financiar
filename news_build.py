#!/usr/bin/env python3
"""Agregator știri financiare RO pentru Clubul Financiar.
Adună din mai multe ziare (RSS), ordonează după importanță (sursă + recență + relevanță),
și generează docs/stiri.html. Rulează în GitHub Actions (cron). Doar titlu + scurt rezumat
+ link către sursă (agregator, nu republică articole întregi)."""
import os, re, time, html, datetime
import requests, feedparser

ROOT = os.path.dirname(os.path.abspath(__file__))

# (nume, url, greutate sursă, necesită filtru relevanță, e_google_news)
GN = "https://news.google.com/rss/search?q={}&hl=ro&gl=RO&ceid=RO:ro"
def gn(q): return GN.format(q.replace(" ", "+").replace(":", "%3A"))
SOURCES = [
    # --- RSS direct (sigure) ---
    ("Ziarul Financiar", "https://www.zf.ro/rss", 1.0, False, False),
    ("ZF Companii", "https://www.zf.ro/rss/companii", 0.9, False, False),
    ("Economica.net", "https://www.economica.net/rss", 0.9, False, False),
    ("Financial Intelligence", "https://financialintelligence.ro/feed/", 0.85, False, False),
    ("Mediafax Economic", "https://www.mediafax.ro/rss/economic.xml", 0.8, False, False),
    ("Digi24 Economie", "https://www.digi24.ro/rss/economie", 0.85, False, False),
    ("Curs de guvernare", "https://cursdeguvernare.ro/feed", 0.8, False, False),
    # --- presa financiară/business (via Google News site:) ---
    ("Profit.ro", gn("site:profit.ro"), 0.9, False, True),
    ("Bursa.ro", gn("site:bursa.ro"), 0.85, False, True),
    ("Wall-Street.ro", gn("site:wall-street.ro"), 0.85, False, True),
    ("Capital.ro", gn("site:capital.ro"), 0.78, False, True),
    ("Business Magazin", gn("site:businessmagazin.ro"), 0.82, False, True),
    ("Forbes România", gn("site:forbes.ro"), 0.8, False, True),
    ("Economedia", gn("site:economedia.ro"), 0.8, False, True),
    ("StartupCafe", gn("site:startupcafe.ro"), 0.72, False, True),
    ("start-up.ro", gn("site:start-up.ro"), 0.7, False, True),
    ("Agerpres Economic", gn("site:agerpres.ro economie"), 0.8, False, True),
    ("Termene.ro Blog", gn("site:termene.ro"), 0.68, False, True),
    # --- presa generală, secțiune economie (via Google News) ---
    ("HotNews Economie", gn("site:hotnews.ro economie"), 0.78, False, True),
    ("Adevărul Economie", gn("site:adevarul.ro economie"), 0.72, False, True),
    ("Libertatea Bani", gn("site:libertatea.ro bani"), 0.7, False, True),
    ("G4Media Economic", gn("site:g4media.ro economie"), 0.74, False, True),
    ("Spotmedia Economie", gn("site:spotmedia.ro economie"), 0.72, False, True),
    ("Ziare.com Economie", gn("site:ziare.com economie"), 0.68, False, True),
    ("ProTV Economic", gn("site:stirileprotv.ro economic"), 0.7, False, True),
    # --- surse suplimentare ---
    ("Income Magazine", gn("site:incomemagazine.ro"), 0.74, False, True),
    ("Money.ro", gn("site:money.ro"), 0.72, False, True),
    ("Banking News", gn("site:bankingnews.ro"), 0.74, False, True),
    ("Conso.ro", gn("site:conso.ro"), 0.7, False, True),
    ("AvocatNet Fiscal", gn("site:avocatnet.ro fiscal"), 0.72, False, True),
    ("Contzilla", gn("site:contzilla.ro"), 0.68, False, True),
    ("1asig (asigurări)", gn("site:1asig.ro"), 0.7, False, True),
    ("Biziday", gn("site:biziday.ro economie"), 0.72, False, True),
    ("PressOne", gn("site:pressone.ro economie"), 0.7, False, True),
    ("Panorama", gn("site:panorama.ro economie"), 0.72, False, True),
    ("Antena3 Economic", gn("site:antena3.ro economic"), 0.68, False, True),
    ("Observator Economic", gn("site:observatornews.ro economic"), 0.68, False, True),
    ("DCNews Economie", gn("site:dcnews.ro economie"), 0.66, False, True),
    ("Știri pe surse Economie", gn("site:stiripesurse.ro economie"), 0.66, False, True),
    ("Jurnalul Economic", gn("site:jurnalul.ro economie"), 0.66, False, True),
    ("Criptomonede RO", gn("criptomonede OR cripto Romania"), 0.7, True, True),
]
PER_SOURCE = 9  # max articole luate per sursă
KW = ["ban", "leu", "euro", "dolar", "bnr", "inflați", "infla", "dobând", "dobanzi", "credit",
      "taxe", "taxă", "impozit", "anaf", "bursă", "bursa", "bvb", "acțiun", "investiți", "economi",
      "salari", "pensi", "preț", "pret", "buget", "pib", "bancă", "banca", "fisc", "tva", "energie",
      "piață", "piata", "datorie", "deficit", "criz", "scump", "ieftin", "randament", "etf", "imobiliar"]
MAX_ITEMS = 110
MAX_AGE_DAYS = 4

# Categorii (cheie, etichetă, cuvinte) — ordine = prioritate la clasificare
NEWS_CATS = [
    ("crypto", "₿ Criptomonede", ["bitcoin", "crypto", "cripto", "blockchain", "ethereum", "stablecoin", "binance", "solana"]),
    ("taxe", "🧾 Taxe & ANAF", ["taxe", "taxă", "impozit", "anaf", "fiscal", "tva", "declarați", "microîntreprind", "microintreprind", "accize", "contribuți"]),
    ("imobiliare", "🏠 Imobiliare", ["imobiliar", "locuinț", "apartament", "chirie", "construcț", "rezidenț", "metru pătrat", "metru patrat", "teren", "mall", "birouri"]),
    ("bursa", "📈 Bursă & Investiții", ["bursă", "bursa", "bvb", "acțiun", "actiun", "etf", "dividend", "indice", "investiț", "investit", "randament", "broker", "obligațiun", "fond mutual", "ipo", "listare", "tezaur", "fidelis"]),
    ("banci", "🏦 Bănci & Credite", ["bancă", "banca", "bnr", "credit", "dobând", "dobanzi", "ircc", "ipotec", "depozit", "împrumut", "imprumut", "refinanț", "card de credit"]),
    ("companii", "💼 Companii & Afaceri", ["companie", "compania", "afaceri", "antreprenor", "startup", "firma", "firmă", "cifra de afaceri", "profit net", "fuziune", "achiziți", "angajat", "concedier", "fabric", "investiție de"]),
    ("economie", "🌍 Economie & Macro", []),  # catch-all
]

def classify(text):
    t = text.lower()
    for key, _, kws in NEWS_CATS:
        if kws and any(k in t for k in kws):
            return key
    return "economie"

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

JUNK = ("ultimele stiri", "stiri online", "ultimele știri", "știri online")
def sigwords(t):
    return {w for w in re.sub(r"[^a-zăâîșț ]", "", t.lower()).split() if len(w) > 4}

def collect():
    items, seen = [], set()
    now = time.time()
    for name, url, w, need, gnews in SOURCES:
        f = fetch(url)
        if not f or not f.entries:
            print(f"  0  {name}"); continue
        cnt = 0
        for e in f.entries[:PER_SOURCE * 3]:
            title = clean(e.get("title", ""))
            link = e.get("link", "")
            if gnews and " - " in title:           # Google News: scoate " - Sursă"
                title = title.rsplit(" - ", 1)[0].strip()
            if not title or not link or len(title) < 25: continue
            if any(j in title.lower() for j in JUNK): continue
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
                          "summary": summ, "score": score, "_sw": sigwords(title)})
            cnt += 1
            if cnt >= PER_SOURCE: break
        print(f"  {cnt:2}  {name}")
    # boost de cluster: știrea acoperită de mai multe surse = mai importantă
    for a in items:
        cluster = sum(1 for b in items if a is not b and a["source"] != b["source"]
                      and len(a["_sw"] & b["_sw"]) >= 3)
        a["score"] += min(cluster * 0.5, 1.6)
    for a in items:
        a.pop("_sw", None)
    items.sort(key=lambda x: x["score"], reverse=True)
    # diversitate: garantează minim GUARANTEE articole/sursă, apoi umple după scor
    GUARANTEE = 2
    per, chosen, rest = {}, [], []
    for it in items:
        s = it["source"]
        if per.get(s, 0) < GUARANTEE:
            per[s] = per.get(s, 0) + 1; chosen.append(it)
        else:
            rest.append(it)
    chosen += rest[:max(0, MAX_ITEMS - len(chosen))]
    chosen.sort(key=lambda x: x["score"], reverse=True)
    return chosen[:MAX_ITEMS]

FONT = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">'

def build():
    items = collect()
    for it in items:
        it["cat"] = classify(it["title"] + " " + it["summary"])
    today = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    counts = {}
    for it in items:
        counts[it["cat"]] = counts.get(it["cat"], 0) + 1
    n_src = len({it["source"] for it in items})
    tabs = f'<button class="news-tab active" data-f="all">Toate <span>({len(items)})</span></button>'
    for key, label, _ in NEWS_CATS:
        if counts.get(key):
            tabs += f'<button class="news-tab" data-f="{key}">{label} <span>({counts[key]})</span></button>'
    cards = ""
    for it in items:
        t = html.escape(it["title"]); s = html.escape(it["summary"])
        cards += f'''<a class="card reveal news-card" data-cat="{it['cat']}" href="{html.escape(it['link'])}" target="_blank" rel="noopener nofollow">
<div style="display:flex;justify-content:space-between;align-items:center;gap:8px;margin-bottom:8px">
<span class="pill">{html.escape(it['source'])}</span><span style="color:var(--muted);font-size:.8rem">{reltime(it['ts'])}</span></div>
<h3 style="font-size:1.05rem">{t}</h3>{f'<p>{s}</p>' if s else ''}<span class="more">Citește la sursă →</span></a>\n'''
    page = f'''<!DOCTYPE html><html lang="ro"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Știri financiare România — Clubul Financiar</title>
<meta name="description" content="Cele mai importante știri financiare și economice din România, pe categorii (bursă, bănci, taxe, imobiliare, crypto), agregate din zeci de surse și actualizate automat.">
<meta name="robots" content="index, follow"><meta name="theme-color" content="#10b981">
<link rel="canonical" href="https://clubulfinanciar.ro/stiri.html">
<link rel="icon" type="image/png" href="/favicon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website"><meta property="og:site_name" content="Clubul Financiar"><meta property="og:locale" content="ro_RO">
<meta property="og:title" content="Știri financiare România — Clubul Financiar"><meta property="og:description" content="Știri financiare RO pe categorii, din zeci de surse, într-un singur loc."><meta property="og:url" content="https://clubulfinanciar.ro/stiri.html"><meta property="og:image" content="https://clubulfinanciar.ro/og-image.png">
<script>(function(){{var t=localStorage.getItem("cf-theme");if(t)document.documentElement.setAttribute("data-theme",t);}})();</script>
{FONT}
<link rel="stylesheet" href="/assets/style.css?v=10"><link rel="stylesheet" href="/assets/upgrade.css?v=10">
<style>
.news-tabs{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-bottom:30px}}
.news-tab{{font:inherit;font-weight:700;font-size:.85rem;padding:9px 16px;border-radius:999px;border:1px solid var(--border);background:var(--card);color:var(--text);cursor:pointer;transition:.2s}}
.news-tab span{{color:var(--muted);font-weight:600}}
.news-tab:hover{{border-color:var(--emerald)}}
.news-tab.active{{background:var(--grad);border-color:transparent;color:#fff}}
.news-tab.active span{{color:rgba(255,255,255,.85)}}
</style></head><body>
<section class="section-sm" style="background:var(--bg-soft)"><div class="container center">
<p class="eyebrow">Știri · {n_src} surse · actualizat {today}</p><h1 class="title">Știri financiare România</h1>
<p class="lead" style="margin-inline:auto">Cele mai importante știri economice și financiare din România, pe categorii, din zeci de surse, ordonate după relevanță.</p></div></section>
<section class="section"><div class="container">
<div class="news-tabs">{tabs}</div>
<div class="grid grid-3" id="newsGrid">
{cards}
</div>
<p style="color:var(--muted);font-size:.85rem;margin-top:30px;text-align:center">Știrile sunt agregate automat din surse externe (titlu + scurt rezumat + link către sursă). Drepturile aparțin publicațiilor sursă. Actualizat automat la fiecare 30 de minute.</p>
</div></section>
<script>
(function(){{
  var tabs=document.querySelectorAll('.news-tab'), cards=document.querySelectorAll('.news-card');
  tabs.forEach(function(b){{b.addEventListener('click',function(){{
    tabs.forEach(function(x){{x.classList.remove('active')}}); b.classList.add('active');
    var f=b.dataset.f;
    cards.forEach(function(c){{c.style.display=(f==='all'||c.dataset.cat===f)?'':'none';}});
  }});}});
}})();
</script>
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script><script src="/assets/tilt.js?v=10"></script><script src="/assets/site.js?v=10"></script></body></html>'''
    open(os.path.join(ROOT, "docs", "stiri.html"), "w", encoding="utf-8").write(page)
    print(f"stiri.html scris cu {len(items)} știri din {n_src} surse | categorii: {counts}")

if __name__ == "__main__":
    build()
