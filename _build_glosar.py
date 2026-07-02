#!/usr/bin/env python3
"""Generează docs/glosar.html din _data/glosar.json.

NOTĂ 2026-07-02: template-ul oglindește glosar.html LIVE (titlu/meta SEO,
secțiunea explicativă + FAQ, bara alfabetică sticky cu ancore pe litere,
buton „înapoi sus"). glosar.html a fost editat și direct în trecut —
compară diff-ul înainte de orice rebuild real.
"""
import json, re, html, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shell import NAV_HTML, FOOTER_HTML  # nav+footer pre-randate static

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_data", "glosar.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "glosar.html")

data = json.load(open(SRC, encoding="utf-8"))
terms = data["result"] if isinstance(data, dict) and "result" in data else data

def fold(s):
    s = s.lower()
    repl = {"ă":"a","â":"a","î":"i","ș":"s","ş":"s","ț":"t","ţ":"t"}
    return "".join(repl.get(c, c) for c in s)

def first_letter(term):
    # ia prima literă alfabetică a numelui (fără acronim între paranteze contează tot prima literă)
    f = fold(term.strip())
    for c in f:
        if c.isalpha():
            return c.upper()
    return "#"

# dedupe după termen normalizat, păstrează prima definiție mai lungă
seen = {}
for t in terms:
    term = (t.get("term") or "").strip()
    deff = (t.get("definition") or "").strip()
    if not term or not deff:
        continue
    key = fold(term)
    if key not in seen or len(deff) > len(seen[key]["definition"]):
        seen[key] = {"term": term, "definition": deff}

items = sorted(seen.values(), key=lambda x: fold(x["term"]))

# grupare pe litere
groups = {}
for it in items:
    groups.setdefault(first_letter(it["term"]), []).append(it)
letters = sorted(groups.keys())

ALL = [chr(c) for c in range(ord("A"), ord("Z")+1)]

def slugify(s):
    s = fold(s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:50] or "termen"

def de(n):
    """Gramatică RO: „807 termeni" dar „850 de termeni" — numeralele cu
    ultimele două cifre 01–19 NU primesc „de"."""
    r = n % 100
    return "" if 1 <= r <= 19 else "de "

# construiește lista
blocks = []
used_ids = set()
for L in letters:
    blocks.append(f'<div class="glos-letter" id="lit-{L}">{L}</div>')
    for it in groups[L]:
        tid = slugify(it["term"]); base = tid; n = 1
        while tid in used_ids:
            n += 1; tid = f"{base}-{n}"
        used_ids.add(tid)
        term_e = html.escape(it["term"])
        def_e = html.escape(it["definition"])
        data = fold(it["term"] + " " + it["definition"])
        blocks.append(
            f'<div class="glos-card" id="{tid}" data-letter="{L}" data-search="{html.escape(data)}">'
            f'<h3>{term_e}</h3><p>{def_e}</p></div>'
        )
list_html = "\n".join(blocks)

alpha_btns = '<button class="active" data-l="all">Toate</button>' + "".join(
    f'<button data-l="{L}"{"" if L in groups else " disabled"}>{L}</button>' for L in ALL
)

count = len(items)
nd = de(count)  # "" sau "de "
desc = f"Glosar de termeni financiari cu {count} {nd}definiții clare: bani, investiții, credite și taxe, explicate simplu pentru începători. Caută orice termen gratuit."

breadcrumb_ld = json.dumps({
    "@context": "https://schema.org", "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Acasă", "item": "https://clubulfinanciar.ro/"},
        {"@type": "ListItem", "position": 2, "name": f"Glosar financiar — {count} {nd}termeni explicați simplu", "item": "https://clubulfinanciar.ro/glosar"},
    ],
}, ensure_ascii=False)

