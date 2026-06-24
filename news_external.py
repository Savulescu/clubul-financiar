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
# Filtru de calitate RO: respinge output cu contaminare engleză/altă limbă/garbage tipic.
# Co-proiectat pe garbage-ul REAL găsit în store (ulei, bonduri, possibiliți, publicăză,
# să-l pășiți, econometrice, trimestrene) + asigură că exemplele BUNE trec (vezi _selftest).
_BAD_RE = re.compile(
    # 1) cuvinte engleze lăsate netraduse
    r"\b(the|and|with|from|after|before|market|markets|oil|crude|stocks?|shares?|equity|equities|"
    r"tariffs?|vessels?|tankers?|trade|growth|prices?|rising|falling|barrel|yield|bonds?|economy|"
    r"bear market|bull market|stock|earnings|revenue|federal reserve)\b"
    # 2) mistranslări tipice / termeni greșiți (oil→ulei, bonds→bonduri)
    r"|\bulei(ul|uri)?\b|\bbondu(ri|l|rile)?\b"
    # 3) garbage / conjugări inexistente / alte limbi
    r"|possibil|publicăz|publicaz[ăa]|econometr|trimestren|p[ăa]șiț|pasiț|vasoare|"
    r"acciun|lanc[eă]az|lancă|internazional|prevezi|pre[țt]ele|subire|irachen|"
    r"più|della|degli|nicht|werden|haben|aujourd", re.I)

def is_good_ro(text):
    return not _BAD_RE.search(text or "")

def _selftest_filter():
    """Co-design: garbage-ul real TREBUIE respins, exemplele bune TREBUIE acceptate."""
    bad = ["se apropie de un bear market", "Bondurile arse de schimbarea politicii Fed... uleiul",
           "possibiliți schimbări ale ratelor", "Un stock de energie puțin cunoscut",
           "publicăză rapoartele trimestrene", "ar putea să-l pășiți", "economii de econometrice"]
    good = ["Rezerva Federală a redus dobânda de referință cu 0,25 puncte procentuale.",
            "Prețul țițeiului a crescut după decizia OPEC, ceea ce împinge inflația în sus.",
            "Bursele europene au scăzut, afectând randamentul fondurilor de pensii.",
            "Obligațiunile de stat oferă un randament mai sigur pentru economiile tale."]
    bf = [t for t in bad if is_good_ro(t)]      # garbage care a trecut greșit
    gf = [t for t in good if not is_good_ro(t)]  # bun respins greșit
    return bf, gf

_DIAG = {"ok": {}, "err": {}, "ro_reject": {}, "samples": [], "no_keys": []}   # telemetrie cloud → docs/data/news_debug.json
_DEADLINE = 0.0   # buget global de timp (setat în main); după el, chat() iese pe fallback rapid

