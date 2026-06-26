#!/usr/bin/env python3
"""Construiește paginile noilor articole din _src + metadata, apoi rebuild educatie/search/sitemap/index."""
import json, re, html, os, sys, glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shell import NAV_HTML, FOOTER_HTML  # nav+footer pre-randate static (sursă unică)

ROOT = "/Users/savulescucristian/clubul-financiar/docs"
ART = os.path.join(ROOT, "articole")
SRC = os.path.join(ART, "_src")
RECORDS = "/Users/savulescucristian/clubul-financiar/_records.json"
GLOS_SRC = "/private/tmp/claude-501/-Users-savulescucristian/2d8bd220-1ab9-4311-b6f9-e180142ffdfa/tasks/wu28oa28b.output"
V = "32"  # cache bust
BUILD_DATE = "2026-06-19"  # dată build pentru date noi (articolele existente păstrează data lor)

CATS = [
    ("buget", "💰 Buget personal"), ("economii", "🐖 Economii"), ("datorii", "💳 Datorii"),
    ("psihologie", "🧠 Psihologia banilor"), ("venituri", "💵 Venituri"), ("investitii", "📈 Investiții"),
    # notă: "datorii" folosea ✂️ — schimbat în 💳 (vezi mai jos)
    ("credite", "🏦 Credite"), ("economie", "🌍 Economie"), ("antreprenoriat", "🚀 Antreprenoriat"),
    ("imobiliare", "🏠 Imobiliare"), ("crypto", "₿ Criptomonede"), ("taxe", "🧾 Taxe & ANAF"),
    ("pensii", "🪙 Pensii"), ("asigurari", "🛡️ Asigurări"), ("planificare", "🗺️ Planificare financiară"),
    ("siguranta", "🔐 Siguranță & fraude"),
    ("fire", "🔥 Independență financiară (FIRE)"),
]
CATNAME = dict(CATS)
CATORDER = [c for c, _ in CATS]

def fold(s):
    s = (s or "").lower()
    for a, b in {"ă":"a","â":"a","î":"i","ș":"s","ş":"s","ț":"t","ţ":"t"}.items():
        s = s.replace(a, b)
    return s

def esc(s):
    return html.escape(s or "", quote=True)

def slugify(s):
    s = fold(s); s = re.sub(r"[^a-z0-9]+", "-", s).strip("-"); return s[:50] or "x"

def clip(s, n=160):
    s = (s or "").strip()
    if len(s) <= n:
        return s
    cut = s[:n].rsplit(" ", 1)[0].rstrip(" ,.;:–-")
    return cut + "…"

def clean_body(body):
    body = body.strip()
    body = re.sub(r"^```html\s*|^```\s*|```\s*$", "", body).strip()
    body = re.sub(r"<h1[^>]*>.*?</h1>", "", body, flags=re.S|re.I)  # fără h1 în corp
    body = re.sub(r'<div class="disc">.*?</div>', "", body, flags=re.S|re.I)  # fără disclaimer dublu
    body = re.sub(r'<p[^>]*>\s*<a[^>]*>\s*←[^<]*</a>\s*</p>', "", body, flags=re.S|re.I)  # fără buton back
    return body.strip()

def reading_minutes(body):
    txt = re.sub(r"<[^>]+>", " ", body)
    n = len(txt.split())
    return max(3, round(n / 200))

RO_LUNI = {"01":"ian.","02":"feb.","03":"mar.","04":"apr.","05":"mai","06":"iun.",
           "07":"iul.","08":"aug.","09":"sep.","10":"oct.","11":"nov.","12":"dec."}
def ro_date(iso):
    y, m, d = iso.split("-"); return f"{int(d)} {RO_LUNI[m]} {y}"

