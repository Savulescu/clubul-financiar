#!/usr/bin/env python3
"""Construiește MANUALUL: hub (educatie.html) cu 17 capitole în ordine + pagini de capitol
(docs/manual/<domain>.html) cu lecțiile în ordine pedagogică + testul capitolului.
Integrează Educație/Investiții/Credite/Cursuri/Teste într-o singură structură, ca un manual."""
import json, os, html, sys, re
ROOT = "/Users/savulescucristian/clubul-financiar"
DOCS = os.path.join(ROOT, "docs")
sys.path.insert(0, ROOT)
from _shell import NAV_HTML, FOOTER_HTML
V = "30"

NAMES = {"buget":"💰 Buget personal","economii":"🐖 Economii","datorii":"💳 Datorii",
 "psihologie":"🧠 Psihologia banilor","venituri":"💵 Venituri","investitii":"📈 Investiții",
 "credite":"🏦 Credite","economie":"🌍 Economie","antreprenoriat":"🚀 Antreprenoriat",
 "imobiliare":"🏠 Imobiliare","crypto":"₿ Criptomonede","taxe":"🧾 Taxe & ANAF","pensii":"🪙 Pensii",
 "asigurari":"🛡️ Asigurări","planificare":"🗺️ Planificare financiară","siguranta":"🔐 Siguranță & fraude",
 "fire":"🔥 Independență financiară (FIRE)"}
ORDER = ["buget","economii","datorii","venituri","psihologie","credite","asigurari","planificare",
 "investitii","pensii","fire","imobiliare","crypto","taxe","antreprenoriat","economie","siguranta"]
NIVEL = {"incepator":"Începător","intermediar":"Intermediar","avansat":"Avansat"}

idx = json.load(open(os.path.join(DOCS,"search-index.json"),encoding="utf-8"))
TITLE = {x["s"]:x["t"] for x in idx if x.get("k")=="a"}
cursuri = {c["domain"]:c for c in json.load(open(os.path.join(ROOT,"_audits/cursuri.json"),encoding="utf-8"))}
split = json.load(open(os.path.join(ROOT,"_audits/free_premium_split.json"),encoding="utf-8"))
PREMIUM = set()
for s in split:
    for sl in s.get("premium",[]): PREMIUM.add(sl)
manifest = json.load(open(os.path.join(DOCS,"assets/quiz/manifest.json"),encoding="utf-8"))
FREE_DOMAINS = {"buget","economii","datorii"}

def esc(s): return html.escape(s or "", quote=True)
FONT = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400..800&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">'
CSS = '''<style>
.chap-card{display:block;background:var(--card);border:1px solid var(--border);border-radius:16px;padding:20px 22px;box-shadow:var(--shadow);transition:transform .18s,box-shadow .18s,border-color .18s;position:relative;margin-bottom:14px}
.chap-card:hover{transform:translateY(-3px);box-shadow:var(--shadow-lg);border-color:color-mix(in srgb,var(--emerald) 45%,var(--border))}
.chap-card .cn{position:absolute;top:18px;right:20px;font-size:.8rem;font-weight:800;color:var(--muted)}
.chap-card h3{font-size:1.15rem;margin:0 0 3px}
.chap-card p{color:var(--muted);font-size:.9rem;margin:0}
.chap-meta{color:var(--muted);font-size:.82rem;margin-top:8px}
.cprog{height:7px;border-radius:99px;background:var(--bg-soft);margin-top:10px;overflow:hidden}.cprog i{display:block;height:100%;background:var(--grad);width:0;transition:width .4s}
.les{display:flex;align-items:center;gap:12px;padding:13px 16px;border:1px solid var(--border);border-radius:12px;margin-bottom:9px;background:var(--card);transition:.15s}
.les:hover{border-color:var(--emerald);transform:translateX(3px)}
.les .ln{flex:0 0 30px;height:30px;border-radius:8px;background:var(--bg-soft);display:grid;place-items:center;font-weight:800;font-size:.85rem;color:var(--muted)}
.les .lt{flex:1;font-weight:600;color:var(--text)}
.les .lk{font-size:.92rem}
.les.read .ln{background:var(--emerald);color:#fff}
.nivel-h{font-family:var(--font-display);font-weight:800;font-size:1.1rem;margin:24px 0 12px;color:var(--emerald-link)}
.chap-nav{display:flex;justify-content:space-between;gap:12px;margin-top:30px;flex-wrap:wrap}
.test-cta{background:linear-gradient(135deg,color-mix(in srgb,var(--emerald) 12%,var(--card)),var(--card));border:1px solid color-mix(in srgb,var(--emerald) 35%,var(--border));border-radius:16px;padding:22px;text-align:center;margin:26px 0}
</style>'''

