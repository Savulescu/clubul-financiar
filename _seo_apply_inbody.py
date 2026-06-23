#!/usr/bin/env python3
"""_seo_apply_inbody.py — aplică REZULTATELE agenților (in-body links + meta + expand) pe articole.
Sigur: agentul NU atinge HTML; aici inserăm determinist, HTML-aware, cu validare + idempotent.
Citește SCRATCH/_seo_out_NNN.json (listă de {slug, inbody_links, meta_description, extra_section}).
"""
import json, re, html, os, glob

ROOT = "/Users/savulescucristian/clubul-financiar/docs"
ART = os.path.join(ROOT, "articole")
SCRATCH = "/private/tmp/claude-501/-Users-savulescucristian/2fc4c138-be21-4ac2-a94b-f866e8bfe4e1/scratchpad"

VALID = {os.path.basename(p)[:-5] for p in glob.glob(os.path.join(ART, "*.html"))}

def esc(s): return html.escape(s or "", quote=True)

def split_body(t):
    """întoarce (head_pre, body, tail) unde body = între </h1> și <section related>/<div disc>."""
    m = re.search(r"(</h1>)(.*?)(<section class=\"related\"|<div class=\"disc\")", t, re.S)
    if not m: return None
    return t[:m.start(2)], m.group(2), t[m.end(2):]

def wrap_first(body, anchor, slug):
    """învelește prima apariție a `anchor` în text liber (nu în <a>/<h1-3>). Idempotent la nivel articol."""
    parts = re.split(r"(<[^>]+>)", body)
    da = dh = 0; done = False; out = []
    for part in parts:
        if part.startswith("<"):
            low = part.lower()
            if low.startswith("<a"): da += 1
            elif low.startswith("</a"): da = max(0, da-1)
            elif re.match(r"<h[1-3][ >]", low): dh += 1
            elif re.match(r"</h[1-3]", low): dh = max(0, dh-1)
        elif not done and da == 0 and dh == 0 and anchor in part:
            i = part.find(anchor)
            part = (part[:i] + f'<a class="cf-ilink" href="/articole/{slug}">{anchor}</a>'
                    + part[i+len(anchor):])
            done = True
        out.append(part)
    return "".join(out), done

def set_meta(t, new):
    new_e = esc(new)
    for pat in (r'(<meta name="description" content=")[^"]*(")',
                r'(<meta property="og:description" content=")[^"]*(")',
                r'(<meta name="twitter:description" content=")[^"]*(")'):
        t = re.sub(pat, lambda m: m.group(1)+new_e+m.group(2), t, count=1)
    return t

def apply_article(slug, rec):
    p = os.path.join(ART, slug + ".html")
    if not os.path.exists(p): return None
    t = open(p, encoding="utf-8").read()
    orig = t
    note = []

    # ---- in-body links (o singură dată / articol) ----
    if "cf-ilink" not in t:
        sb = split_body(t)
        if sb:
            pre, body, tail = sb
            used = set(); n = 0
            for lk in (rec.get("inbody_links") or []):
                anc = (lk.get("anchor") or "").strip()
                tgt = (lk.get("target_slug") or "").strip()
                if not anc or len(anc) < 6 or tgt not in VALID or tgt == slug or tgt in used:
                    continue
                if f"/articole/{tgt}" in body:   # deja linkat în corp
                    continue
                body2, ok = wrap_first(body, anc, tgt)
                if ok:
                    body = body2; used.add(tgt); n += 1
                if n >= 3: break
            if n:
                t = pre + body + tail; note.append(f"{n} link-uri")

    # ---- meta description (rescrisă de agent) ----
    md = (rec.get("meta_description") or "").strip()
    if md and 50 <= len(md) <= 160:
        cur = re.search(r'<meta name="description" content="([^"]*)"', t)
        if cur and html.unescape(cur.group(1)) != md:
            t = set_meta(t, md); note.append("meta")

    # ---- expand (o secțiune nouă, doar dacă agentul a returnat) ----
    ex = rec.get("extra_section")
    if ex and "cf-expand" not in t and isinstance(ex, dict):
        heading = (ex.get("heading") or "").strip()
        bodyhtml = (ex.get("html") or "").strip()
        # acceptă doar conținut sigur (p/ul/ol/li/strong/em/h3/a interne)
        if heading and len(re.sub(r"<[^>]+>", "", bodyhtml)) > 200 and "<script" not in bodyhtml.lower():
            sec = f'<h2 class="cf-expand">{esc(heading)}</h2>{bodyhtml}'
            # secțiunea e CONȚINUT de articol -> înainte de disclaimer (în corp), nu după butonul back
            t = t.replace('<div class="disc"', sec + '<div class="disc"', 1); note.append("expand")

    if t != orig:
        open(p, "w", encoding="utf-8").write(t)
        return ", ".join(note)
    return None

def main():
    outs = sorted(glob.glob(os.path.join(SCRATCH, "_seo_out_*.json")))
    print(f"out-files: {len(outs)}")
    done = collections_count = 0
    stat = {"link": 0, "meta": 0, "expand": 0, "touched": 0, "articles": 0}
    for of in outs:
        try:
            recs = json.load(open(of, encoding="utf-8"))
        except Exception as e:
            print("  skip malformed", os.path.basename(of), e); continue
        for rec in recs:
            slug = rec.get("slug")
            if not slug: continue
            stat["articles"] += 1
            note = apply_article(slug, rec)
            if note:
                stat["touched"] += 1
                if "link" in note: stat["link"] += 1
                if "meta" in note: stat["meta"] += 1
                if "expand" in note: stat["expand"] += 1
    print(f"articole procesate: {stat['articles']} | modificate: {stat['touched']} "
          f"(linkuri:{stat['link']}, meta:{stat['meta']}, expand:{stat['expand']})")

if __name__ == "__main__":
    main()
