#!/usr/bin/env python3
"""_seo_pages2.py — completează SEO pe masterclass (200), despre/glosar/educatie + trim universal.
Idempotent. Breadcrumb pe paginile indexabile care încă nu îl au; trim meta description >160.
"""
import json, re, html, os, glob

ROOT = "/Users/savulescucristian/clubul-financiar/docs"
BASE = "https://clubulfinanciar.ro"

def esc(s): return html.escape(s or "", quote=True)
def ld(d): return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + '</script>'

def crumb(trail):
    return ld({"@context":"https://schema.org","@type":"BreadcrumbList",
        "itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"item":u}
                           for i,(n,u) in enumerate(trail)]})

def title_of(t, *strip):
    m = re.search(r"<title>(.*?)</title>", t, re.S)
    if not m: return ""
    s = html.unescape(m.group(1)).strip()
    for suf in (" — Clubul Financiar",) + strip:
        s = re.sub(re.escape(suf) + r"\s*$", "", s).strip()
    return s

def smart_trim(d, n=158):
    d = d.strip()
    return d if len(d) <= 160 else d[:n].rsplit(" ",1)[0].rstrip(" ,.;:–—-") + "…"

def trim_descs(t):
    for m in set(re.findall(r'<meta name="description" content="([^"]*)"', t)):
        u = html.unescape(m)
        if len(u) > 160:
            t = t.replace(f'content="{m}"', f'content="{esc(smart_trim(u))}"')
    return t

def add_before_head(t, block):
    return t.replace("</head>", block + "</head>", 1)

# ---------- masterclass (200) ----------
def do_masterclass():
    n = nt = 0
    for p in glob.glob(os.path.join(ROOT, "masterclass", "*.html")):
        t = open(p, encoding="utf-8").read()
        if "noindex" in t.lower(): continue
        slug = os.path.basename(p)[:-5]
        url = f"{BASE}/masterclass/{slug}"
        orig = t
        if '"BreadcrumbList"' not in t:
            name = title_of(t, " — Masterclass Bursă", " — Masterclass")
            t = add_before_head(t, crumb([("Acasă",BASE+"/"),("Masterclass",BASE+"/masterclass"),(name,url)]))
            n += 1
        t2 = trim_descs(t)
        if t2 != t: nt += 1
        t = t2
        if t != orig: open(p,"w",encoding="utf-8").write(t)
    print(f"masterclass: breadcrumb +{n}, desc-trim {nt}")

# ---------- despre / glosar / educatie ----------
LANDING2 = {
    "despre.html":   ("AboutPage",      "Despre"),
    "glosar.html":   ("CollectionPage", "Glosar financiar"),
    "educatie.html": None,  # are deja CollectionPage; doar breadcrumb
}
def do_landing2():
    for fn, cfg in LANDING2.items():
        p = os.path.join(ROOT, fn)
        if not os.path.exists(p): continue
        t = open(p, encoding="utf-8").read()
        if '"BreadcrumbList"' in t: continue
        url = f"{BASE}/{fn[:-5]}"
        name = title_of(t)
        block = crumb([("Acasă",BASE+"/"),(name,url)])
        t = add_before_head(t, block)
        open(p,"w",encoding="utf-8").write(t)
        print(f"{fn}: breadcrumb adăugat")

# ---------- trim universal pe paginile indexabile ----------
def do_trim_all():
    n = 0
    for p in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        if "/_" in p or "/articole/" in p: continue
        t = open(p, encoding="utf-8").read()
        if "noindex" in t.lower(): continue
        t2 = trim_descs(t)
        if t2 != t: open(p,"w",encoding="utf-8").write(t2); n += 1
    print(f"trim universal: {n} pagini")

if __name__ == "__main__":
    do_masterclass()
    do_landing2()
    do_trim_all()
    print("DONE pages2")