PAGE_TMPL = '''<!DOCTYPE html><html lang="ro"><head>
<meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; base-uri 'self'; object-src 'none'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://maumjqciuxdbwjtvcpsy.supabase.co https://maumjqciuxdbwjtvcpsy.functions.supabase.co wss://maumjqciuxdbwjtvcpsy.supabase.co; form-action 'self'; frame-src 'self'; upgrade-insecure-requests"><meta name="referrer" content="strict-origin-when-cross-origin"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Clubul Financiar</title><meta name="description" content="{desc}"><meta name="robots" content="index, follow"><meta name="theme-color" content="#0f2540">
<link rel="canonical" href="https://clubulfinanciar.ro/articole/{slug}"><link rel="icon" type="image/png" href="/favicon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="article"><meta property="og:site_name" content="Clubul Financiar"><meta property="og:locale" content="ro_RO">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="https://clubulfinanciar.ro/articole/{slug}"><meta property="og:image" content="https://clubulfinanciar.ro/og-image.jpg">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{title}"><meta name="twitter:description" content="{desc}"><meta name="twitter:image" content="https://clubulfinanciar.ro/og-image.jpg">
<script type="application/ld+json">{ldjson}</script><script type="application/ld+json">{bcjson}</script>
<script>(function(){{var t=localStorage.getItem("cf-theme");if(t)document.documentElement.setAttribute("data-theme",t);}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fraunces:opsz,ital,wght@9..144,0,400;9..144,0,600;9..144,1,400&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v=31"><link rel="stylesheet" href="/assets/upgrade.css?v={v}"><link rel="stylesheet" href="/assets/cf-ultra.css?v=4"><link rel="stylesheet" href="/assets/cf-article.css?v=1"></head><body>{nav}<main class="u-page"><article class="article"><p class="meta"><a href="/educatie">Educație</a> · <a href="/educatie#{cat}">{catname}</a> · {min} min citire · Actualizat {date_disp} · Scris de <a href="/despre" rel="author">Săvulescu Cristian</a></p><h1>{title}</h1>{body}<div class="disc">⚠️ Conținut educativ, nu sfat de investiții. Pentru decizii financiare consultă un specialist autorizat.</div><p style="margin-top:26px"><a class="btn btn-ghost" href="/educatie">← Toate articolele</a></p></article></main>{footer}<script defer src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.108.2/dist/umd/supabase.js" integrity="sha384-nD3dwv4+ZqdYnmZKe/249ImlV04om7xTCcsoSeQYI+RO+XlKPoqAWaJR1M5SJH9p" crossorigin="anonymous"></script><script defer src="/assets/article.js?v={v}"></script><script defer src="/assets/site.js?v={v}"></script></body></html>'''

def clean_cat(cat):
    # CATNAME include emoji; pentru breadcrumb vrem nume curat
    return re.sub(r"^[^\wĂÂÎȘȚăâîșț]+", "", CATNAME.get(cat, cat)).strip()

def build_page(slug, title, desc, cat, body):
    mins = reading_minutes(body)
    ld = json.dumps({
        "@context":"https://schema.org","@type":"Article","headline":title,"description":desc,
        "inLanguage":"ro-RO","datePublished":BUILD_DATE,"dateModified":BUILD_DATE,
        "author":{"@type":"Person","name":"Săvulescu Cristian","url":"https://clubulfinanciar.ro/despre","jobTitle":"Fondator, Clubul Financiar","description":"Investitor în piața de acțiuni de peste 10 ani."},
        "image":"https://clubulfinanciar.ro/og-image.jpg",
        "publisher":{"@type":"Organization","name":"Clubul Financiar",
        "logo":{"@type":"ImageObject","url":"https://clubulfinanciar.ro/icon-512.png"}},
        "mainEntityOfPage":f"https://clubulfinanciar.ro/articole/{slug}"}, ensure_ascii=False)
    bc = json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Acasă","item":"https://clubulfinanciar.ro/"},
        {"@type":"ListItem","position":2,"name":"Educație","item":"https://clubulfinanciar.ro/educatie"},
        {"@type":"ListItem","position":3,"name":clean_cat(cat),"item":f"https://clubulfinanciar.ro/educatie#{cat}"},
        {"@type":"ListItem","position":4,"name":title,"item":f"https://clubulfinanciar.ro/articole/{slug}"}]},
        ensure_ascii=False)
    return PAGE_TMPL.format(title=esc(title), desc=esc(desc), slug=slug, ldjson=ld, bcjson=bc,
        cat=cat, catname=esc(CATNAME.get(cat, cat)), min=mins, body=body, v=V,
        date_disp=ro_date(BUILD_DATE), nav=NAV_HTML, footer=FOOTER_HTML)