def head(title, desc, canon, ld=""):
    return f'''<!DOCTYPE html><html lang="ro"><head>{ld}
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="robots" content="index, follow"><meta name="theme-color" content="#10b981">
<link rel="canonical" href="{canon}"><link rel="icon" type="image/png" href="/favicon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website"><meta property="og:site_name" content="Clubul Financiar"><meta property="og:locale" content="ro_RO"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{canon}"><meta property="og:image" content="https://clubulfinanciar.ro/og-image.jpg">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:image" content="https://clubulfinanciar.ro/og-image.jpg">
<script>(function(){{var t=localStorage.getItem("cf-theme");if(t)document.documentElement.setAttribute("data-theme",t);}})();</script>
{FONT}
<link rel="stylesheet" href="/assets/style.css?v={V}"><link rel="stylesheet" href="/assets/upgrade.css?v={V}">{CSS}</head><body>{NAV_HTML}'''

FOOT_SCRIPTS = f'{FOOTER_HTML}<script defer src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script><script defer src="/assets/site.js?v={V}"></script>'

# ---------- pagini de capitol ----------
os.makedirs(os.path.join(DOCS,"manual"), exist_ok=True)
built=0
for i, dom in enumerate(ORDER):
    if dom not in cursuri: continue
    c = cursuri[dom]; lessons = c["lessons"]
    slugs = [l["slug"] for l in lessons]
    m = manifest.get(dom, {"lectii":0,"intrebari":0})
    # grupează pe nivel păstrând ordinea
    groups = {}
    for l in lessons: groups.setdefault(l["nivel"], []).append(l["slug"])
    rows=""; num=0
    for niv in ["incepator","intermediar","avansat"]:
        if niv not in groups: continue
        rows += f'<h2 class="nivel-h">{NIVEL[niv]}</h2>'
        for sl in groups[niv]:
            num += 1
            lock = ' <span class="lk" title="Premium">🔒</span>' if sl in PREMIUM else ''
            rows += f'<a class="les" data-slug="{sl}" href="/articole/{sl}.html"><span class="ln">{num}</span><span class="lt">{esc(TITLE.get(sl,sl))}</span>{lock}</a>'
    prev_dom = ORDER[i-1] if i>0 else None
    next_dom = ORDER[i+1] if i<len(ORDER)-1 else None
    prevb = f'<a class="btn btn-ghost" href="/manual/{prev_dom}.html">← {esc(NAMES[prev_dom].split(" ",1)[1])}</a>' if prev_dom and prev_dom in cursuri else '<span></span>'
    nextb = f'<a class="btn btn-primary" href="/manual/{next_dom}.html">{esc(NAMES[next_dom].split(" ",1)[1])} →</a>' if next_dom and next_dom in cursuri else '<a class="btn btn-ghost" href="/educatie.html">Toate capitolele</a>'
    test_free = dom in FREE_DOMAINS
    cname = NAMES[dom].split(" ",1)[1]; churl = f"https://clubulfinanciar.ro/manual/{dom}.html"
    course = {"@context":"https://schema.org","@type":"Course","name":cname,"description":c["subtitle"],
        "url":churl,"inLanguage":"ro-RO","isAccessibleForFree":True,"educationalLevel":"începător-avansat",
        "provider":{"@type":"Organization","name":"Clubul Financiar","url":"https://clubulfinanciar.ro"},
        "hasCourseInstance":{"@type":"CourseInstance","courseMode":"online","courseWorkload":f"PT{max(1,m['lectii'])*15}M"}}
    bc = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Acasă","item":"https://clubulfinanciar.ro/"},
        {"@type":"ListItem","position":2,"name":"Manual","item":"https://clubulfinanciar.ro/educatie.html"},
        {"@type":"ListItem","position":3,"name":cname,"item":churl}]}
    ld = f'<script type="application/ld+json">{json.dumps(course,ensure_ascii=False)}</script><script type="application/ld+json">{json.dumps(bc,ensure_ascii=False)}</script>'
    page = head(f'Capitolul {i+1}: {cname} — Manual — Clubul Financiar',
                f'{c["subtitle"]} {m["lectii"]} lecții + test cu {m["intrebari"]} întrebări.',
                f'https://clubulfinanciar.ro/manual/{dom}.html', ld=ld)
    page += f'''<section class="section"><div class="container" style="max-width:820px">
<p class="meta" style="color:var(--muted);font-size:.88rem"><a href="/educatie.html">Manual</a> · Capitolul {i+1} din {len([d for d in ORDER if d in cursuri])}</p>
<h1 class="title" style="margin:6px 0">{NAMES[dom]}</h1>
<p class="lead">{esc(c["subtitle"])}</p>
<div class="chap-meta">{m["lectii"]} lecții · {m["intrebari"]} întrebări în test</div>
<div class="cprog"><i id="cprog"></i></div><p id="cprogtxt" style="color:var(--muted);font-size:.82rem;margin-top:6px"></p>
{rows}
<div class="test-cta">
  <p class="eyebrow" style="margin-bottom:6px">Testează capitolul</p>
  <h2 style="font-size:1.3rem;margin:0 0 8px">Ai învățat {NAMES[dom].split(" ",1)[1]}? Verifică-te.</h2>
  <p style="color:var(--muted);margin:0 0 14px">{m["intrebari"]} întrebări{"" if test_free else " · Premium"} cu feedback pe loc.</p>
  <a class="btn btn-primary" href="/teste.html?d={dom}">Începe testul</a>
</div>
<div class="chap-nav">{prevb}{nextb}</div>
<div class="disc">⚠️ Conținut educativ, nu sfat de investiții. Pentru decizii financiare consultă un specialist autorizat.</div>
</div></section>
<script>
(function(){{
  var slugs={json.dumps(slugs)};
  var read=[];try{{read=JSON.parse(localStorage.getItem("cf-read")||"[]");}}catch(e){{}}
  var done=0;
  document.querySelectorAll(".les").forEach(function(el){{
    if(read.indexOf(el.dataset.slug)>=0){{el.classList.add("read");done++;var t=el.querySelector(".ln");if(t)t.textContent="✓";}}
  }});
  var pct=slugs.length?Math.round(done/slugs.length*100):0;
  document.getElementById("cprog").style.width=pct+"%";
  document.getElementById("cprogtxt").textContent=done+" din "+slugs.length+" lecții citite ("+pct+"%)";
}})();
</script>
{FOOT_SCRIPTS}</body></html>'''
    open(os.path.join(DOCS,"manual",f"{dom}.html"),"w",encoding="utf-8").write(page)
    built+=1

