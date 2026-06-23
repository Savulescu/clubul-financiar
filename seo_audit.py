#!/usr/bin/env python3
"""seo_audit.py — audit SEO pe tot site-ul (docs/). Rulează: python3 seo_audit.py
Raportează: title/description/canonical/h1/OG/JSON-LD lipsă, titluri/descrieri duplicate,
pagini lipsă din sitemap, descrieri prea scurte/lungi. NU modifică nimic."""
import re, glob, os, collections
BASE="https://clubulfinanciar.ro"
sm=open("docs/sitemap.xml",encoding="utf-8").read() if os.path.exists("docs/sitemap.xml") else ""
files=[f for f in glob.glob("docs/**/*.html",recursive=True) if "/_" not in f and "_src" not in f]
def g(h,p):
    m=re.search(p,h,re.I|re.S); return m.group(1).strip() if m else None
titles=collections.Counter(); descs=collections.Counter()
issues=collections.Counter(); flagged=[]
for f in files:
    h=open(f,encoding="utf-8").read()
    rel="/"+os.path.relpath(f,"docs").replace("\\","/")
    url=BASE+("/" if rel=="/" else rel)
    if re.search(r'noindex',h,re.I): continue  # sar paginile noindex (redirecturi)
    t=g(h,r'<title>([^<]*)</title>'); d=g(h,r'<meta name="description" content="([^"]*)"')
    can=g(h,r'rel="canonical"\s+href="([^"]*)"') or g(h,r'href="([^"]*)"\s+rel="canonical"')
    h1=len(re.findall(r'<h1[ >]',h)); og=('og:title' in h); ld=('application/ld+json' in h)
    # numără linkuri interne către alte articole (semnal de internal linking)
    inter = len(re.findall(r'href="/articole/[^"#]+', h))
    probs=[]
    if not t: probs.append("fără title"); issues["title lipsă"]+=1
    elif not(25<=len(t)<=70): pass
    if t: titles[t]+=1
    if not d: probs.append("fără meta description"); issues["desc lipsă"]+=1
    elif not(60<=len(d)<=170): probs.append(f"desc {len(d)} car"); issues["desc lungime"]+=1
    if d: descs[d]+=1
    if not can: probs.append("fără canonical"); issues["canonical lipsă"]+=1
    if h1!=1: probs.append(f"{h1} h1"); issues["h1 != 1"]+=1
    if not og: probs.append("fără OG"); issues["OG lipsă"]+=1
    if not ld: issues["JSON-LD lipsă"]+=1
    if '"BreadcrumbList"' not in h: issues["Breadcrumb lipsă"]+=1
    if "/articole/" in rel and inter==0: issues["fără internal-link art→art"]+=1
    # in sitemap? — site-ul folosește URL-uri curate (fără .html / fără /index.html)
    clean = re.sub(r'/index\.html$','/',rel); clean = re.sub(r'\.html$','',clean)
    clean_url = BASE+clean
    in_sm = any(x in sm for x in (url, rel, clean, clean_url, "<loc>"+clean_url+"</loc>"))
    if not in_sm and not any(x in rel for x in ["/login","/reset","/account","/statistici","/privacy","/terms","/contact","/dezabonare","/feedback","/newsletter/","/_"]):
        probs.append("LIPSĂ din sitemap"); issues["lipsă sitemap"]+=1
    if probs: flagged.append((rel,probs))
dup_t=[(t,n) for t,n in titles.items() if n>1]
dup_d=[(d,n) for d,n in descs.items() if n>1]
print(f"=== AUDIT SEO — {len(files)} pagini ===")
print("\nSUMAR probleme:")
for k,v in issues.most_common(): print(f"  {v:>5}  {k}")
print(f"\nTitluri duplicate: {len(dup_t)} | Descrieri duplicate: {len(dup_d)}")
for t,n in sorted(dup_t,key=lambda x:-x[1])[:5]: print(f"  {n}× «{t[:60]}»")
print(f"\nPagini cu probleme: {len(flagged)} (primele 25):")
for rel,probs in flagged[:25]: print(f"  {rel}: {', '.join(probs)}")
