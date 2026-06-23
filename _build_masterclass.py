#!/usr/bin/env python3
"""Construiește secțiunea MASTERCLASS BURSĂ: pagini /masterclass/<slug>.html din _src + _quiz
+ hub masterclass.html. Layout: corp → share/citit → TEST(25) → prev/next → disclaimer → ←Toate.
Citește _audits/masterclass_records.json = [{slug,title,metaDescription,domain,premium}]."""
import json, os, re, html, glob

ROOT = "/Users/savulescucristian/clubul-financiar"
DOCS = os.path.join(ROOT, "docs")
MC = os.path.join(DOCS, "masterclass")
SRC = os.path.join(MC, "_src")
QZ = os.path.join(MC, "_quiz")
RECORDS = os.path.join(ROOT, "_audits", "masterclass_records.json")
import sys; sys.path.insert(0, ROOT)
from _shell import NAV_HTML, FOOTER_HTML
V = "30"
BUILD_DATE = "2026-06-21"

DOMNAMES = {
    "valuation": "Evaluare (valuation)", "allocation": "Alocarea activelor", "credit": "Risc de credit",
    "behavioral": "Psihologia tranzacționării", "compliance": "Reguli & conformitate", "news": "Știri & informație",
    "macro": "Macroeconomie", "risk": "Risc & volatilitate", "execution": "Execuție & ordine",
    "options": "Opțiuni & derivate", "technical": "Analiză tehnică", "fundamental": "Analiză fundamentală",
    "portfolio": "Construcția portofoliului", "fixed_income": "Venit fix & obligațiuni", "equities": "Acțiuni",
    "derivatives": "Derivate", "quant": "Cantitativ & modele",
}
def domname(d): return DOMNAMES.get(d, d.replace("_", " ").title())

def esc(s): return html.escape(s or "", quote=True)
def fold(s):
    s = (s or "").lower()
    for a, b in {"ă":"a","â":"a","î":"i","ș":"s","ş":"s","ț":"t","ţ":"t"}.items(): s = s.replace(a, b)
    return s
def clean_body(b):
    b = b.strip()
    b = re.sub(r"^```html\s*|^```\s*|```\s*$", "", b).strip()
    b = re.sub(r"<h1[^>]*>.*?</h1>", "", b, flags=re.S|re.I)
    b = re.sub(r'<div class="disc">.*?</div>', "", b, flags=re.S|re.I)
    return b.strip()
def reading_minutes(b):
    return max(5, round(len(re.sub(r"<[^>]+>", " ", b).split()) / 200))
RO_LUNI = {"01":"ian.","02":"feb.","03":"mar.","04":"apr.","05":"mai","06":"iun.","07":"iul.","08":"aug.","09":"sep.","10":"oct.","11":"nov.","12":"dec."}
def ro_date(iso): y,m,d = iso.split("-"); return f"{int(d)} {RO_LUNI[m]} {y}"

PAGE = '''<!DOCTYPE html><html lang="ro"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Masterclass Bursă — Clubul Financiar</title><meta name="description" content="{desc}"><meta name="robots" content="index, follow"><meta name="theme-color" content="#10b981">
<link rel="canonical" href="https://clubulfinanciar.ro/masterclass/{slug}.html"><link rel="icon" type="image/png" href="/favicon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="article"><meta property="og:site_name" content="Clubul Financiar"><meta property="og:locale" content="ro_RO">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="https://clubulfinanciar.ro/masterclass/{slug}.html"><meta property="og:image" content="https://clubulfinanciar.ro/og-image.jpg">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{title}"><meta name="twitter:description" content="{desc}"><meta name="twitter:image" content="https://clubulfinanciar.ro/og-image.jpg">
<script type="application/ld+json">{ldjson}</script>
<script>(function(){{var t=localStorage.getItem("cf-theme");if(t)document.documentElement.setAttribute("data-theme",t);}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400..800&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v=31"><link rel="stylesheet" href="/assets/upgrade.css?v={v}"></head><body>{nav}<article class="article"{prem}{dprev}{dnext} data-hub="/masterclass.html"><p class="meta"><a href="/masterclass.html">Masterclass Bursă</a> · <a href="/masterclass.html#{dom}">{domname}</a> · {min} min · Actualizat {date_disp}</p><h1>{title}</h1>{body}<script type="application/json" id="cf-mc-quiz">{quizjson}</script><div class="disc">⚠️ Conținut educativ, nu sfat de investiții. Pentru decizii financiare consultă un specialist autorizat.</div><p style="margin-top:26px"><a class="btn btn-ghost" href="/masterclass.html">← Toate lecțiile Masterclass</a></p></article>{footer}<script defer src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script><script defer src="/assets/masterclass.js?v={v}"></script><script defer src="/assets/site.js?v={v}"></script></body></html>'''

