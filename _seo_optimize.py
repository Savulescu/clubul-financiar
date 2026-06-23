#!/usr/bin/env python3
"""_seo_optimize.py — optimizare SEO deterministă pe articole (docs/articole/*.html).
Idempotent (markeri): rulabil de oricâte ori fără dublări.
  D1  internal linking semantic: <section class="related" data-cf-related> (6 articole)
  D2  BreadcrumbList JSON-LD (Acasă > Educație > Categorie > Articol)
  D3  trim meta description >160 car (description + og + twitter, sincron)
Output: _seo_candidates.json (slug -> top 12 articole înrudite) pentru pasul cu agenți.
NU atinge cursurile (noindex). NU regenerează corpul; doar adaugă/ajustează.
"""
import json, re, html, os, glob, math, collections, unicodedata

ROOT = "/Users/savulescucristian/clubul-financiar/docs"
ART = os.path.join(ROOT, "articole")
BASE = "https://clubulfinanciar.ro"
CAND_OUT = "/Users/savulescucristian/clubul-financiar/_seo_candidates.json"

# categorie -> nume curat (fără emoji, pentru schema + carduri)
CATNAME = {
    "buget":"Buget personal","economii":"Economii","datorii":"Datorii","psihologie":"Psihologia banilor",
    "venituri":"Venituri","investitii":"Investiții","credite":"Credite","economie":"Economie",
    "antreprenoriat":"Antreprenoriat","imobiliare":"Imobiliare","crypto":"Criptomonede","taxe":"Taxe & ANAF",
    "pensii":"Pensii","asigurari":"Asigurări","planificare":"Planificare financiară","siguranta":"Siguranță & fraude",
    "fire":"Independență financiară (FIRE)",
}

RO_STOP = set("""a ai al ale altul am ar are as asta astea astfel asupra au avea avem aveti avut ca cam cand care
carei carele cari caror carora cat catre ce cea ceea cei cel cele celor ceva chiar cinci cine cineva contra cu cui cum
cumva da daca dar dat dau de deci deja desi despre din dintr dintre doar doi din dupa ea ei el ele era erau esti este
eu face fara fata fie fiecare fii fim fiu fost frumos i ia iar ii il imi in inainte inapoi inca incat insa intr intre
isi iti l la le li lor lui m ma mai mea mei mele mereu meu mi mie mine mult multa multe multi n neni nici niste noi noastra
noastre nostri nostru nou noua o opt or ori oricare orice oricine oricum oriunde pai pana patru pe pentru peste pic poate
prea prima primul prin printr putea ca sa sa sai sale sau se si sint sintem sinteti spre sub sunt suntem sunteti ta tale te
ti tine toata toate tot toti totul totusi tu tuturor un una unde undeva unei uneia unele uneori unii unor unora unu unui unul
va vi voastra voastre voi vom vor vostru vreo vreun toata catva chiar fel""".split())
RO_STOP |= set(["lei","ron","an","ani","luna","lunar","cum","ce","face","poti","trebuie","mod","cazul","cazuri",
                "exemplu","euro","mai","mult","caz","care","cele","tot","face","doua","doar"])

def fold(s):
    s = (s or "").lower()
    return (s.replace("ă","a").replace("â","a").replace("î","i")
             .replace("ș","s").replace("ş","s").replace("ț","t").replace("ţ","t"))

def tokens(s):
    s = fold(s)
    return [w for w in re.split(r"[^a-z0-9]+", s) if len(w) >= 3 and w not in RO_STOP and not w.isdigit()]

def esc(s):
    return html.escape(s or "", quote=True)

def strip_tags(s):
    return re.sub(r"<[^>]+>", " ", s)

# ---------- 1. încarcă toate articolele ----------
def load_articles():
    arts = {}
    for p in sorted(glob.glob(os.path.join(ART, "*.html"))):
        if os.path.basename(p).startswith("_"):
            continue
        t = open(p, encoding="utf-8").read()
        if re.search(r'name="robots" content="noindex', t):
            continue
        slug = os.path.basename(p)[:-5]
        mt = re.search(r'<meta property="og:title" content="([^"]*)"', t) or re.search(r"<title>([^<]*?)(?: —|</title>)", t)
        md = re.search(r'<meta name="description" content="([^"]*)"', t)
        mc = re.search(r'educatie(?:\.html)?#([a-z]+)"', t)
        bm = re.search(r"</h1>(.*?)<div class=\"disc\"", t, re.S)
        body = bm.group(1) if bm else ""
        heads = " ".join(re.findall(r"<h2[^>]*>(.*?)</h2>", body, re.S))
        arts[slug] = {
            "slug": slug, "path": p, "html": t,
            "title": html.unescape(mt.group(1)) if mt else slug,
            "desc": html.unescape(md.group(1)) if md else "",
            "cat": mc.group(1) if mc else "planificare",
            "body_text": strip_tags(body), "heads": html.unescape(strip_tags(heads)),
            "words": len(strip_tags(body).split()),
        }
    return arts

