#!/usr/bin/env python3
"""Știri economice EXTERNE → explainer ORIGINAL în română ("ce înseamnă pentru tine").
NU traduce/republică — comentariu propriu cu LLM (sistemul StockCap), citează sursa + link.
Store rulant: păstrează cele mai importante știri din ultimele ~36h (~30-40), generează doar
explainer-e NOI la fiecare rulare (dedup). Pagina = ca /stiri.html (domenii + interval + sortare).
Rulează: ~/stockmarketcap/stockmarketcap/venv/bin/python news_external.py → docs/stiri-externe.html"""
import os, sys, json, re, html, time, datetime, urllib.request, xml.etree.ElementTree as ET

import urllib.error
CF = os.path.dirname(os.path.abspath(__file__))   # rădăcina repo (merge și local, și în cloud)
sys.path.insert(0, CF); os.chdir(CF)
from _shell import NAV_HTML, FOOTER_HTML
# Chei LLM: LOCAL din .env-ul StockCap; în CLOUD din variabilele de mediu (GitHub Secrets)
try:
    from dotenv import load_dotenv
    _sc = os.path.expanduser("~/stockmarketcap/stockmarketcap/.env")
    if os.path.exists(_sc): load_dotenv(_sc)
except Exception: pass

# ---- LLM self-contained: providri OpenAI-compatibili, fallback peste toți + toate cheile ----
PROVIDERS = [
    # cele mai bune la ROMÂNĂ primele (gemini/mistral), apoi modelele mari, nemotron-nano ultimul
    ("gemini",     "https://generativelanguage.googleapis.com/v1beta/openai", "gemini-2.0-flash",                       "GEMINI_API_KEY"),
    ("mistral",    "https://api.mistral.ai/v1",                        "mistral-small-latest",                           "MISTRAL_API_KEY"),
    ("cerebras",   "https://api.cerebras.ai/v1",                       "gpt-oss-120b",                                   "CEREBRAS_API_KEY"),
    ("deepseek",   "https://api.deepseek.com/v1",                      "deepseek-chat",                                  "DEEPSEEK_API_KEY"),
    ("siliconflow","https://api.siliconflow.cn/v1",                    "deepseek-ai/DeepSeek-V3",                        "SILICONFLOW_API_KEY"),
    ("groq",       "https://api.groq.com/openai/v1",                   "llama-3.3-70b-versatile",                        "GROQ_API_KEY"),
    ("together",   "https://api.together.xyz/v1",                      "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",   "TOGETHER_API_KEY"),
    ("sambanova",  "https://api.sambanova.ai/v1",                      "Meta-Llama-3.3-70B-Instruct",                    "SAMBANOVA_API_KEY"),
    ("nvidia",     "https://integrate.api.nvidia.com/v1",              "meta/llama-3.3-70b-instruct",                    "NVIDIA_API_KEY"),
    ("fireworks",  "https://api.fireworks.ai/inference/v1",            "accounts/fireworks/models/llama-v3p3-70b-instruct", "FIREWORKS_API_KEY"),
    ("openrouter", "https://openrouter.ai/api/v1",                     "nvidia/nemotron-3-nano-30b-a3b:free",            "OPENROUTER_API_KEY"),
]
def _keys(base):
    ks = []
    if os.getenv(base): ks.append(os.getenv(base))
    for i in range(1, 16):
        v = os.getenv(f"{base}_{i}")
        if v: ks.append(v)
    return ks
# Filtru de calitate RO: respinge output cu contaminare engleză/italiană/garbage tipic
_BAD_RE = re.compile(
    r"\b(the|and|with|from|after|before|market|markets|oil|crude|stocks?|shares?|equity|equities|"
    r"tariffs?|vessels?|tankers?|trade|growth|prices?|rising|falling|barrel|yield|bonds?|economy)\b"
    r"|acciun|lanc[eă]az|lancă|vasoare|internazional|prevezi|pre[țt]ele|subire|irachen|"
    r"più|della|degli|nicht|werden|haben|aujourd", re.I)