def build_page(rec, body, quizjson, prev, nxt):
    mins = reading_minutes(body)
    ld = {"@context":"https://schema.org","@type":"LearningResource","headline":rec["title"],"description":rec["metaDescription"],
          "inLanguage":"ro-RO","datePublished":BUILD_DATE,"dateModified":BUILD_DATE,
          "author":{"@type":"Organization","name":"Clubul Financiar","url":"https://clubulfinanciar.ro/despre.html"},
          "image":"https://clubulfinanciar.ro/og-image.jpg",
          "publisher":{"@type":"Organization","name":"Clubul Financiar","logo":{"@type":"ImageObject","url":"https://clubulfinanciar.ro/icon-512.png"}},
          "mainEntityOfPage":f"https://clubulfinanciar.ro/masterclass/{rec['slug']}.html"}
    if rec.get("premium"):
        ld["isAccessibleForFree"] = False
        ld["hasPart"] = {"@type":"WebPageElement","isAccessibleForFree":False,"cssSelector":".premium-rest"}
    prem = ' data-premium="1"' if rec.get("premium") else ''
    dprev = f' data-prev="{esc(prev["slug"])}" data-prev-title="{esc(prev["title"])}"' if prev else ''
    dnext = f' data-next="{esc(nxt["slug"])}" data-next-title="{esc(nxt["title"])}"' if nxt else ''
    return PAGE.format(title=esc(rec["title"]), desc=esc(rec["metaDescription"]), slug=rec["slug"],
        ldjson=json.dumps(ld, ensure_ascii=False), v=V, nav=NAV_HTML, footer=FOOTER_HTML,
        prem=prem, dprev=dprev, dnext=dnext, dom=rec["domain"], domname=esc(domname(rec["domain"])),
        min=mins, date_disp=ro_date(BUILD_DATE), body=body, quizjson=json.dumps(quizjson, ensure_ascii=False))

# ---------- build pagini ----------
records = json.load(open(RECORDS, encoding="utf-8"))
# ordine: pe domeniu, păstrând ordinea din records
bydom = {}
for r in records: bydom.setdefault(r["domain"], []).append(r)
order = []
for dom in sorted(bydom): order.extend(bydom[dom])

built, missing = 0, []
for idx, rec in enumerate(order):
    slug = rec["slug"]
    fp = os.path.join(SRC, slug + ".html"); qp = os.path.join(QZ, slug + ".json")
    if not os.path.exists(fp): missing.append(slug); continue
    body = clean_body(open(fp, encoding="utf-8").read())
    quiz = []
    if os.path.exists(qp):
        try:
            qd = json.load(open(qp, encoding="utf-8")); quiz = qd.get("questions", qd) if isinstance(qd, dict) else qd
        except Exception as e: print("  quiz skip", slug, e)
    # prev/next în cadrul aceluiași domeniu
    dlist = bydom[rec["domain"]]; di = dlist.index(rec)
    prev = dlist[di-1] if di > 0 else None
    nxt = dlist[di+1] if di < len(dlist)-1 else None
    open(os.path.join(MC, slug + ".html"), "w", encoding="utf-8").write(build_page(rec, body, quiz, prev, nxt))
    built += 1