# FAQ — vizibil + JSON-LD din aceeași sursă (textul trebuie să coincidă)
faqs = [
    ("Câți termeni are glosarul financiar Clubul Financiar?",
     f"Glosarul cuprinde {count} {nd}termeni financiari, aranjați alfabetic și explicați în limba română, pe înțelesul tuturor. Sunt acoperite teme precum bani, economisire, credite, investiții, taxe și pensii, iar lista este actualizată periodic."),
    ("Glosarul de termeni financiari este gratuit?",
     "Da, glosarul este complet gratuit și nu necesită cont. Poți căuta orice termen, sări la orice literă și deschide definițiile fără nicio limită sau plată."),
    ("Cum caut repede un termen în glosar?",
     "Scrie cuvântul în câmpul de căutare din partea de sus a paginii, de exemplu „dobândă\", „ETF\" sau „CASS\". Lista se filtrează instant și nu trebuie să folosești diacritice. Poți apăsa și o literă din bara alfabetică pentru a sări direct la termenii care încep cu ea."),
    ("Care este diferența dintre un glosar și un dicționar financiar?",
     "În practică sunt termeni apropiați: un glosar este o listă de cuvinte dintr-un domeniu, cu explicații scurte. Glosarul nostru se concentrează pe termeni financiari și folosește definiții simple, scrise pentru începători, nu definiții tehnice de specialitate."),
    ("Definițiile din glosar sunt sfaturi de investiții?",
     "Nu. Definițiile au scop educativ și sunt simplificate pentru a fi ușor de înțeles. Ele te ajută să pricepi termenii, dar nu reprezintă recomandări financiare. Pentru decizii concrete consultă un specialist autorizat."),
]
faq_html = "\n".join(
    f'  <details class="faq-item" style="border-top:1px solid var(--line,#e5e7eb);padding:16px 0"><summary style="cursor:pointer;font-weight:600;font-size:1.05rem">{q}</summary><p style="color:var(--muted);margin-top:10px">{a}</p></details>'
    for q, a in faqs
)
faq_ld = json.dumps({
    "@context": "https://schema.org", "@type": "FAQPage",
    "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs],
}, ensure_ascii=False, separators=(",", ":"))

# secțiune explicativă SEO (sub listă) — copie 1:1 cu glosar.html live
seo_section = f'''<section class="section" style="background:var(--bg-soft)"><div class="container" style="max-width:860px">
<h2 class="title" style="font-size:1.9rem">Ce este un glosar de termeni financiari și la ce te ajută</h2>
<p style="color:var(--muted);margin-top:14px">Un glosar de termeni financiari este un dicționar care explică, simplu și pe scurt, cuvintele pe care le întâlnești când e vorba de bani: de la dobândă, inflație și TVA, până la ETF, dividende sau grad de îndatorare. Scopul lui nu este să te transforme în specialist peste noapte, ci să-ți dea, în câteva secunde, înțelesul corect al unui termen atunci când îl citești într-un contract, un articol sau o ofertă bancară. Glosarul Clubul Financiar adună <strong>{count} {nd}termeni</strong> aranjați alfabetic, fiecare cu o definiție clară în limba română, fără jargon inutil.</p>

<h2 style="margin-top:26px">Cum folosești glosarul</h2>
<p style="color:var(--muted);margin-top:10px">Ai trei moduri de a găsi rapid ce cauți:</p>
<ul style="color:var(--muted);line-height:1.8;margin-top:8px">
  <li><strong>Caută</strong> — scrie cuvântul în câmpul de căutare de sus (de exemplu „dobândă", „ETF" sau „CASS") și lista se filtrează instant, fără diacritice obligatorii.</li>
  <li><strong>Sari la literă</strong> — apasă o literă din bara alfabetică (rămâne vizibilă la derulare) și pagina sare direct la termenii care încep cu ea.</li>
  <li><strong>Link direct</strong> — fiecare termen are propria ancoră, așa că poți trimite cuiva un link care sare exact la definiția dorită (de exemplu <code>/glosar#dobanda-compusa</code>).</li>
</ul>

<h2 style="margin-top:26px">Pe ce teme sunt grupați termenii</h2>
<p style="color:var(--muted);margin-top:10px">Termenii acoperă întreaga viață financiară a unui român: <strong>bugetul personal și economisirea</strong> (fond de urgență, abonamente recurente, regula 50/30/20), <strong>creditele și imobiliarele</strong> (DAE, grad de îndatorare, ipotecă, arvună), <strong>investițiile</strong> (acțiuni, ETF, obligațiuni, dividende, diversificare), <strong>taxele și statul</strong> (ANAF, TVA de 21%, impozit pe dividende de 16%, CASS), <strong>pensiile</strong> (Pilon II și III, VUAN) și <strong>psihologia banilor</strong> (efectul de ancorare, amânarea recompensei). Pentru fiecare temă găsești atât noțiunile de bază, cât și termeni mai avansați, explicați în același stil simplu.</p>

<h2 style="margin-top:26px">De la definiție la calcul concret</h2>
<p style="color:var(--muted);margin-top:10px">Un glosar îți spune <em>ce înseamnă</em> un termen, dar de multe ori vrei să vezi și <em>cât</em>. După ce înțelegi noțiunea, poți trece direct la cifre cu instrumentele noastre: testează puterea dobânzii compuse cu <a href="/calculatoare/dobanda-compusa">calculatorul de dobândă compusă</a>, vezi cât îți erodează inflația economiile cu <a href="/calculatoare/inflatie">calculatorul de inflație</a>, sau verifică-ți <a href="/calculatoare/grad-indatorare">gradul de îndatorare</a> înainte de un credit. Ai toate uneltele într-un singur loc în pagina <a href="/calculatoare">Calculatoare</a>, iar dacă vrei să înveți pas cu pas, începe cu secțiunile de <a href="/educatie">educație financiară</a> și <a href="/investitii">investiții</a>.</p>

<h2 style="margin-top:30px">Întrebări frecvente</h2>
<div style="margin-top:14px">
{faq_html}
</div>
</div></section>'''

