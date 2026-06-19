#!/usr/bin/env python3
import json, re, html, unicodedata, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shell import NAV_HTML, FOOTER_HTML  # nav+footer pre-randate static

SRC = "/private/tmp/claude-501/-Users-savulescucristian/2d8bd220-1ab9-4311-b6f9-e180142ffdfa/tasks/wu28oa28b.output"
OUT = "/Users/savulescucristian/clubul-financiar/docs/glosar.html"

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
desc = f"Glosar financiar — {count} de termeni despre bani, investiții, credite, taxe și economie, explicați simplu pentru începători."

page = f'''<!DOCTYPE html><html lang="ro"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Glosar financiar — {count} de termeni explicați simplu — Clubul Financiar</title>
<meta name="description" content="{desc}"><meta name="robots" content="index, follow"><meta name="theme-color" content="#10b981">
<link rel="canonical" href="https://clubulfinanciar.ro/glosar.html">
<link rel="icon" type="image/png" href="/favicon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="website"><meta property="og:site_name" content="Clubul Financiar"><meta property="og:locale" content="ro_RO">
<meta property="og:title" content="Glosar financiar — termeni explicați simplu"><meta property="og:description" content="{desc}"><meta property="og:url" content="https://clubulfinanciar.ro/glosar.html"><meta property="og:image" content="https://clubulfinanciar.ro/og-image.jpg">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="Glosar financiar — termeni explicați simplu"><meta name="twitter:image" content="https://clubulfinanciar.ro/og-image.jpg">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"DefinedTermSet","name":"Glosar financiar Clubul Financiar","inLanguage":"ro-RO","url":"https://clubulfinanciar.ro/glosar.html"}}</script>
<script>(function(){{var t=localStorage.getItem("cf-theme");if(t)document.documentElement.setAttribute("data-theme",t);}})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400..800&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v=21">
<link rel="stylesheet" href="/assets/upgrade.css?v=21"></head><body>{NAV_HTML}
<section class="section-sm" style="background:var(--bg-soft)"><div class="container center">
<p class="eyebrow">Dicționar</p><h1 class="title">Glosar financiar</h1>
<p class="lead" style="margin-inline:auto">{count} de termeni despre bani, investiții, credite și taxe — explicați pe înțelesul tuturor.</p>
<div class="glos-search"><input type="search" id="glosQ" placeholder="Caută un termen… (ex: dobândă, ETF, CASS)" autocomplete="off"></div>
<div class="glos-alpha" id="glosAlpha">{alpha_btns}</div>
</div></section>
<section class="section" style="padding-top:20px"><div class="container">
<div class="glos-list" id="glosList">
{list_html}
</div>
<p id="glosEmpty" class="search-hint" hidden>Niciun termen găsit. Încearcă alt cuvânt.</p>
<div style="max-width:820px;margin:34px auto 0"><div class="disc">⚠️ Definițiile au scop educativ și sunt simplificate pentru începători. Pentru decizii financiare consultă un specialist autorizat.</div></div>
</div></section>
{FOOTER_HTML}
<script>
const cards=[...document.querySelectorAll(".glos-card")];
const letters=[...document.querySelectorAll(".glos-letter")];
const q=document.getElementById("glosQ"), empty=document.getElementById("glosEmpty");
const alpha=document.getElementById("glosAlpha");
const norm=s=>(s||"").toLowerCase().replace(/[ăâ]/g,"a").replace(/î/g,"i").replace(/ș|ş/g,"s").replace(/ț|ţ/g,"t");
let curL="all";
function apply(){{
  const term=norm(q.value.trim()); let shown=0;
  cards.forEach(c=>{{
    const okL=curL==="all"||c.dataset.letter===curL;
    const okQ=!term||c.dataset.search.includes(term);
    const vis=okL&&okQ; c.style.display=vis?"":"none"; if(vis)shown++;
  }});
  letters.forEach(l=>{{
    const L=l.id.replace("lit-","");
    const any=cards.some(c=>c.dataset.letter===L&&c.style.display!=="none");
    l.style.display=any?"":"none";
  }});
  empty.hidden=shown>0;
}}
alpha.addEventListener("click",e=>{{
  const b=e.target.closest("button"); if(!b||b.disabled)return;
  curL=b.dataset.l; [...alpha.children].forEach(x=>x.classList.remove("active")); b.classList.add("active");
  if(curL!=="all"){{const el=document.getElementById("lit-"+curL); }} apply();
}});
q.addEventListener("input",()=>{{ if(q.value.trim()){{curL="all";[...alpha.children].forEach(x=>x.classList.remove("active"));alpha.firstElementChild.classList.add("active");}} apply(); }});
</script>
<script defer src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script><script defer src="/assets/site.js?v=21"></script></body></html>'''

open(OUT, "w", encoding="utf-8").write(page)
print(f"glosar.html scris: {count} termeni, {len(letters)} litere")