# ---------- 1. construiește paginile noi ----------
new_built, skipped, missing = 0, [], []
if os.path.exists(RECORDS):
    records = json.load(open(RECORDS, encoding="utf-8"))
    for r in records:
        slug = r.get("slug"); title = r.get("title"); desc = r.get("metaDescription"); cat = r.get("category")
        if not (slug and title and cat):
            continue
        if cat not in CATNAME:
            cat = "planificare"
        frag = os.path.join(SRC, slug + ".html")
        dest = os.path.join(ART, slug + ".html")
        if os.path.exists(dest):
            skipped.append(slug); continue
        if not os.path.exists(frag):
            missing.append(slug); continue
        body = clean_body(open(frag, encoding="utf-8").read())
        open(dest, "w", encoding="utf-8").write(build_page(slug, title, desc or title, cat, body))
        new_built += 1
    print(f"Pagini noi construite: {new_built} | sărite (existau): {len(skipped)} | fragment lipsă: {len(missing)}")
    if missing: print("  lipsă:", missing[:20])
else:
    print("Nu există _records.json — sar peste construirea paginilor noi (rebuild indexuri din ce e pe disc).")

# ---------- 2. scanează toate articolele ----------
def extract(path):
    t = open(path, encoding="utf-8").read()
    title = re.search(r'<meta property="og:title" content="([^"]*)"', t)
    desc = re.search(r'<meta name="description" content="([^"]*)"', t)
    cat = re.search(r'educatie(?:\.html)?#([a-z]+)"', t)
    if not (title and cat):
        return None
    return {"slug": os.path.basename(path)[:-5], "title": html.unescape(title.group(1)),
            "desc": html.unescape(desc.group(1)) if desc else "", "cat": cat.group(1)}

arts = []
for p in glob.glob(os.path.join(ART, "*.html")):
    e = extract(p)
    if e: arts.append(e)
arts.sort(key=lambda a: fold(a["title"]))
total = len(arts)
print(f"Total articole pe disc: {total}")

bycat = {}
for a in arts:
    bycat.setdefault(a["cat"], []).append(a)

# ---------- 3. rebuild educatie.html ----------
sections = []
for cat in CATORDER:
    items = bycat.get(cat, [])
    if not items: continue
    cards = "".join(
        f'<a class="card reveal" href="/articole/{a["slug"]}"><h3>{esc(a["title"])}</h3><p>{esc(a["desc"])}</p><span class="more">Citește</span></a>'
        for a in items)
    sections.append(
        f'<h2 class="title cat-h" id="{cat}" style="margin-top:44px">{esc(CATNAME[cat])} <span style="color:var(--muted);font-weight:400;font-size:1rem">({len(items)})</span></h2><div class="grid grid-3 cat-grid">{cards}</div>')
quicknav = "".join(f'<a href="#{cat}" class="pill">{esc(CATNAME[cat])}</a>' for cat in CATORDER if bycat.get(cat))

