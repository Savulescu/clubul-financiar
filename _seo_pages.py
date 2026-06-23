#!/usr/bin/env python3
"""_seo_pages.py — schema/meta pe paginile non-articol (landing, calculatoare, statice).
Idempotent. Adaugă JSON-LD (WebApplication/CollectionPage/ContactPage/WebPage + BreadcrumbList),
repară terms/privacy (description+canonical+OG), noindex pe preview-uri newsletter,
trim meta description >160 pe toate paginile non-articol.
"""
import json, re, html, os, glob

ROOT = "/Users/savulescucristian/clubul-financiar/docs"
BASE = "https://clubulfinanciar.ro"

def esc(s): return html.escape(s or "", quote=True)

def get_title(t):
    m = re.search(r"<title>(.*?)</title>", t, re.S)
    if not m: return ""
    return html.unescape(re.sub(r"\s*—\s*Clubul Financiar\s*$", "", m.group(1)).strip())

def get_desc(t):
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    return html.unescape(m.group(1)) if m else ""

def ld(d):
    return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + '</script>'

def breadcrumb(trail):
    return {"@context":"https://schema.org","@type":"BreadcrumbList",
        "itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":u}
                           for i,(n,u) in enumerate(trail)]}

def inject_head(t, blocks):
    """adaugă blocuri (string-uri) înainte de </head> dacă tipurile lor nu există deja."""
    add = []
    for b in blocks:
        tm = re.search(r'"@type":\s*"([A-Za-z]+)"', b)
        typ = tm.group(1) if tm else None
        if typ and f'"@type":"{typ}"' in t.replace(" ", "") :
            continue
        add.append(b)
    if not add: return t, False
    return t.replace("</head>", "".join(add) + "</head>", 1), True

def smart_trim(d, n=158):
    d = d.strip()
    if len(d) <= 160: return d
    return d[:n].rsplit(" ",1)[0].rstrip(" ,.;:–—-") + "…"

def trim_descs(t):
    changed = False
    for m in re.findall(r'<meta name="description" content="([^"]*)"', t):
        u = html.unescape(m)
        if len(u) > 160:
            t = t.replace(f'content="{m}"', f'content="{esc(smart_trim(u))}"'); changed = True
    return t, changed

CALCS = {
    "dobanda-compusa":"Calculator dobândă compusă","credit":"Calculator rată credit",
    "salariu-net":"Calculator salariu net","economii":"Calculator economii",
    "inflatie":"Calculator inflație","fire":"Calculator FIRE",
    "grad-indatorare":"Calculator grad de îndatorare","obiectiv-economisire":"Calculator obiectiv de economisire",
    "chirie-vs-cumparare":"Calculator chirie vs cumpărare","pensie":"Calculator pensie",
    "impozit-investitii":"Calculator impozit investiții",
}

def do_calculators():
    n = 0
    for slug, name in CALCS.items():
        p = os.path.join(ROOT, "calculatoare", slug + ".html")
        if not os.path.exists(p): continue
        t = open(p, encoding="utf-8").read()
        url = f"{BASE}/calculatoare/{slug}"
        webapp = ld({"@context":"https://schema.org","@type":"WebApplication","name":name,"url":url,
            "applicationCategory":"FinanceApplication","operatingSystem":"Web","inLanguage":"ro-RO",
            "isAccessibleForFree":True,"offers":{"@type":"Offer","price":"0","priceCurrency":"RON"},
            "description":get_desc(t) or name,
            "publisher":{"@type":"Organization","name":"Clubul Financiar","url":BASE}})
        bc = ld(breadcrumb([("Acasă",BASE+"/"),("Calculatoare",BASE+"/calculatoare"),(name,url)]))
        t2, ch = inject_head(t, [webapp, bc])
        t2, _ = trim_descs(t2)
        if t2 != t: open(p,"w",encoding="utf-8").write(t2); n += 1
    print(f"calculatoare: {n} actualizate")

# landing -> (tip, breadcrumb-nume)
LANDING = {
    "calculatoare.html": ("CollectionPage","Calculatoare"),
    "teste.html": ("CollectionPage","Teste"),
    "masterclass.html": ("CollectionPage","Masterclass"),
    "instrumente.html": ("CollectionPage","Instrumente"),
    "incepe-aici.html": ("WebPage","Începe aici"),
    "stiri.html": ("CollectionPage","Știri"),
    "stiri-externe.html": ("CollectionPage","Știri externe"),
    "premium.html": ("WebPage","Premium"),
    "contact.html": ("ContactPage","Contact"),
    "feedback.html": ("WebPage","Feedback"),
}