# ---------- hub (educatie.html) ----------
chapters=""
for i, dom in enumerate(ORDER):
    if dom not in cursuri: continue
    c=cursuri[dom]; m=manifest.get(dom,{"lectii":0,"intrebari":0})
    dslugs=json.dumps([l["slug"] for l in c["lessons"]])
    chapters += f'''<a class="chap-card" data-slugs='{dslugs}' href="/manual/{dom}.html"><span class="cn">Capitolul {i+1}</span><h3>{NAMES[dom]}</h3><p>{esc(c["subtitle"])}</p><div class="chap-meta">{m["lectii"]} lecții · {m["intrebari"]} întrebări</div><div class="cprog"><i></i></div></a>'''
hubld = '<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@type":"CollectionPage","name":"Manualul de educație financiară","description":"17 capitole pe domenii, în ordine, cu 500 de lecții și teste.","url":"https://clubulfinanciar.ro/educatie.html","inLanguage":"ro-RO","isPartOf":{"@type":"WebSite","name":"Clubul Financiar","url":"https://clubulfinanciar.ro"}},ensure_ascii=False)+'</script>'
hub = head("Manualul de educație financiară — Clubul Financiar",
           "Manual complet de educație financiară RO: 17 capitole pe domenii, în ordine, cu 500 de lecții și teste. De la buget la independența financiară.",
           "https://clubulfinanciar.ro/educatie.html", ld=hubld)
hub += f'''<section class="section"><div class="container" style="max-width:880px">
<div class="center" style="margin-bottom:8px"><p class="eyebrow">Manual · învață în ordine</p><h1 class="title">Manualul de educație financiară</h1><p class="lead" style="margin-inline:auto">Totul, organizat ca un manual: 17 capitole pe domenii, în ordine logică — de la primul buget la independența financiară. Fiecare capitol are lecții + test.</p></div>
{chapters}
</div></section>
<script>
(function(){{
  var read=[];try{{read=JSON.parse(localStorage.getItem("cf-read")||"[]");}}catch(e){{}}
  document.querySelectorAll(".chap-card").forEach(function(el){{
    var sl=[];try{{sl=JSON.parse(el.dataset.slugs||"[]");}}catch(e){{}}
    var d=sl.filter(function(s){{return read.indexOf(s)>=0;}}).length;
    var b=el.querySelector(".cprog i");if(b)b.style.width=(sl.length?Math.round(d/sl.length*100):0)+"%";
  }});
}})();
</script>
{FOOT_SCRIPTS}</body></html>'''
open(os.path.join(DOCS,"educatie.html"),"w",encoding="utf-8").write(hub)

# ---------- sitemap: adaugă paginile de capitol ----------
sm=open(os.path.join(DOCS,"sitemap.xml"),encoding="utf-8").read()
add=""
for dom in ORDER:
    u=f"https://clubulfinanciar.ro/manual/{dom}.html"
    if u not in sm: add+=f'<url><loc>{u}</loc><changefreq>weekly</changefreq><priority>0.7</priority></url>\n'
if add: sm=sm.replace("</urlset>",add+"</urlset>"); open(os.path.join(DOCS,"sitemap.xml"),"w",encoding="utf-8").write(sm)

print(f"Manual construit: {built} capitole + hub educatie.html + {add.count('<url>')} în sitemap")