EDU_HEAD = '''<!DOCTYPE html><html lang="ro"><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; base-uri 'self'; object-src 'none'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://maumjqciuxdbwjtvcpsy.supabase.co https://maumjqciuxdbwjtvcpsy.functions.supabase.co wss://maumjqciuxdbwjtvcpsy.supabase.co; form-action 'self'; frame-src 'self'; upgrade-insecure-requests"><meta name="referrer" content="strict-origin-when-cross-origin"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Educație financiară — TOTAL articole și ghiduri — Clubul Financiar</title><meta name="description" content="Cea mai completă bibliotecă RO de educație financiară: TOTAL articole despre buget, economii, investiții, credite, taxe, pensii și FIRE."><meta name="robots" content="index, follow"><meta name="theme-color" content="#10b981">
<link rel="canonical" href="https://clubulfinanciar.ro/educatie"><link rel="icon" type="image/png" href="/favicon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website"><meta property="og:site_name" content="Clubul Financiar"><meta property="og:locale" content="ro_RO"><meta property="og:title" content="Educație financiară — articole și ghiduri"><meta property="og:description" content="Cea mai completă bibliotecă RO de educație financiară."><meta property="og:url" content="https://clubulfinanciar.ro/educatie"><meta property="og:image" content="https://clubulfinanciar.ro/og-image.jpg">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="Educație financiară — articole și ghiduri"><meta name="twitter:description" content="Cea mai completă bibliotecă RO de educație financiară."><meta name="twitter:image" content="https://clubulfinanciar.ro/og-image.jpg">
<script>(function(){var t=localStorage.getItem("cf-theme");if(t)document.documentElement.setAttribute("data-theme",t);})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fraunces:opsz,ital,wght@9..144,0,400;9..144,0,600;9..144,1,400&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v=31"><link rel="stylesheet" href="/assets/upgrade.css?v=__V__"></head><body>__NAV__<section class="section"><div class="container"><div class="center" style="margin-bottom:6px"><p class="eyebrow">Bibliotecă · TOTAL articole</p><h1 class="title">Educație financiară</h1><p class="lead" style="margin-inline:auto">Ghiduri pe înțelesul tuturor — de la primul buget la independența financiară.</p></div>
<div class="glos-search" style="max-width:560px"><input type="search" id="eduQ" placeholder="Filtrează articolele… (ex: ETF, pensie, credit)" autocomplete="off"></div>
<div style="display:flex;flex-wrap:wrap;gap:6px;justify-content:center;margin:18px 0 4px">__QUICKNAV__</div>
<p id="eduEmpty" class="search-hint" hidden>Niciun articol găsit. Încearcă alt cuvânt.</p>
__SECTIONS__
</div></section>
<script>
const eduCards=[...document.querySelectorAll(".cat-grid .card")];
const eduHeads=[...document.querySelectorAll(".cat-h")];
const eduQ=document.getElementById("eduQ"), eduEmpty=document.getElementById("eduEmpty");
const eduNorm=s=>(s||"").toLowerCase().replace(/[ăâ]/g,"a").replace(/î/g,"i").replace(/ș|ş/g,"s").replace(/ț|ţ/g,"t");
eduCards.forEach(c=>c.dataset.s=eduNorm(c.textContent));
eduQ&&eduQ.addEventListener("input",()=>{
  const q=eduNorm(eduQ.value.trim()); let shown=0;
  eduCards.forEach(c=>{const v=!q||c.dataset.s.includes(q);c.style.display=v?"":"none";c.classList.toggle("in",v);if(v)shown++;});
  eduHeads.forEach(h=>{const g=h.nextElementSibling;const any=g&&[...g.children].some(x=>x.style.display!=="none");h.style.display=any?"":"none";if(g)g.style.display=any?"":"none";});
  eduEmpty.hidden=shown>0;
});
</script>
__FOOTER__<script defer src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.108.2/dist/umd/supabase.js" integrity="sha384-nD3dwv4+ZqdYnmZKe/249ImlV04om7xTCcsoSeQYI+RO+XlKPoqAWaJR1M5SJH9p" crossorigin="anonymous"></script><script defer src="/assets/site.js?v=__V__"></script></body></html>'''

edu = (EDU_HEAD.replace("__V__", V).replace("__QUICKNAV__", quicknav)
       .replace("__SECTIONS__", "\n".join(sections)).replace("TOTAL", str(total))
       .replace("__NAV__", NAV_HTML).replace("__FOOTER__", FOOTER_HTML))
# educatie.html e generat acum de _build_manual.py (Manualul); nu-l mai suprascriem aici
# open(os.path.join(ROOT, "educatie.html"), "w", encoding="utf-8").write(edu)
print("educatie.html rebuild OK")

# ---------- 4. search-index.json (articole + glosar + calculatoare) ----------
idx = []
for a in arts:
    idx.append({"s": a["slug"], "t": a["title"], "d": a["desc"], "c": a["cat"],
                "cn": CATNAME.get(a["cat"], a["cat"]), "u": f"/articole/{a['slug']}", "k": "a"})