print(f"Pagini Masterclass construite: {built} | fragment lipsă: {len(missing)}")
if missing: print("  lipsă:", missing[:10])

# ---------- hub masterclass.html ----------
HUBHEAD = '''<!DOCTYPE html><html lang="ro"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Masterclass Bursă — investiții și trading de la zero — Clubul Financiar</title><meta name="description" content="Masterclass Bursă: curs complet de investiții și tranzacționare, de la zero la avansat, cu lecții și teste de {n} întrebări fiecare.">
<meta name="robots" content="index, follow"><meta name="theme-color" content="#10b981"><link rel="canonical" href="https://clubulfinanciar.ro/masterclass.html"><link rel="icon" type="image/png" href="/favicon.png">
<meta property="og:type" content="website"><meta property="og:site_name" content="Clubul Financiar"><meta property="og:title" content="Masterclass Bursă — Clubul Financiar"><meta property="og:description" content="Curs complet de investiții și tranzacționare, de la zero la avansat."><meta property="og:url" content="https://clubulfinanciar.ro/masterclass.html"><meta property="og:image" content="https://clubulfinanciar.ro/og-image.jpg">
<script>(function(){var t=localStorage.getItem("cf-theme");if(t)document.documentElement.setAttribute("data-theme",t);})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400..800&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v=31"><link rel="stylesheet" href="/assets/upgrade.css?v=__V__"></head><body>__NAV__
<section class="section"><div class="container"><div class="center"><p class="eyebrow">Bursă · de la zero la avansat</p><h1 class="title">Masterclass Bursă</h1><p class="lead" style="margin-inline:auto">Curs complet de investiții și tranzacționare — concepte explicate simplu, cu un test de __NQ__ întrebări după fiecare lecție.</p></div>
<div style="display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin:18px 0 4px">__QUICK__</div>__SECTIONS__</div></section>__FOOTER__
<script defer src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script><script defer src="/assets/site.js?v=__V__"></script></body></html>'''

sections, quick = [], []
for dom in sorted(bydom):
    items = bydom[dom]
    quick.append(f'<a href="#{dom}" class="pill">{esc(domname(dom))}</a>')
    cards = "".join(f'<a class="card reveal" href="/masterclass/{r["slug"]}.html"><h3>{esc(r["title"])}</h3><p>{esc(r["metaDescription"])}</p><span class="more">Învață →</span></a>' for r in items)
    sections.append(f'<h2 class="title cat-h" id="{dom}" style="margin-top:40px">{esc(domname(dom))} <span style="color:var(--muted);font-weight:400;font-size:1rem">({len(items)})</span></h2><div class="grid grid-3">{cards}</div>')
hub = (HUBHEAD.replace("__V__", V).replace("__NAV__", NAV_HTML).replace("__FOOTER__", FOOTER_HTML)
       .replace("__QUICK__", "".join(quick)).replace("__SECTIONS__", "".join(sections))
       .replace("__NQ__", "25").replace("{n}", "25"))
open(os.path.join(DOCS, "masterclass.html"), "w", encoding="utf-8").write(hub)
print(f"Hub masterclass.html construit: {len(records)} lecții, {len(bydom)} domenii")

# ---------- sitemap: adaugă paginile masterclass ----------
smp = os.path.join(DOCS, "sitemap.xml"); sm = open(smp, encoding="utf-8").read()
add = ""
for r in records:
    loc = f"https://clubulfinanciar.ro/masterclass/{r['slug']}.html"
    if loc not in sm:
        add += f'<url><loc>{loc}</loc><lastmod>{BUILD_DATE}</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>'
hubloc = "https://clubulfinanciar.ro/masterclass.html"
if hubloc not in sm: add += f'<url><loc>{hubloc}</loc><lastmod>{BUILD_DATE}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>'
if add: sm = sm.replace("</urlset>", add + "</urlset>"); open(smp, "w", encoding="utf-8").write(sm)
print(f"sitemap += {add.count('<url>')} URL-uri masterclass")
print("DONE")