# stil + buton „înapoi sus" + scriptul paginii (navigare pe litere cu ancore reale,
# bara alfabetică sticky, scrollspy, deep-link) — string simplu, NU f-string
TAIL = '''<button class="glos-top" id="glosTop" aria-label="Înapoi sus" title="Înapoi sus"><svg width="18" height="18" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3.5 9.75 8 5.25l4.5 4.5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
<style>
.glos-letter,.glos-card{scroll-margin-top:var(--glos-off,150px)}
@keyframes glosHit{0%{background:color-mix(in srgb,var(--emerald,#1c9e6b) 22%,transparent);box-shadow:0 0 0 3px color-mix(in srgb,var(--emerald,#1c9e6b) 55%,transparent)}100%{background:transparent;box-shadow:0 0 0 0 transparent}}
.glos-hit{animation:glosHit 2.4s ease-out;border-radius:14px}
/* bara alfabetică — sticky sub header, hairline auriu */
.glos-alphabar{position:sticky;top:var(--glos-nav-h,0px);z-index:900;padding:9px 0;
  background:color-mix(in srgb,var(--u-bg1,#f4efe3) 86%,transparent);
  -webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);
  border-bottom:1px solid var(--u-line-soft,rgba(168,134,49,.16))}
.glos-alphabar .glos-alpha{margin:0}
@media(max-width:720px){
  .glos-alphabar .glos-alpha{flex-wrap:nowrap;overflow-x:auto;justify-content:flex-start;padding-bottom:2px;scrollbar-width:none}
  .glos-alphabar .glos-alpha::-webkit-scrollbar{display:none}
  .glos-alphabar .glos-alpha button{flex:0 0 auto}
}
/* limbaj Ultra pe glosar */
.glos-alpha button{padding:1px 9px}
.u-page .glos-alpha button.active{color:#1a1304;font-weight:700}
.u-page .glos-letter{font-family:'Fraunces',Georgia,serif;font-weight:600;font-size:1.55rem;display:flex;align-items:center;gap:14px;margin:34px 0 4px}
.u-page .glos-letter::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--u-line,rgba(168,134,49,.3)),transparent)}
.u-page .glos-card h3{font-family:'Fraunces',Georgia,serif;font-weight:600}
/* buton discret „înapoi sus" */
.glos-top{position:fixed;right:20px;bottom:20px;z-index:950;width:44px;height:44px;border-radius:999px;
  display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;
  background:var(--u-panel,#fffdf9);color:var(--u-gold,#9a7414);
  border:1px solid var(--u-line,rgba(168,134,49,.30));box-shadow:0 12px 30px rgba(20,16,4,.16);
  opacity:0;visibility:hidden;transform:translateY(8px);transition:opacity .25s,transform .25s,visibility .25s}
.glos-top.show{opacity:1;visibility:visible;transform:none}
.glos-top:hover{border-color:var(--u-gold,#9a7414)}
@media(max-width:720px){.glos-top{right:14px;bottom:14px}}
</style>
<script>
const cards=[...document.querySelectorAll(".glos-card")];
const letters=[...document.querySelectorAll(".glos-letter")];
const q=document.getElementById("glosQ"), empty=document.getElementById("glosEmpty");
const alpha=document.getElementById("glosAlpha"), alphaBar=document.getElementById("glosAlphaBar");
const navEl=document.querySelector(".nav"), topBtn=document.getElementById("glosTop");
const abtns=[...alpha.querySelectorAll("button")];
const norm=s=>(s||"").toLowerCase().replace(/[ăâ]/g,"a").replace(/î/g,"i").replace(/ș|ş/g,"s").replace(/ț|ţ/g,"t");
const smooth=()=>matchMedia("(prefers-reduced-motion: reduce)").matches?"auto":"smooth";

/* offset ancore = header (doar dacă e sticky/fixed) + bara alfabetică sticky (recalculat la resize) */
function navFixed(){const p=navEl?getComputedStyle(navEl).position:"";return p==="sticky"||p==="fixed";}
function anchorOff(){return (navFixed()?navEl.offsetHeight:0)+(alphaBar?alphaBar.offsetHeight:0)+12;}
function setOffsets(){
  const r=document.documentElement.style;
  r.setProperty("--glos-off",anchorOff()+"px");
  r.setProperty("--glos-nav-h",(navFixed()?navEl.offsetHeight-1:0)+"px");
}
setOffsets(); addEventListener("resize",setOffsets);

function apply(){
  const term=norm(q.value.trim()); let shown=0;
  cards.forEach(c=>{const vis=!term||c.dataset.search.includes(term);c.style.display=vis?"":"none";if(vis)shown++;});
  letters.forEach(l=>{
    const L=l.id.replace("lit-","");
    const any=cards.some(c=>c.dataset.letter===L&&c.style.display!=="none");
    l.style.display=any?"":"none";
  });
  empty.hidden=shown>0;
  spy(true);
}
q.addEventListener("input",apply);

/* navigare pe litere: ancore reale #lit-A..#lit-Z + scrollspy pe litera curentă */
let spyTarget=null;
function setActive(L){
  if(alpha.dataset.cur===L)return; alpha.dataset.cur=L;
  abtns.forEach(x=>x.classList.toggle("active",x.dataset.l===L));
  const b=abtns.find(x=>x.dataset.l===L);
  if(b&&alpha.scrollWidth>alpha.clientWidth+4)
    alpha.scrollTo({left:b.offsetLeft-alpha.clientWidth/2+b.offsetWidth/2,behavior:"smooth"});
}
function currentLetter(){
  const off=anchorOff()+6; let cur="all";
  for(const l of letters){
    if(l.style.display==="none")continue;
    if(l.getBoundingClientRect().top<=off)cur=l.id.replace("lit-",""); else break;
  }
  return cur;
}
function spy(force){
  const cur=currentLetter();
  if(spyTarget){ if(cur===spyTarget||force){spyTarget=null;setActive(cur);} else setActive(spyTarget); return; }
  setActive(cur);
}
function goToLetter(L,behavior){
  if(q.value.trim()){q.value="";apply();}
  const el=L==="all"?null:document.getElementById("lit-"+L);
  if(L!=="all"&&!el)return;
  spyTarget=L; setActive(L);
  if(L==="all"){window.scrollTo({top:0,behavior:behavior||smooth()});return;}
  el.scrollIntoView({behavior:behavior||smooth(),block:"start"});
}
alpha.addEventListener("click",e=>{
  const b=e.target.closest("button"); if(!b||b.disabled)return;
  const L=b.dataset.l;
  goToLetter(L);
  history.replaceState(null,"",L==="all"?location.pathname+location.search:"#lit-"+L);
});

/* scrollspy + buton „înapoi sus" */
let tick=false;
addEventListener("scroll",()=>{
  if(tick)return; tick=true;
  requestAnimationFrame(()=>{tick=false;spy();topBtn.classList.toggle("show",scrollY>700);});
},{passive:true});
["wheel","touchstart"].forEach(ev=>addEventListener(ev,()=>{spyTarget=null;},{passive:true}));
topBtn.addEventListener("click",()=>{
  spyTarget="all";window.scrollTo({top:0,behavior:smooth()});
  history.replaceState(null,"",location.pathname+location.search);
});
spy();

/* Deep-link: /glosar#lit-B sare la literă; /glosar#slug sare direct la termen (fallback fuzzy) */
function glosResolve(slug){
  if(!slug) return null;
  slug=norm(slug.replace(/[#]/g,"").trim());
  let el=document.getElementById(slug);
  if(el&&el.classList.contains("glos-card")) return el;
  el=cards.find(c=>norm(c.id).startsWith(slug)); if(el) return el;      // prefix: fond-de-urgenta -> fond-de-urgenta-emergency-fund
  el=cards.find(c=>norm(c.id).includes(slug)); if(el) return el;        // conține
  const txt=slug.replace(/-/g," ");
  el=cards.find(c=>c.dataset.search.startsWith(txt))
     ||cards.find(c=>c.dataset.search.includes(txt));                   // după textul termenului
  return el||null;
}
function glosGoToHash(){
  const raw=decodeURIComponent((location.hash||"").replace(/^#/,""));
  const mL=raw.match(/^lit-([a-z])$/i);
  if(mL){goToLetter(mL[1].toUpperCase(),"auto");return;}
  const el=glosResolve(raw);
  if(!el) return;
  if(q.value){q.value="";apply();}          // asigură că termenul e vizibil (resetează căutarea)
  el.scrollIntoView({block:"start"});
  el.classList.remove("glos-hit"); void el.offsetWidth; el.classList.add("glos-hit");
}
window.addEventListener("hashchange",glosGoToHash);
if(location.hash) requestAnimationFrame(()=>requestAnimationFrame(glosGoToHash));
</script>
<script defer src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.108.2/dist/umd/supabase.js" integrity="sha384-nD3dwv4+ZqdYnmZKe/249ImlV04om7xTCcsoSeQYI+RO+XlKPoqAWaJR1M5SJH9p" crossorigin="anonymous"></script><script defer src="/assets/site.js?v=32"></script></body></html>'''