def do_landing():
    n = 0
    for fn, (typ, name) in LANDING.items():
        p = os.path.join(ROOT, fn)
        if not os.path.exists(p): continue
        t = open(p, encoding="utf-8").read()
        slug = fn[:-5]
        url = f"{BASE}/{slug}"
        page = ld({"@context":"https://schema.org","@type":typ,"name":get_title(t) or name,"url":url,
            "inLanguage":"ro-RO","description":get_desc(t) or name,
            "isPartOf":{"@type":"WebSite","name":"Clubul Financiar","url":BASE}})
        bc = ld(breadcrumb([("Acasă",BASE+"/"),(name,url)]))
        t2, _ = inject_head(t, [page, bc])
        t2, _ = trim_descs(t2)
        if t2 != t: open(p,"w",encoding="utf-8").write(t2); n += 1
    print(f"landing: {n} actualizate")

def do_tool():
    p = os.path.join(ROOT, "unelte", "plan-anti-datorii.html")
    if not os.path.exists(p): return
    t = open(p, encoding="utf-8").read()
    url = f"{BASE}/unelte/plan-anti-datorii"
    name = get_title(t) or "Plan anti-datorii"
    webapp = ld({"@context":"https://schema.org","@type":"WebApplication","name":name,"url":url,
        "applicationCategory":"FinanceApplication","operatingSystem":"Web","inLanguage":"ro-RO",
        "isAccessibleForFree":True,"description":get_desc(t) or name,
        "publisher":{"@type":"Organization","name":"Clubul Financiar","url":BASE}})
    bc = ld(breadcrumb([("Acasă",BASE+"/"),("Instrumente",BASE+"/instrumente"),(name,url)]))
    t2, ch = inject_head(t, [webapp, bc])
    t2, _ = trim_descs(t2)
    if t2 != t: open(p,"w",encoding="utf-8").write(t2); print("unelte/plan-anti-datorii: OK")

def do_newsletter_noindex():
    n = 0
    for p in glob.glob(os.path.join(ROOT, "newsletter", "preview", "*.html")):
        t = open(p, encoding="utf-8").read()
        if "noindex" in t: continue
        if '<meta name="robots"' in t:
            t = re.sub(r'<meta name="robots" content="[^"]*"', '<meta name="robots" content="noindex, follow"', t)
        else:
            t = t.replace("</title>", '</title><meta name="robots" content="noindex, follow">', 1)
        open(p,"w",encoding="utf-8").write(t); n += 1
    print(f"newsletter preview noindex: {n}")

STATIC = {
    "terms.html": ("Termeni și condiții","Termenii și condițiile de utilizare a platformei Clubul Financiar — educație financiară gratuită și conținut informativ."),
    "privacy.html": ("Politica de confidențialitate","Cum colectăm, folosim și protejăm datele tale pe Clubul Financiar. Politica de confidențialitate completă."),
}

def do_static():
    n = 0
    for fn, (name, desc) in STATIC.items():
        p = os.path.join(ROOT, fn)
        if not os.path.exists(p): continue
        t = open(p, encoding="utf-8").read()
        url = f"{BASE}/{fn[:-5]}"
        head_add = ""
        if '<meta name="description"' not in t:
            head_add += f'<meta name="description" content="{esc(desc)}">'
        if 'rel="canonical"' not in t:
            head_add += f'<link rel="canonical" href="{url}">'
        if 'og:title' not in t:
            head_add += (f'<meta property="og:type" content="website"><meta property="og:site_name" content="Clubul Financiar">'
                         f'<meta property="og:locale" content="ro_RO"><meta property="og:title" content="{esc(name)}">'
                         f'<meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}">'
                         f'<meta property="og:image" content="{BASE}/og-image.jpg">')
        if head_add and "<title>" in t:
            t = re.sub(r'(</title>)', r'\1' + head_add, t, count=1)
        bc = ld(breadcrumb([("Acasă",BASE+"/"),(name,url)]))
        wp = ld({"@context":"https://schema.org","@type":"WebPage","name":name,"url":url,
                 "inLanguage":"ro-RO","description":desc})
        t, _ = inject_head(t, [wp, bc])
        open(p,"w",encoding="utf-8").write(t); n += 1
    print(f"static (terms/privacy): {n}")

if __name__ == "__main__":
    do_calculators()
    do_landing()
    do_tool()
    do_newsletter_noindex()
    do_static()
    print("DONE pages")
