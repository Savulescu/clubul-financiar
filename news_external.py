#!/usr/bin/env python3
"""Știri economice EXTERNE → explainer ORIGINAL în română ("ce înseamnă pentru tine").
NU traduce/republică — generează comentariu propriu cu LLM (sistemul StockCap), citează sursa + link.
Rulează cu venvul StockCap: ~/stockmarketcap/stockmarketcap/venv/bin/python news_external.py
Scrie docs/stiri-externe.html."""
import os, sys, json, re, html, time, datetime, urllib.request, xml.etree.ElementTree as ET

CF = os.path.expanduser("~/clubul-financiar")
SC = os.path.expanduser("~/stockmarketcap/stockmarketcap")
sys.path.insert(0, CF); sys.path.insert(0, SC)
os.chdir(CF)
from _shell import NAV_HTML, FOOTER_HTML
try:
    from dotenv import load_dotenv; load_dotenv(os.path.join(SC, ".env"))
except Exception as e: print("dotenv:", e)
from backend.llm_router import chat

V = "23"; N = 8
DOCS = os.path.join(CF, "docs"); SEEN_F = os.path.join(CF, "_external_seen.json")

# surse economice mondiale (RSS direct + Google News pt Reuters/Bloomberg fără RSS public)
FEEDS = [
    ("BBC Business", "https://feeds.bbci.co.uk/news/business/rss.xml", 1.0),
    ("The Guardian", "https://www.theguardian.com/uk/business/rss", 1.0),
    ("CNBC Economy", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258", 1.1),
    ("CNBC Finance", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664", 1.0),
    ("MarketWatch", "http://feeds.marketwatch.com/marketwatch/topstories/", 1.0),
    ("Reuters", "https://news.google.com/rss/search?q=site:reuters.com%20(economy%20OR%20inflation%20OR%20%22interest%20rate%22%20OR%20markets%20OR%22central%20bank%22)%20when:2d&hl=en-US&gl=US&ceid=US:en", 1.3),
    ("Bloomberg", "https://news.google.com/rss/search?q=site:bloomberg.com%20(economy%20OR%20inflation%20OR%20%22federal%20reserve%22%20OR%20markets%20OR%20ECB)%20when:2d&hl=en-US&gl=US&ceid=US:en", 1.3),
    ("Yahoo Finance", "https://news.google.com/rss/search?q=site:finance.yahoo.com%20(economy%20OR%20stocks%20OR%20inflation%20OR%20fed)%20when:2d&hl=en-US&gl=US&ceid=US:en", 0.9),
]
KW = ["fed","federal reserve","ecb","central bank","inflation","interest rate","rate cut","rate hike","recession",
      "gdp","unemployment","jobs","oil","crude","dollar","euro","stock","markets","s&p","nasdaq","dow","bond",
      "yield","tariff","trade","china","crash","rally","earnings","bitcoin","crypto","gold","debt","default"]
UA = {"User-Agent": "Mozilla/5.0 (clubulfinanciar news bot)"}

def fetch(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        raw = urllib.request.urlopen(req, timeout=20).read()
        root = ET.fromstring(raw)
        out = []
        for it in root.iter("item"):
            t = (it.findtext("title") or "").strip()
            link = (it.findtext("link") or "").strip()
            desc = re.sub("<[^>]+>", "", it.findtext("description") or "").strip()
            pub = it.findtext("pubDate") or ""
            ts = 0
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z"):
                try: ts = datetime.datetime.strptime(pub, fmt).timestamp(); break
                except: pass
            if t and link: out.append({"title": t, "link": link, "desc": desc[:600], "ts": ts})
        return out
    except Exception as e:
        print("  fetch fail", url[:50], e); return []

def norm(t): return re.sub(r"[^a-z0-9 ]", "", t.lower())[:60]

def main():
    seen = {}
    if os.path.exists(SEEN_F):
        try: seen = json.load(open(SEEN_F))
        except: seen = {}
    cutoff = time.time() - 14*86400
    seen = {k: v for k, v in seen.items() if v > cutoff}

    items = []
    now = time.time()
    for src, url, w in FEEDS:
        got = fetch(url)
        print(f"  {src}: {len(got)}")
        for it in got:
            it["src"] = src; it["w"] = w
            txt = (it["title"] + " " + it["desc"]).lower()
            kw = sum(1 for k in KW if k in txt)
            age_h = max(0.5, (now - it["ts"]) / 3600) if it["ts"] else 48
            it["score"] = w * (1 + 0.25*kw) * (1 / (1 + age_h/24))
            items.append(it)

    # dedup (titlu normalizat) + scoate ce-am explicat deja
    items.sort(key=lambda x: -x["score"])
    picked, seent = [], set()
    for it in items:
        k = norm(it["title"])
        if not k or k in seent: continue
        # cheie unică (link sau titlu) — sari peste cele deja explicate
        key = it["link"].split("?")[0]
        if key in seen: continue
        seent.add(k); picked.append(it)
        if len(picked) >= N: break
    print(f"selectate: {len(picked)} (din {len(items)})")

    cards = []
    for it in picked:
        prompt = (
            "Ești redactor la Clubul Financiar, site de educație financiară din România. "
            "Primești o știre economică internațională (în engleză). Scrie în ROMÂNĂ, conținut ORIGINAL — "
            "NU traduce și NU copia textul sursei. Răspunde DOAR cu JSON valid:\n"
            '{"titlu":"titlu nou clar în română, reformulat (nu tradus cuvânt cu cuvânt)",'
            '"fapt":"1-2 propoziții neutre cu faptul principal",'
            '"ce_inseamna":"2-4 propoziții: Ce înseamnă pentru tine — leagă faptul de banii unui român obișnuit '
            '(rată la credit, economii, prețuri, leu, job, investiții). Concret, util, fără jargon."}\n\n'
            f"ȘTIRE — TITLU: {it['title']}\nREZUMAT: {it['desc']}\nSURSĂ: {it['src']}"
        )
        try:
            r = chat([{"role": "user", "content": prompt}], tier="fast", json_mode=True, max_tokens=900, temperature=0.5)
            c = r.get("content", "").strip()
            m = re.search(r"\{.*\}", c, re.S)
            raw = re.sub(r"[\x00-\x1f]", " ", m.group(0) if m else c)  # scoate newline-uri brute din stringuri
            d = json.loads(raw)
            titlu = html.escape(d["titlu"].strip()); fapt = html.escape(d["fapt"].strip())
            cti = html.escape(d["ce_inseamna"].strip())
        except Exception as e:
            print("  LLM skip:", it["title"][:40], e); continue
        when = ""
        if it["ts"]:
            dh = (now - it["ts"]) / 3600
            when = f"acum {int(dh)}h" if dh < 24 else f"acum {int(dh/24)}z"
        cards.append(f'''<article class="card news-ext reveal">
<div class="ne-top"><span class="ne-src">🌍 {html.escape(it['src'])}</span>{f'<span class="ne-when">{when}</span>' if when else ''}</div>
<h2>{titlu}</h2>
<p class="ne-fapt">{fapt} <a class="ne-link" href="{html.escape(it['link'])}" target="_blank" rel="noopener nofollow">Sursă: {html.escape(it['src'])} →</a></p>
<div class="ne-cti"><strong>💡 Ce înseamnă pentru tine:</strong> {cti}</div>
</article>''')
        seen[it["link"].split("?")[0]] = now

    if not cards:
        print("0 carduri generate — nu suprascriu pagina."); return
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    page = f'''<!DOCTYPE html><html lang="ro"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Știri economice externe — ce înseamnă pentru tine | Clubul Financiar</title>
<meta name="description" content="Cele mai importante știri economice mondiale, explicate pe înțelesul tău: ce înseamnă fiecare pentru banii, rata și economiile tale. Surse citate.">
<meta name="robots" content="index, follow"><meta name="theme-color" content="#10b981">
<link rel="canonical" href="https://clubulfinanciar.ro/stiri-externe.html"><link rel="icon" type="image/png" href="/favicon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website"><meta property="og:site_name" content="Clubul Financiar"><meta property="og:locale" content="ro_RO"><meta property="og:title" content="Știri economice externe — ce înseamnă pentru tine"><meta property="og:description" content="Știri economice mondiale explicate pentru banii tăi."><meta property="og:url" content="https://clubulfinanciar.ro/stiri-externe.html"><meta property="og:image" content="https://clubulfinanciar.ro/og-image.jpg">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="Știri economice externe — ce înseamnă pentru tine"><meta name="twitter:image" content="https://clubulfinanciar.ro/og-image.jpg">
<script>(function(){{var t=localStorage.getItem("cf-theme");if(t)document.documentElement.setAttribute("data-theme",t);}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400..800&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v={V}"><link rel="stylesheet" href="/assets/upgrade.css?v={V}">
<style>.news-ext{{padding:22px}}.ne-top{{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}}.ne-src{{font-size:.78rem;font-weight:800;color:var(--emerald-link);text-transform:uppercase;letter-spacing:.05em}}.ne-when{{font-size:.78rem;color:var(--muted)}}.news-ext h2{{font-size:1.2rem;margin:2px 0 10px;line-height:1.3}}.ne-fapt{{color:var(--muted);font-size:.95rem;margin:0 0 12px}}.ne-link{{color:var(--emerald-link);font-weight:700;white-space:nowrap}}.ne-cti{{background:var(--bg-soft);border-left:4px solid var(--emerald);border-radius:10px;padding:14px 16px;font-size:.95rem}}</style></head><body>{NAV_HTML}
<section class="section-sm" style="background:var(--bg-soft)"><div class="container center">
<p class="eyebrow">Știri externe · actualizat {today}</p><h1 class="title">Economia lumii, pe înțelesul tău</h1>
<p class="lead" style="margin-inline:auto">Cele mai importante știri economice mondiale, explicate simplu: <strong>ce înseamnă fiecare pentru banii tăi</strong>. Comentariu original, cu sursa citată.</p>
<div class="news-tabs" style="justify-content:center;margin-top:18px"><a class="news-tab" href="/stiri.html">🇷🇴 Știri România</a><a class="news-tab active" href="/stiri-externe.html"><span>🌍 Știri externe</span></a></div></div></section>
<section class="section"><div class="container"><div class="grid grid-2">
{"".join(cards)}
</div>
<p style="color:var(--muted);font-size:.85rem;margin-top:30px;text-align:center">Analize originale Clubul Financiar pe baza știrilor din surse externe (citate + link). Faptele aparțin publicațiilor sursă; interpretarea „ce înseamnă pentru tine" e a noastră. Caracter educativ, nu sfat de investiții.</p>
</div></section>
{FOOTER_HTML}
<script defer src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script><script defer src="/assets/tilt.js?v={V}"></script><script defer src="/assets/site.js?v={V}"></script></body></html>'''
    open(os.path.join(DOCS, "stiri-externe.html"), "w", encoding="utf-8").write(page)
    json.dump(seen, open(SEEN_F, "w"))
    print(f"✅ stiri-externe.html scris cu {len(cards)} explainer-e")

if __name__ == "__main__":
    main()