# ---------- 2. TF-IDF + cosine prin index inversat ----------
def build_similarity(arts):
    slugs = list(arts.keys())
    N = len(slugs)
    tf = {}        # slug -> {term: weighted_count}
    df = collections.Counter()
    for s in slugs:
        a = arts[s]
        bag = collections.Counter()
        for term in tokens(a["title"]): bag[term] += 3
        for term in tokens(a["heads"]): bag[term] += 2
        for term in tokens(a["desc"]):  bag[term] += 2
        for term in tokens(a["body_text"]): bag[term] += 1
        tf[s] = bag
        for term in bag: df[term] += 1
    idf = {term: math.log(N / dfc) for term, dfc in df.items()}
    # vectori normalizați + index inversat (ignoră termeni prea comuni)
    vec = {}; norm = {}; inv = collections.defaultdict(list)
    for s in slugs:
        v = {}
        for term, c in tf[s].items():
            if df[term] >= N * 0.5:   # termen aproape universal -> zgomot
                continue
            v[term] = (1 + math.log(c)) * idf[term]
        nrm = math.sqrt(sum(w*w for w in v.values())) or 1.0
        vec[s] = v; norm[s] = nrm
        for term, w in v.items():
            inv[term].append((s, w))
    related = {}
    for s in slugs:
        scores = collections.defaultdict(float)
        for term, w in vec[s].items():
            for (s2, w2) in inv[term]:
                if s2 != s:
                    scores[s2] += w * w2
        ranked = []
        for s2, dot in scores.items():
            cos = dot / (norm[s] * norm[s2])
            if arts[s2]["cat"] == arts[s]["cat"]:
                cos *= 1.12   # ușor boost aceeași categorie (coerență tematică)
            ranked.append((cos, s2))
        ranked.sort(reverse=True)
        related[s] = [s2 for _, s2 in ranked[:14]]
    return related

# ---------- 3. injectoare ----------
def breadcrumb_ld(a):
    catn = CATNAME.get(a["cat"], a["cat"])
    data = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Acasă","item":f"{BASE}/"},
        {"@type":"ListItem","position":2,"name":"Educație","item":f"{BASE}/educatie"},
        {"@type":"ListItem","position":3,"name":catn,"item":f"{BASE}/educatie#{a['cat']}"},
        {"@type":"ListItem","position":4,"name":a["title"],"item":f"{BASE}/articole/{a['slug']}"},
    ]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'

def related_section(arts, slug, rel_slugs):
    pick = rel_slugs[:6]
    if not pick:
        return ""
    cards = "".join(
        f'<a class="card" href="/articole/{s}"><h3>{esc(arts[s]["title"])}</h3>'
        f'<p>{esc(arts[s]["desc"])}</p><span class="more">Citește</span></a>'
        for s in pick)
    return ('<section class="related" data-cf-related="1">'
            '<h2 class="title" style="font-size:1.4rem">Articole conexe</h2>'
            f'<div class="related-grid">{cards}</div></section>')

def smart_trim(d, n=158):
    d = d.strip()
    if len(d) <= 160:
        return d
    cut = d[:n].rsplit(" ", 1)[0].rstrip(" ,.;:–—-")
    return cut + "…"

def trim_meta(t):
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    if not m:
        return t, False
    old = m.group(1)
    if len(html.unescape(old)) <= 160:
        return t, False
    new = esc(smart_trim(html.unescape(old)))
    # sincronizează cele 3 locuri care folosesc fix acest string
    changed = t.replace(f'content="{old}"', f'content="{new}"')
    return changed, changed != t

# ---------- 4. rulează ----------
def main():
    arts = load_articles()
    print(f"Articole indexabile: {len(arts)}")
    related = build_similarity(arts)
    json.dump({s: [{"slug": r, "title": arts[r]["title"], "cat": arts[r]["cat"]}
                   for r in related[s][:12]] for s in arts},
              open(CAND_OUT, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"_seo_candidates.json scris ({len(arts)} sloturi)")

    n_bc = n_rel = n_trim = 0
    for slug, a in arts.items():
        t = a["html"]
        # D2 breadcrumb
        if '"BreadcrumbList"' not in t:
            t = t.replace("</head>", breadcrumb_ld(a) + "</head>", 1); n_bc += 1
        # D1 related (server-side, după </article> back-button => în afara gating-ului premium)
        if 'data-cf-related' not in t:
            sec = related_section(arts, slug, related[slug])
            if sec:
                t = t.replace("</article>", sec + "</article>", 1); n_rel += 1
        # D3 trim meta
        t, did = trim_meta(t)
        if did: n_trim += 1
        if t != a["html"]:
            open(a["path"], "w", encoding="utf-8").write(t)
    print(f"Breadcrumb adăugat: {n_bc} | Related adăugat: {n_rel} | Meta trim: {n_trim}")

if __name__ == "__main__":
    main()