# glosar
try:
    gd = json.load(open(GLOS_SRC, encoding="utf-8"))
    gterms = gd["result"] if isinstance(gd, dict) and "result" in gd else gd
    seen = set()
    for t in gterms:
        term = (t.get("term") or "").strip(); deff = (t.get("definition") or "").strip()
        if not term or fold(term) in seen: continue
        seen.add(fold(term))
        idx.append({"t": term, "d": clip(deff, 160), "u": "/glosar#" + slugify(term), "k": "g"})
except Exception as e:
    print("glosar search skip:", e)

CALCS = [
    ("Calculator dobândă compusă", "Cât cresc banii tăi în timp", "/calculatoare/dobanda-compusa"),
    ("Calculator rată credit", "Rata lunară, total și dobândă", "/calculatoare/credit"),
    ("Calculator salariu net", "Din brut în net (CAS, CASS, impozit)", "/calculatoare/salariu-net"),
    ("Calculator economii", "Cât pui lunar pentru o țintă", "/calculatoare/economii"),
    ("Calculator inflație", "Puterea de cumpărare în timp", "/calculatoare/inflatie"),
    ("Calculator FIRE", "Suma pentru independență financiară", "/calculatoare/fire"),
    ("Calculator grad de îndatorare", "Cât din venit merge pe rate", "/calculatoare/grad-indatorare"),
    ("Calculator obiectiv de economisire", "În cât timp atingi ținta", "/calculatoare/obiectiv-economisire"),
    ("Calculator chirie vs cumpărare", "Ce e mai avantajos pe termen lung", "/calculatoare/chirie-vs-cumparare"),
    ("Calculator pensie", "Cât strângi până la pensionare", "/calculatoare/pensie"),
    ("Calculator impozit investiții", "Pe câștiguri și dividende", "/calculatoare/impozit-investitii"),
]
for t, d, u in CALCS:
    idx.append({"t": t, "d": d, "u": u, "k": "calc"})

json.dump(idx, open(os.path.join(ROOT, "search-index.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"search-index.json OK ({len(idx)} intrări)")

# ---------- 5. sitemap.xml ----------
PAGES = ["", "incepe-aici", "educatie", "teste", "glosar", "stiri", "investitii",
         "credite", "calculatoare", "cursuri", "premium", "despre", "contact",
         "privacy", "terms"]
CALC_PAGES = [u.lstrip("/") for _, _, u in CALCS]
COURSE_PAGES = ["cursuri/" + os.path.basename(p)[:-5] for p in glob.glob(os.path.join(ROOT, "cursuri", "*.html"))]
urls = []
def add(loc, pr="0.6"):
    urls.append(f"<url><loc>https://clubulfinanciar.ro/{loc}</loc><lastmod>{BUILD_DATE}</lastmod><changefreq>weekly</changefreq><priority>{pr}</priority></url>")
add("", "1.0")
for p in PAGES[1:]: add(p, "0.8")
for p in CALC_PAGES: add(p, "0.7")
for p in COURSE_PAGES: add(p, "0.6")
for a in arts: add(f"articole/{a['slug']}", "0.6")
sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n"
open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(sitemap)
print(f"sitemap.xml OK ({len(urls)} url-uri)")

# ---------- 6. actualizează cifrele din index.html ----------
idxp = os.path.join(ROOT, "index.html")
h = open(idxp, encoding="utf-8").read()
ncat = len([c for c in CATORDER if bycat.get(c)])
h = re.sub(r'<div class="num">\d+\+</div>', f'<div class="num">{total}+</div>', h)
h = re.sub(r'(<div class="num">)\d+(</div><div class="lbl">Calculatoare financiare</div>)', rf'\g<1>{len(CALCS)}\g<2>', h)
h = re.sub(r'(<div class="num">)\d+(</div><div class="lbl">Categorii acoperite</div>)', rf'\g<1>{ncat}\g<2>', h)
h = re.sub(r'Bibliotecă · \d+ articole', f'Bibliotecă · {total} articole', h)
h = re.sub(r'Vezi toate cele \d+ articole', f'Vezi toate cele {total} articole', h)
open(idxp, "w", encoding="utf-8").write(h)
print("index.html cifre actualizate")
print("DONE")