def chat(messages, max_tokens=900, temperature=0.5, accept=None, max_tries=3, max_attempts=40):
    last = "n/a"; fallback = None; tries = 0; attempts = 0
    if _DEADLINE and time.time() > _DEADLINE:
        raise RuntimeError("buget de timp depășit — fallback rapid pe restul")
    for name, api_base, model, envb in PROVIDERS:
        ks = _keys(envb)
        if not ks and name not in _DIAG["no_keys"]: _DIAG["no_keys"].append(name)
        for key in ks:
            if attempts >= max_attempts or (_DEADLINE and time.time() > _DEADLINE): break
            attempts += 1
            try:
                body = json.dumps({"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}).encode()
                req = urllib.request.Request(api_base + "/chat/completions", data=body,
                    headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
                resp = urllib.request.urlopen(req, timeout=10)   # era 30 — cheile moarte care fac hang opreau rularea ~25 min
                j = json.loads(resp.read())
                content = j["choices"][0]["message"]["content"]
                tries += 1
                if len(_DIAG["samples"]) < 6: _DIAG["samples"].append({"p": name, "raw": (content or "")[:200]})
                if accept and not accept(content):
                    if fallback is None: fallback = content        # prima variantă validă = rezervă
                    last = f"{name} (RO respins)"
                    _DIAG["ro_reject"][name] = _DIAG["ro_reject"].get(name, 0) + 1
                    if tries >= max_tries:                         # nu te învârti la nesfârșit
                        return {"content": fallback, "provider": name + " (fallback)"}
                    continue
                _DIAG["ok"][name] = _DIAG["ok"].get(name, 0) + 1
                return {"content": content, "provider": name}
            except urllib.error.HTTPError as e:
                last = f"{name} HTTP {e.code}"; _DIAG["err"][f"{name}:{e.code}"] = _DIAG["err"].get(f"{name}:{e.code}", 0) + 1
                if e.code in (401, 403, 404):
                    break   # cheie/provider inutilizabil → sari TOATE cheile lui (nu mânca bugetul de încercări)
            except Exception as e:
                last = f"{name} {e}"; k = f"{name}:{type(e).__name__}"; _DIAG["err"][k] = _DIAG["err"].get(k, 0) + 1
    if fallback is not None:
        return {"content": fallback, "provider": "fallback"}
    raise RuntimeError("toți providerii au eșuat: " + last)

V = "23"
MAX_NEW = 24          # explainer-e noi pe rulare (mărit de la 18: rulările sunt rare din cauza throttle-ului GitHub, deci prindem mai multe știri/rulare = acoperire mai bună)
KEEP_H = 336          # cât stă o știre în pagină (7 zile)
DISPLAY = 400         # max carduri afișate (o săptămână de știri)
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
            if pub:
                try:
                    from email.utils import parsedate_to_datetime
                    ts = parsedate_to_datetime(pub).timestamp()   # RFC822 robust (incl. GMT/zone)
                except Exception:
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

# Notă RO generică pe categorie — fallback de ULTIMĂ instanță (doar dacă nici traducerea simplă nu reușește).
FB_NOTE = {
    "banci-centrale": "Deciziile băncilor centrale (Fed, BCE, BNR) influențează dobânzile la credite, depozite și cursul leului.",
    "piete": "Mișcările piețelor se reflectă în randamentele investițiilor, fondurilor de pensii și ETF-urilor.",
    "companii": "Rezultatele marilor companii pot mișca bursa și valoarea acțiunilor sau fondurilor deținute.",
    "crypto": "Volatilitatea crypto e mare — relevantă doar pentru partea de portofoliu pe care ți-o permiți să o riști.",
    "marfuri": "Prețurile materiilor prime (țiței, gaz, aur) se simt în facturi, la pompă și în inflație.",
    "macro": "Indicatorii macro (inflație, șomaj, PIB) arată încotro merg prețurile, dobânzile și puterea ta de cumpărare.",
}

def _base(it, now):
    return {"url": it["link"].split("?")[0], "link": it["link"], "src": it["src"],
            "ts": it["ts"], "gen_ts": now, "score": it["score"]}

def _parse_json(c):
    m = re.search(r"\{.*\}", c, re.S)
    return json.loads(re.sub(r"[\x00-\x1f]", " ", m.group(0) if m else c))

def _ro_penalty(text):
    """Cât de «ne-românesc» e textul: cuvinte engleze/garbage + (mare) dacă n-are diacritice.
    0 = română curată. Folosit ca RANG de calitate, nu ca poartă spre engleză."""
    t = text or ""
    hits = len(_BAD_RE.findall(t))
    has_diac = bool(re.search(r"[ăâîșțĂÂÎȘȚ]", t))
    return hits + (0 if has_diac else 5)   # fără diacritice = aproape sigur netradus

def make_record(it, now):
    """Întoarce CEL MAI BUN record ROMÂNESC disponibil. Filtrul de calitate e RANG, nu poartă
    spre engleză: o română cu o mică scăpare e tot mai bună decât engleza brută. Engleză (None)
    DOAR dacă niciun provider nu produce ceva românesc. Fără latch global — fiecare știre încearcă
    independent (un eșec tranzitoriu nu mai aruncă restul rulării pe engleză)."""
    cands = []  # (penalty, record)
    # ── Treapta 1: explainer complet (titlu + fapt + ce înseamnă) ──
    p1 = (
        "Ești redactor senior la Clubul Financiar (educație financiară, România). "
        "Primești o știre economică internațională în engleză. Scrie un rezumat ORIGINAL în ROMÂNĂ — NU traduce cuvânt cu cuvânt.\n\n"
        "REGULI DE LIMBĂ (obligatorii):\n"
        "- Română corectă, naturală. ZERO cuvinte din alte limbi. Diacritice corecte.\n"
        "- Termeni CORECȚI: oil/crude = «țiței» (NICIODATĂ «ulei»); barrel=baril; yield=randament; "
        "shares/stocks/equities=acțiuni; bonds=obligațiuni (NU «bonduri»); bear market=piață în scădere; "
        "rally/surge=creștere puternică; Fed=Rezerva Federală; ECB=BCE; tariffs=tarife/taxe vamale; vessels/tankers=nave/petroliere.\n"
        "- Verifică numele proprii (Iran ≠ Irak etc.).\n\n"
        "Răspunde DOAR cu JSON valid pe o linie:\n"
        '{"titlu":"titlu clar în română, reformulat","fapt":"1-2 propoziții neutre cu faptul principal",'
        '"ce_inseamna":"2-4 propoziții: ce înseamnă pentru banii unui român (rată, economii, prețuri, leu, job, investiții). Concret.",'
        '"categorie":"una din: banci-centrale, piete, companii, crypto, marfuri, macro"}\n\n'
        f"ȘTIRE — TITLU: {it['title']}\nREZUMAT: {it['desc']}\nSURSĂ: {it['src']}"
    )
    try:
        r = chat([{"role": "user", "content": p1}], max_tokens=900, temperature=0.5, accept=is_good_ro)
        d = _parse_json(r.get("content", "").strip())
        titlu, fapt, ce = d["titlu"].strip(), d["fapt"].strip(), d["ce_inseamna"].strip()
        cat = d.get("categorie", "").strip()
        if cat not in CAT_KEYS: cat = classify(it["title"] + " " + it["desc"])
        if titlu and len(ce) > 20:
            pen = _ro_penalty(titlu + " " + fapt + " " + ce)
            cands.append((pen, {**_base(it, now), "cat": cat, "titlu": titlu, "fapt": fapt, "ce_inseamna": ce}))
            if pen == 0:
                return cands[0][1]   # română curată — gata
    except Exception as e:
        print("  treapta1 fail:", it["title"][:40], str(e)[:50])
    # ── Treapta 2: traducere simplă (reușește des când explainerul complex nu) ──
    p2 = ("Tradu în română naturală și corectă (oil=țiței NU ulei, bonds=obligațiuni, stocks/shares=acțiuni, "
          "yield=randament, Fed=Rezerva Federală). Răspunde DOAR JSON pe o linie: "
          '{"titlu":"titlul tradus","fapt":"o propoziție cu faptul principal"}\n\n'
          f"TITLU: {it['title']}\nREZUMAT: {it['desc'][:300]}")
    try:
        r = chat([{"role": "user", "content": p2}], max_tokens=400, temperature=0.3, accept=is_good_ro)
        d = _parse_json(r.get("content", "").strip())
        titlu, fapt = d.get("titlu", "").strip(), d.get("fapt", "").strip()
        cat = classify(it["title"] + " " + it["desc"])
        if titlu:
            pen = _ro_penalty(titlu + " " + fapt)
            cands.append((pen, {**_base(it, now), "cat": cat, "titlu": titlu, "fapt": fapt or titlu,
                                "ce_inseamna": FB_NOTE.get(cat, FB_NOTE["macro"]), "tier2": 1}))
    except Exception as e:
        print("  treapta2 fail:", it["title"][:40], str(e)[:50])
    if cands:
        cands.sort(key=lambda x: x[0])
        pen, best = cands[0]
        if pen < 5:          # are diacritice / e românesc → mai bun decât engleza brută
            return best
    return None              # nimic românesc → engleză brută badge-uită

def make_fallback(it, now):
    """Ultimă instanță: păstrăm faptul în engleză (badge «rezumat în engleză») + notă RO pe categorie."""
    cat = classify(it["title"] + " " + it["desc"])
    fapt = re.sub(r"\s+", " ", it.get("desc", "")).strip()[:240] or it["title"].strip()
    return {**_base(it, now), "cat": cat, "fb": 1,
            "titlu": it["title"].strip(), "fapt": fapt, "ce_inseamna": FB_NOTE.get(cat, FB_NOTE["macro"])}

def main():
    store = []
    if os.path.exists(STORE_F):
        try: store = json.load(open(STORE_F))
        except: store = []
    now = time.time()
    global _DEADLINE
    _DEADLINE = now + 300   # buget total ~5 min (fetch + LLM); după el, restul știrilor → fallback rapid
    store = [s for s in store if s.get("gen_ts", 0) > now - KEEP_H*3600]
    new = []
    if "--rebuild-only" in sys.argv:
        # Reconstruiește pagina + feed din store, FĂRĂ fetch/LLM (pentru cleanup/regenerare).
        print("--rebuild-only: reconstruiesc din store, fără fetch/LLM")
    else:
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
        for it in items:
            u = it["link"].split("?")[0]; k = norm(it["title"])
            if u in have or k in seent: continue
            seent.add(k); new.append(it)
            if len(new) >= MAX_NEW: break
        print(f"noi de generat: {len(new)} | în store: {len(store)}")
        fb_count = 0
        for it in new:
            rec = make_record(it, now)         # 2 trepte: explainer complet → traducere simplă
            if rec is None:
                rec = make_fallback(it, now); fb_count += 1   # ultimă instanță: engleză badge-uită
            store.append(rec)
        if new:
            print(f"generate: {len(new) - fb_count} traduse RO / {fb_count} fallback engleză")

        # VINDECĂ fallback-urile: re-încearcă traducerea știrilor rămase în engleză (providerii
        # free pică intermitent; fără asta, o știre prinsă pe fallback rămânea engleză pe veci).
        # Întâi cele mai vizibile (scor mare); în limita bugetului de timp.
        healed = 0
        for s in sorted([x for x in store if x.get("fb")], key=lambda x: -x.get("score", 0)):
            if _DEADLINE and time.time() > _DEADLINE - 25: break   # lasă timp de scriere/commit
            it = {"title": s.get("titlu", ""), "desc": s.get("fapt", ""), "src": s.get("src", ""),
                  "link": s.get("link") or s["url"], "ts": s.get("ts", 0), "score": s.get("score", 0)}
            rec = make_record(it, now)   # None dacă tot nu iese română → rămâne fallback
            if rec:
                s["titlu"] = rec["titlu"]; s["fapt"] = rec["fapt"]; s["ce_inseamna"] = rec["ce_inseamna"]
                s["cat"] = rec["cat"]; s.pop("fb", None)
                if rec.get("tier2"): s["tier2"] = 1
                healed += 1
        if healed: print(f"vindecate (fallback→RO): {healed}")

    store.sort(key=lambda s: -s.get("score", 0))
    disp = store[:DISPLAY]
    counts = {k: sum(1 for s in disp if s["cat"] == k) for k, _ in CATS}

    cards = []
    for s in disp:
        ref = s["ts"] or s["gen_ts"]
        dmin = max(0, (now - ref) / 60)
        if dmin < 1:
            when = "chiar acum"
        elif dmin < 60:
            when = f"acum {int(dmin)} min"
        elif dmin < 1440:
            when = f"acum {int(dmin // 60)}h"
        else:
            when = f"acum {int(dmin // 1440)}z"
        cards.append(f'''<article class="card news-card" data-cat="{s['cat']}" data-ts="{s['ts'] or s['gen_ts']:.0f}" data-score="{s.get('score',0)}">
<div class="ne-top"><span class="ne-src">🌍 {html.escape(s['src'])} · {CAT_LABEL[s['cat']]}{' · rezumat în engleză' if s.get('fb') else ''}</span><span class="ne-when">{when}</span></div>
<h2>{html.escape(s['titlu'])}</h2>
<p class="ne-fapt">{html.escape(s['fapt'])} <a class="ne-link" href="{html.escape(s['link'])}" target="_blank" rel="noopener nofollow">Sursă: {html.escape(s['src'])} →</a></p>
<div class="ne-cti"><strong>💡 Ce înseamnă pentru tine:</strong> {html.escape(s['ce_inseamna'])}</div>
</article>''')

    tabs = f'<button class="news-tab active" data-f="all">Toate <span>({len(disp)})</span></button>'
    for k, label in CATS:
        if counts[k]: tabs += f'<button class="news-tab" data-f="{k}">{label} <span>({counts[k]})</span></button>'
    today = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")

    page = f'''<!DOCTYPE html><html lang="ro"><head>
<meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; base-uri 'self'; object-src 'none'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://maumjqciuxdbwjtvcpsy.supabase.co https://maumjqciuxdbwjtvcpsy.functions.supabase.co wss://maumjqciuxdbwjtvcpsy.supabase.co; form-action 'self'; frame-src 'self'; upgrade-insecure-requests"><meta name="referrer" content="strict-origin-when-cross-origin"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Știri economice externe — ce înseamnă pentru tine | Clubul Financiar</title>
<meta name="description" content="Cele mai importante știri economice mondiale, explicate pe înțelesul tău: ce înseamnă fiecare pentru banii, rata și economiile tale. Surse citate.">
<meta name="robots" content="index, follow"><meta name="theme-color" content="#0f2540">
<link rel="canonical" href="https://clubulfinanciar.ro/stiri-externe"><link rel="icon" type="image/png" href="/favicon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website"><meta property="og:site_name" content="Clubul Financiar"><meta property="og:locale" content="ro_RO"><meta property="og:title" content="Știri economice externe — ce înseamnă pentru tine"><meta property="og:description" content="Știri economice mondiale explicate pentru banii tăi."><meta property="og:url" content="https://clubulfinanciar.ro/stiri-externe"><meta property="og:image" content="https://clubulfinanciar.ro/og-image.jpg">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="Știri economice externe — ce înseamnă pentru tine"><meta name="twitter:image" content="https://clubulfinanciar.ro/og-image.jpg">
<script>(function(){{var t=localStorage.getItem("cf-theme");if(t)document.documentElement.setAttribute("data-theme",t);}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400..800&family=Sora:wght@600;700;800&family=Fraunces:opsz,ital,wght@9..144,0,400;9..144,0,600;9..144,1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v=31"><link rel="stylesheet" href="/assets/upgrade.css?v={V}"><link rel="stylesheet" href="/assets/cf-ultra.css?v=1"><link rel="stylesheet" href="/assets/cf-preview.css?v=2">
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
<div class="news-tabs" style="justify-content:center;margin-top:14px"><a class="news-tab" href="/stiri">🇷🇴 Știri România</a><a class="news-tab active" href="/stiri-externe"><span>🌍 Știri externe</span></a></div></div></section>
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
  // Timestamp LIVE: recalculează „acum X" din data-ts la fiecare încărcare (textul server-side
  // se învechea între rulări — zicea „acum 5 min" și la 4h). Server-side rămâne fallback fără JS.
  function rel(ts){{ var d=(Date.now()/1000)-ts; if(d<0)d=0; if(d<60)return 'chiar acum'; if(d<3600)return 'acum '+Math.floor(d/60)+' min'; if(d<86400)return 'acum '+Math.floor(d/3600)+'h'; return 'acum '+Math.floor(d/86400)+'z'; }}
  function tick(){{ cards.forEach(function(c){{ var w=c.querySelector('.ne-when'); var ts=parseFloat(c.dataset.ts)||0; if(w&&ts){{ w.textContent=rel(ts); }} }}); }}
  tick(); setInterval(tick,60000);
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
<script defer src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.108.2/dist/umd/supabase.js" integrity="sha384-nD3dwv4+ZqdYnmZKe/249ImlV04om7xTCcsoSeQYI+RO+XlKPoqAWaJR1M5SJH9p" crossorigin="anonymous"></script><script defer src="/assets/tilt.js?v={V}"></script><script defer src="/assets/site.js?v={V}"></script></body></html>'''
    open(os.path.join(DOCS, "stiri-externe.html"), "w", encoding="utf-8").write(page)
    json.dump(store, open(STORE_F, "w"), ensure_ascii=False)
    # feed compact pentru Terminal (știri inline, refolosește același store)
    news_top = [{"titlu": s.get("titlu", ""), "fapt": s.get("fapt", ""), "src": s.get("src", ""),
                 "cat": s.get("cat", ""), "link": s.get("link") or s.get("url", "")} for s in disp[:15]]
    os.makedirs(os.path.join(DOCS, "data"), exist_ok=True)
    json.dump({"updated": time.strftime("%Y-%m-%d %H:%M", time.gmtime()), "items": news_top},
              open(os.path.join(DOCS, "data", "news.json"), "w"), ensure_ascii=False)
    # Telemetrie diagnostic (de ce eșuează LLM-urile în cloud) — comisă de workflow, citită de pe main.
    fresh = [s for s in store if s.get("gen_ts", 0) > now - 360]
    _DIAG["summary"] = {"new": len(new), "fresh": len(fresh),
                        "fb": sum(1 for s in fresh if s.get("fb")),
                        "tier2": sum(1 for s in fresh if s.get("tier2")),
                        "explainer": sum(1 for s in fresh if not s.get("fb") and not s.get("tier2"))}
    json.dump(_DIAG, open(os.path.join(DOCS, "data", "news_debug.json"), "w"), ensure_ascii=False, indent=1)
    print(f"✅ stiri-externe.html: {len(disp)} afișate ({len(new)} noi generate azi)")
    print(f"DIAG: ok={_DIAG['ok']} | err={_DIAG['err']} | ro_reject={_DIAG['ro_reject']} | no_keys={_DIAG['no_keys']}")

if __name__ == "__main__":
    main()