page = f'''<!DOCTYPE html><html lang="ro"><head>
<meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; base-uri 'self'; object-src 'none'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://maumjqciuxdbwjtvcpsy.supabase.co https://maumjqciuxdbwjtvcpsy.functions.supabase.co wss://maumjqciuxdbwjtvcpsy.supabase.co; form-action 'self'; frame-src 'self'; upgrade-insecure-requests"><meta name="referrer" content="strict-origin-when-cross-origin"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Glosar termeni financiari 2026 — Clubul Financiar</title>
<meta name="description" content="{desc}"><meta name="robots" content="index, follow"><meta name="theme-color" content="#10b981">
<link rel="canonical" href="https://clubulfinanciar.ro/glosar">
<link rel="icon" type="image/png" href="/favicon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website"><meta property="og:site_name" content="Clubul Financiar"><meta property="og:locale" content="ro_RO">
<meta property="og:title" content="Glosar termeni financiari 2026 — {count} {nd}definiții"><meta property="og:description" content="{desc}"><meta property="og:url" content="https://clubulfinanciar.ro/glosar"><meta property="og:image" content="https://clubulfinanciar.ro/og-image.jpg">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="Glosar termeni financiari 2026 — {count} {nd}definiții"><meta name="twitter:description" content="{desc}"><meta name="twitter:image" content="https://clubulfinanciar.ro/og-image.jpg">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"DefinedTermSet","name":"Glosar financiar Clubul Financiar","inLanguage":"ro-RO","url":"https://clubulfinanciar.ro/glosar"}}</script>
<script>(function(){{var t=localStorage.getItem("cf-theme");if(t)document.documentElement.setAttribute("data-theme",t);}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fraunces:opsz,ital,wght@9..144,0,400;9..144,0,600;9..144,1,400&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v=31">
<link rel="stylesheet" href="/assets/upgrade.css?v=30">
<link rel="stylesheet" href="/assets/cf-ultra.css?v=4"><script type="application/ld+json">{breadcrumb_ld}</script></head><body class="u-page">{NAV_HTML}
<section class="section-sm" style="background:var(--bg-soft)"><div class="container center">
<p class="eyebrow">Dicționar</p><h1 class="title">Glosar de termeni financiari</h1>
<p class="lead" style="margin-inline:auto">{count} {nd}termeni despre bani, investiții, credite și taxe — explicați pe înțelesul tuturor. Caută orice cuvânt sau sari direct la litera dorită.</p>
<div class="glos-search"><input type="search" id="glosQ" placeholder="Caută un termen… (ex: dobândă, ETF, CASS)" autocomplete="off"></div>
</div></section>
<div class="glos-alphabar" id="glosAlphaBar"><div class="container"><div class="glos-alpha" id="glosAlpha">{alpha_btns}</div></div></div>
<section class="section" style="padding-top:20px"><div class="container">
<div class="glos-list" id="glosList">
{list_html}
</div>
<p id="glosEmpty" class="search-hint" hidden>Niciun termen găsit. Încearcă alt cuvânt.</p>
<div style="max-width:820px;margin:34px auto 0"><div class="disc">⚠️ Definițiile au scop educativ și sunt simplificate pentru începători. Pentru decizii financiare consultă un specialist autorizat.</div></div>
</div></section>

{seo_section}

<script type="application/ld+json">{faq_ld}</script>

{FOOTER_HTML}
{TAIL}'''

open(OUT, "w", encoding="utf-8").write(page)
print(f"glosar.html scris: {count} termeni, {len(letters)} litere")