def is_good_ro(text):
    return not _BAD_RE.search(text or "")

def chat(messages, max_tokens=900, temperature=0.5, accept=None, max_tries=3):
    last = "n/a"; fallback = None; tries = 0
    for name, api_base, model, envb in PROVIDERS:
        for key in _keys(envb):
            try:
                body = json.dumps({"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}).encode()
                req = urllib.request.Request(api_base + "/chat/completions", data=body,
                    headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
                resp = urllib.request.urlopen(req, timeout=30)
                j = json.loads(resp.read())
                content = j["choices"][0]["message"]["content"]
                tries += 1
                if accept and not accept(content):
                    if fallback is None: fallback = content        # prima variantă validă = rezervă
                    last = f"{name} (RO respins)"
                    if tries >= max_tries:                         # nu te învârti la nesfârșit
                        return {"content": fallback, "provider": name + " (fallback)"}
                    continue
                return {"content": content, "provider": name}
            except urllib.error.HTTPError as e:
                last = f"{name} HTTP {e.code}"
            except Exception as e:
                last = f"{name} {e}"
    if fallback is not None:
        return {"content": fallback, "provider": "fallback"}
    raise RuntimeError("toți providerii au eșuat: " + last)

V = "23"
MAX_NEW = 18          # explainer-e noi generate pe rulare (restul vin din store)
KEEP_H = 168          # cât stă o știre în pagină (7 zile)
DISPLAY = 110         # max carduri afișate (o săptămână de știri)
STORE_F = os.path.join(CF, "_external_store.json")
DOCS = os.path.join(CF, "docs")

CATS = [("banci-centrale", "🏦 Bănci centrale"), ("piete", "📈 Piețe & Burse"), ("companii", "🏢 Companii"),
        ("crypto", "₿ Crypto"), ("marfuri", "🛢️ Mărfuri & Energie"), ("macro", "🌍 Macro & Economie")]
CAT_KEYS = {k for k, _ in CATS}; CAT_LABEL = dict(CATS)
CAT_KW = {"banci-centrale": ["fed","ecb","central bank","rate cut","rate hike","interest rate","powell","lagarde","boe","monetary"],
          "crypto": ["bitcoin","crypto","ethereum","btc","blockchain","stablecoin","binance"],
          "marfuri": ["oil","crude","opec","gas","gold","copper","commodity","energy","barrel"],
          "companii": ["earnings","shares","ceo","quarterly","profit","revenue","stock jumps","merger","acquisition"],
          "piete": ["s&p","nasdaq","dow","stocks","markets","index","yield","bond","rally","selloff","wall street"]}

FEEDS = [
    ("BBC Business", "https://feeds.bbci.co.uk/news/business/rss.xml", 1.0),
    ("The Guardian", "https://www.theguardian.com/uk/business/rss", 1.0),
    ("CNBC Economy", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258", 1.1),
    ("CNBC Finance", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664", 1.0),
    ("MarketWatch", "http://feeds.marketwatch.com/marketwatch/topstories/", 1.0),
    ("Reuters", "https://news.google.com/rss/search?q=site:reuters.com%20(economy%20OR%20inflation%20OR%20%22interest%20rate%22%20OR%20markets%20OR%22central%20bank%22)%20when:2d&hl=en-US&gl=US&ceid=US:en", 1.3),
    ("Bloomberg", "https://news.google.com/rss/search?q=site:bloomberg.com%20(economy%20OR%20inflation%20OR%20%22federal%20reserve%22%20OR%20markets%20OR%20ECB)%20when:2d&hl=en-US&gl=US&ceid=US:en", 1.3),
    ("Yahoo Finance", "https://news.google.com/rss/search?q=site:finance.yahoo.com%20(economy%20OR%20stocks%20OR%20inflation%20OR%20fed)%20when:2d&hl=en-US&gl=US&ceid=US:en", 0.9),
    ("Financial Times", "https://news.google.com/rss/search?q=site:ft.com%20(economy%20OR%20markets%20OR%20inflation%20OR%20rates)%20when:2d&hl=en-US&gl=US&ceid=US:en", 1.2),
]
KW = ["fed","federal reserve","ecb","central bank","inflation","interest rate","rate cut","rate hike","recession",
      "gdp","unemployment","jobs","oil","crude","dollar","euro","stock","markets","s&p","nasdaq","dow","bond",
      "yield","tariff","trade","china","crash","rally","earnings","bitcoin","crypto","gold","debt","default","opec"]
UA = {"User-Agent": "Mozilla/5.0 (clubulfinanciar news bot)"}

def fetch(url):
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20).read()
        root = ET.fromstring(raw); out = []
        for it in root.iter("item"):
            t = (it.findtext("title") or "").strip()
            link = (it.findtext("link") or "").strip()
            desc = re.sub("<[^>]+>", "", it.findtext("description") or "").strip()
            pub = it.findtext("pubDate") or ""; ts = 0
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z"):
                try: ts = datetime.datetime.strptime(pub, fmt).timestamp(); break
                except: pass
            if t and link: out.append({"title": t, "link": link, "desc": desc[:600], "ts": ts})
        return out
    except Exception as e:
        print("  fetch fail", url[:48], e); return []

def norm(t): return re.sub(r"[^a-z0-9 ]", "", t.lower())[:60]
def classify(txt):
    txt = txt.lower(); best, bn = "macro", 0
    for k, kws in CAT_KW.items():
        n = sum(1 for w in kws if w in txt)
        if n > bn: best, bn = k, n
    return best

def main():
    store = []
    if os.path.exists(STORE_F):
        try: store = json.load(open(STORE_F))
        except: store = []
    now = time.time()
    store = [s for s in store if s.get("gen_ts", 0) > now - KEEP_H*3600]
    have = {s["url"] for s in store}

    items, seent = [], set()
    for src, url, w in FEEDS:
        got = fetch(url); print(f"  {src}: {len(got)}")
        for it in got:
            txt = (it["title"] + " " + it["desc"]).lower()
            kw = sum(1 for k in KW if k in txt)
            if kw == 0: continue
            age_h = max(0.5, (now - it["ts"]) / 3600) if it["ts"] else 48
            it["score"] = round(w * (1 + 0.25*kw) * (1 / (1 + age_h/24)), 3)
            it["src"] = src; items.append(it)
    items.sort(key=lambda x: -x["score"])

    new = []
    for it in items:
        u = it["link"].split("?")[0]; k = norm(it["title"])
        if u in have or k in seent: continue
        seent.add(k); new.append(it)
        if len(new) >= MAX_NEW: break
    print(f"noi de generat: {len(new)} | în store: {len(store)}")

    for it in new:
        prompt = (
            "Ești redactor senior la Clubul Financiar (educație financiară, România). "
            "Primești o știre economică internațională în engleză. Scrie un rezumat ORIGINAL în ROMÂNĂ — NU traduce cuvânt cu cuvânt, NU copia.\n\n"
            "REGULI DE LIMBĂ (obligatorii, altfel răspunsul e respins):\n"
            "- Română corectă, naturală, fluentă. ZERO cuvinte din alte limbi (engleză, italiană, germană, franceză). Diacritice corecte.\n"
            "- Termeni financiari CORECȚI: oil / crude oil = «țiței» (sau «petrol»), NICIODATĂ «ulei»; barrel = baril; yield = randament; "
            "shares / stocks / equities = acțiuni; bonds = obligațiuni; bear market = piață în scădere; rally / surge = creștere puternică; "
            "Fed = Rezerva Federală; ECB = BCE; tariffs = tarife / taxe vamale; vessels / tankers = nave / petroliere.\n"
            "- Verifică numele proprii (țări, companii, persoane): ex. Iran ≠ Irak, Hong Kong, OMV Petrom.\n"
            "- Dacă nu ești sigur de un termen, folosește un cuvânt simplu românesc. Recitește mental: să sune ca scris de un român, nu tradus automat.\n\n"
            "Răspunde DOAR cu JSON valid pe o linie:\n"
            '{"titlu":"titlu clar în română corectă, reformulat","fapt":"1-2 propoziții neutre cu faptul principal",'
            '"ce_inseamna":"2-4 propoziții: ce înseamnă pentru banii unui român (rată, economii, prețuri, leu, job, investiții). Concret, fără jargon.",'
            '"categorie":"una din: banci-centrale, piete, companii, crypto, marfuri, macro"}\n\n'
            f"ȘTIRE — TITLU: {it['title']}\nREZUMAT: {it['desc']}\nSURSĂ: {it['src']}"
        )
        try:
            r = chat([{"role": "user", "content": prompt}], max_tokens=900, temperature=0.5, accept=is_good_ro)
            c = r.get("content", "").strip(); m = re.search(r"\{.*\}", c, re.S)
            d = json.loads(re.sub(r"[\x00-\x1f]", " ", m.group(0) if m else c))
            cat = d.get("categorie", "").strip()
            if cat not in CAT_KEYS: cat = classify(it["title"] + " " + it["desc"])
            store.append({"url": it["link"].split("?")[0], "link": it["link"], "src": it["src"],
                          "ts": it["ts"], "gen_ts": now, "score": it["score"], "cat": cat,
                          "titlu": d["titlu"].strip(), "fapt": d["fapt"].strip(), "ce_inseamna": d["ce_inseamna"].strip()})
        except Exception as e:
            print("  LLM skip:", it["title"][:40], e); continue

    store.sort(key=lambda s: -s.get("score", 0))
    disp = store[:DISPLAY]
    counts = {k: sum(1 for s in disp if s["cat"] == k) for k, _ in CATS}

    cards = []
    for s in disp:
        when = ""
        ref = s["ts"] or s["gen_ts"]
        dh = (now - ref) / 3600
        when = f"acum {int(dh)}h" if dh < 24 else f"acum {int(dh/24)}z"
        cards.append(f'''<article class="card news-card reveal" data-cat="{s['cat']}" data-ts="{s['ts'] or s['gen_ts']:.0f}" data-score="{s.get('score',0)}">
<div class="ne-top"><span class="ne-src">🌍 {html.escape(s['src'])} · {CAT_LABEL[s['cat']]}</span><span class="ne-when">{when}</span></div>
<h2>{html.escape(s['titlu'])}</h2>
<p class="ne-fapt">{html.escape(s['fapt'])} <a class="ne-link" href="{html.escape(s['link'])}" target="_blank" rel="noopener nofollow">Sursă: {html.escape(s['src'])} →</a></p>
<div class="ne-cti"><strong>💡 Ce înseamnă pentru tine:</strong> {html.escape(s['ce_inseamna'])}</div>
</article>''')

    tabs = f'<button class="news-tab active" data-f="all">Toate <span>({len(disp)})</span></button>'
    for k, label in CATS:
        if counts[k]: tabs += f'<button class="news-tab" data-f="{k}">{label} <span>({counts[k]})</span></button>'
    today = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")

    page = f'''<!DOCTYPE html><html lang="ro"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Știri economice externe — ce înseamnă pentru tine | Clubul Financiar</title>
<meta name="description" content="Cele mai importante știri economice mondiale, explicate pe înțelesul tău: ce înseamnă fiecare pentru banii, rata și economiile tale. Surse citate.">
<meta name="robots" content="index, follow"><meta name="theme-color" content="#0f2540">
<link rel="canonical" href="https://clubulfinanciar.ro/stiri-externe.html"><link rel="icon" type="image/png" href="/favicon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website"><meta property="og:site_name" content="Clubul Financiar"><meta property="og:locale" content="ro_RO"><meta property="og:title" content="Știri economice externe — ce înseamnă pentru tine"><meta property="og:description" content="Știri economice mondiale explicate pentru banii tăi."><meta property="og:url" content="https://clubulfinanciar.ro/stiri-externe.html"><meta property="og:image" content="https://clubulfinanciar.ro/og-image.jpg">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="Știri economice externe — ce înseamnă pentru tine"><meta name="twitter:image" content="https://clubulfinanciar.ro/og-image.jpg">
<script>(function(){{var t=localStorage.getItem("cf-theme");if(t)document.documentElement.setAttribute("data-theme",t);}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400..800&family=Sora:wght@600;700;800&family=Fraunces:opsz,ital,wght@9..144,0,400;9..144,0,600;9..144,1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v={V}"><link rel="stylesheet" href="/assets/upgrade.css?v={V}"><link rel="stylesheet" href="/assets/cf-ultra.css?v=1"><link rel="stylesheet" href="/assets/cf-preview.css?v=1">
<style>
/* premium auriu pe pagina de stiri (remap tokeni pe .u-page) */
.u-page{{--emerald:var(--u-gold);--emerald-link:var(--u-gold);--grad:linear-gradient(135deg,var(--u-gold),var(--u-gold2));--card:var(--u-panel);--border:var(--u-line-soft);--bg-soft:var(--u-panel2);--bg-soft2:var(--u-panel2);--text:var(--u-ink);--muted:var(--u-muted)}}
.u-page .news-tab.active{{color:#1a1304}}
.u-page .ne-cti{{border-left-color:var(--u-gold)}}
.u-page .title{{font-family:'Fraunces',serif;font-weight:600}}
.u-page .eyebrow{{color:var(--u-gold)}}
.news-tabs{{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-bottom:30px}}
.news-tab{{font:inherit;font-weight:700;font-size:.85rem;padding:9px 16px;border-radius:999px;border:1px solid var(--border);background:var(--card);color:var(--text);cursor:pointer;transition:.2s}}
.news-tab span{{color:var(--muted);font-weight:600}}.news-tab:hover{{border-color:var(--emerald)}}
.news-tab.active{{background:var(--grad);border-color:transparent;color:#fff}}.news-tab.active span{{color:rgba(255,255,255,.85)}}
.news-controls{{display:flex;flex-wrap:wrap;gap:20px;justify-content:center;margin-bottom:34px}}
.news-grp{{display:flex;flex-wrap:wrap;gap:8px;align-items:center}}
.news-lbl{{color:var(--muted);font-size:.8rem;font-weight:800;text-transform:uppercase;letter-spacing:.08em}}
.news-ext,.news-card{{padding:22px}}.ne-top{{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:8px}}
.ne-src{{font-size:.74rem;font-weight:800;color:var(--emerald-link);text-transform:uppercase;letter-spacing:.04em}}.ne-when{{font-size:.78rem;color:var(--muted);white-space:nowrap}}
.news-card h2{{font-size:1.18rem;margin:2px 0 10px;line-height:1.3}}.ne-fapt{{color:var(--muted);font-size:.94rem;margin:0 0 12px}}.ne-link{{color:var(--emerald-link);font-weight:700;white-space:nowrap}}
.ne-cti{{background:var(--bg-soft);border-left:4px solid var(--emerald);border-radius:10px;padding:13px 15px;font-size:.93rem}}
</style></head><body>{NAV_HTML}<main class="u-page">
<section class="section-sm" style="background:var(--bg-soft)"><div class="container center">
<p class="eyebrow">Știri externe · actualizat {today}</p><h1 class="title">Economia lumii, pe înțelesul tău</h1>
<p class="lead" style="margin-inline:auto">Cele mai importante știri economice mondiale, explicate simplu: <strong>ce înseamnă fiecare pentru banii tăi</strong>. Comentariu original, cu sursa citată.</p>
<div class="news-tabs" style="justify-content:center;margin-top:14px"><a class="news-tab" href="/stiri.html">🇷🇴 Știri România</a><a class="news-tab active" href="/stiri-externe.html"><span>🌍 Știri externe</span></a></div></div></section>
<section class="section"><div class="container">
<div class="news-controls">
<div class="news-grp"><span class="news-lbl">Interval</span>
<button class="news-tab nt-range active" data-range="all">Toate</button>
<button class="news-tab nt-range" data-range="24h">Ultimele 24h</button>
<button class="news-tab nt-range" data-range="7d">Ultima săptămână</button></div>
<div class="news-grp"><span class="news-lbl">Sortare</span>
<button class="news-tab nt-sort active" data-sort="recent">Cele mai recente</button>
<button class="news-tab nt-sort" data-sort="relevant">Cele mai relevante</button></div>
</div>
<div class="news-tabs" id="catTabs">{tabs}</div>
<p id="newsEmpty" class="lead" hidden style="text-align:center;margin:14px auto">Nicio știre în acest interval.</p>
<div class="grid grid-3" id="newsGrid">
{"".join(cards)}
</div>
<p style="color:var(--muted);font-size:.85rem;margin-top:30px;text-align:center">Analize originale Clubul Financiar pe baza știrilor din surse externe (citate + link). Faptele aparțin publicațiilor sursă; interpretarea „ce înseamnă pentru tine" e a noastră. Caracter educativ, nu sfat de investiții.</p>
</div></section></main>
{FOOTER_HTML}
<script>
(function(){{
  var grid=document.getElementById('newsGrid');
  var cards=[].slice.call(document.querySelectorAll('.news-card'));
  var st={{cat:'all',range:'all',sort:'recent'}};
  var now=Date.now()/1000;
  function inRange(ts){{ if(st.range==='all')return true; var d=now-ts; return st.range==='24h'?d<=86400:d<=604800; }}
  function apply(){{
    var vis=cards.filter(function(c){{
      var okCat=(st.cat==='all'||c.dataset.cat===st.cat);
      var okR=inRange(parseFloat(c.dataset.ts)||0);
      c.style.display=(okCat&&okR)?'':'none'; return okCat&&okR;
    }});
    vis.sort(function(a,b){{
      if(st.sort==='recent') return (parseFloat(b.dataset.ts)||0)-(parseFloat(a.dataset.ts)||0);
      return (parseFloat(b.dataset.score)||0)-(parseFloat(a.dataset.score)||0);
    }});
    vis.forEach(function(c){{ grid.appendChild(c); }});
    var e=document.getElementById('newsEmpty'); if(e) e.hidden=(vis.length>0);
  }}
  function wire(sel,key){{ document.querySelectorAll(sel).forEach(function(b){{ b.addEventListener('click',function(){{
    document.querySelectorAll(sel).forEach(function(x){{x.classList.remove('active')}}); b.classList.add('active');
    st[key]=b.dataset[key]; apply();
  }}); }}); }}
  wire('.nt-range','range'); wire('.nt-sort','sort');
  document.querySelectorAll('#catTabs .news-tab[data-f]').forEach(function(b){{ b.addEventListener('click',function(){{
    document.querySelectorAll('#catTabs .news-tab[data-f]').forEach(function(x){{x.classList.remove('active')}}); b.classList.add('active');
    st.cat=b.dataset.f; apply();
  }}); }});
  apply();
}})();
</script>
<script defer src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script><script defer src="/assets/tilt.js?v={V}"></script><script defer src="/assets/site.js?v={V}"></script></body></html>'''
    open(os.path.join(DOCS, "stiri-externe.html"), "w", encoding="utf-8").write(page)
    json.dump(store, open(STORE_F, "w"), ensure_ascii=False)
    # feed compact pentru Terminal (știri inline, refolosește același store)
    news_top = [{"titlu": s.get("titlu", ""), "fapt": s.get("fapt", ""), "src": s.get("src", ""),
                 "cat": s.get("cat", ""), "link": s.get("link") or s.get("url", "")} for s in disp[:15]]
    os.makedirs(os.path.join(DOCS, "data"), exist_ok=True)
    json.dump({"updated": time.strftime("%Y-%m-%d %H:%M", time.gmtime()), "items": news_top},
              open(os.path.join(DOCS, "data", "news.json"), "w"), ensure_ascii=False)
    print(f"✅ stiri-externe.html: {len(disp)} afișate ({len(new)} noi generate azi)")

if __name__ == "__main__":
    main()
