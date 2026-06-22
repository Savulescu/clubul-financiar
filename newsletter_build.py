#!/usr/bin/env python3
# =============================================================================
# newsletter_build.py — generează newsletterele pe tieruri (Free/Premium/Pro/Ultra)
# după strategia din _audits/NEWSLETTER_STRATEGY_2026-06-22.md.
#   Free „Dimineața pe scurt"  — determinist din date (BNR + dividende + știri + macro + glosar)
#   Premium „Ordinea din zgomot" — voce de autor (LLM, fallback templat)
#   Pro „Masa de lucru"        — acționabil + calendar dividende (LLM, fallback)
#   Ultra „Raportul tău"       — personalizat (demo aici; live = per-user din ultra_profile)
#
# TRIMITERE GATED: implicit doar PREVIEW (scrie HTML în docs/newsletter/preview/).
#   --test EMAIL   → trimite varianta Free la o singură adresă (test).
#   --send TIER    → trimite live abonaților tierului (NECESITĂ RESEND_API_KEY + Supabase).
# Fără dependențe externe (urllib). LLM-ul reutilizează providerii din news_external.py.
# =============================================================================
import os, sys, json, html, datetime, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "docs", "data")
PREVIEW = os.path.join(ROOT, "docs", "newsletter", "preview")
SITE = "https://clubulfinanciar.ro"

RESEND = os.environ.get("RESEND_API_KEY", "")
FROM = os.environ.get("NEWSLETTER_FROM", "Clubul Financiar <noreply@clubulfinanciar.ro>")
SB_URL = os.environ.get("SUPABASE_URL", "https://maumjqciuxdbwjtvcpsy.supabase.co")
SB_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# paleta (inline, email-safe)
NAVY = "#0e2750"; NAVY2 = "#081627"; PANEL = "#0f2238"; GOLD = "#E8C268"; GOLD2 = "#caa44a"
INK = "#eaf1fb"; MUT = "#93a7c4"; LINE = "rgba(232,194,104,.24)"; POS = "#19c08a"; NEG = "#ef6b62"
SERIF = "Georgia,'Times New Roman',serif"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"

# blue-chips lichide RO (pt radarul de dividende — evită micro-cap-uri cu randamente distorsionate)
BIG_TICKERS = ["H2O","SNN","SNP","TGN","TLV","SNG","BRD","EL","DIGI","FP","TEL","ATB","TTS","M","SNN","COTE","ONE","AQ","WINE","SFG"]
LUNI = ["ianuarie","februarie","martie","aprilie","mai","iunie","iulie","august","septembrie","octombrie","noiembrie","decembrie"]
ZILE = ["luni","marți","miercuri","joi","vineri","sâmbătă","duminică"]


def load(name, default=None):
    try:
        return json.load(open(os.path.join(DATA, name), encoding="utf-8"))
    except Exception:
        return default if default is not None else {}


def glosar():
    try:
        return json.load(open(os.path.join(ROOT, "_data", "glosar.json"), encoding="utf-8"))
    except Exception:
        return []


def lei(x, dec=2):
    try:
        s = f"{float(x):,.{dec}f}".replace(",", " ").replace(".", ",")
        return s
    except Exception:
        return str(x)


def data_ro(d=None):
    d = d or datetime.date.today()
    return f"{ZILE[d.weekday()]}, {d.day} {LUNI[d.month-1]} {d.year}"


# ---------- LLM opțional (reutilizează providerii free din news_external.py) ----------
def llm(messages, max_tokens=900):
    try:
        sys.path.insert(0, ROOT)
        from news_external import chat
        return chat(messages, max_tokens=max_tokens).get("content", "").strip()
    except Exception as e:
        print("  LLM indisponibil:", str(e)[:80])
        return ""


# ---------- shell email comun ----------
def shell(title, eyebrow, inner, accent_cta=True):
    cta = f'''
      <tr><td style="padding:8px 28px 30px">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
          <td align="center" style="border-radius:12px;background:linear-gradient(135deg,{GOLD},{GOLD2})">
            <a href="{SITE}/premium.html" style="display:inline-block;padding:13px 26px;font-family:{SANS};font-weight:800;font-size:14px;color:#1a1304;text-decoration:none">Vezi planurile →</a>
          </td></tr></table>
      </td></tr>''' if accent_cta else ""
    return f'''<!DOCTYPE html><html lang="ro"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark"><title>{html.escape(title)}</title></head>
<body style="margin:0;padding:0;background:{NAVY2};-webkit-text-size-adjust:100%">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{NAVY2}"><tr><td align="center" style="padding:24px 12px">
  <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:{NAVY};border:1px solid {LINE};border-radius:18px;overflow:hidden">
    <tr><td style="height:3px;background:linear-gradient(90deg,transparent,{GOLD2},transparent)"></td></tr>
    <tr><td style="padding:26px 28px 6px">
      <div style="font-family:{SERIF};letter-spacing:.18em;text-transform:uppercase;font-size:11px;color:{GOLD};font-weight:bold">Clubul Financiar</div>
      <div style="font-family:{SANS};font-size:12px;color:{MUT};margin-top:3px">{data_ro()}</div>
      <div style="font-family:{SERIF};font-size:26px;color:{INK};font-weight:bold;margin-top:14px">{html.escape(eyebrow)}</div>
    </td></tr>
    {inner}
    {cta}
    <tr><td style="padding:18px 28px 26px;border-top:1px solid {LINE}">
      <div style="font-family:{SANS};font-size:11px;color:{MUT};line-height:1.6">
        Primești acest email pentru că ești abonat la Clubul Financiar. Conținut educativ, nu sfat de investiții.<br>
        <a href="{SITE}" style="color:{GOLD};text-decoration:none">clubulfinanciar.ro</a> ·
        <a href="{SITE}/account.html" style="color:{MUT}">Preferințe</a> ·
        <a href="%unsubscribe_url%" style="color:{MUT}">Dezabonare</a>
      </div>
    </td></tr>
  </table>
</td></tr></table></body></html>'''


def h_section(label):
    return f'<tr><td style="padding:22px 28px 4px"><div style="font-family:{SERIF};font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:{GOLD};font-weight:bold">{html.escape(label)}</div></td></tr>'


# ---------- FREE: Dimineața pe scurt (determinist) ----------
def build_free():
    fx = load("fx.json"); news = load("news.json"); div = load("dividends.json"); macro = load("macro.json")
    byc = {r["cur"]: r for r in fx.get("rates", [])}
    items = (news.get("items") or [])[:5]

    # intro
    eur = byc.get("EUR", {})
    eur_chg = eur.get("chg", 0) or 0
    trend = "stabil" if abs(eur_chg) < 0.1 else ("în creștere" if eur_chg > 0 else "în scădere")
    intro = f"Leul e {trend} față de euro azi. Iată ce mișcă banii înainte să-ți începi ziua."

    inner = f'<tr><td style="padding:14px 28px 4px"><div style="font-family:{SANS};font-size:15px;color:{MUT};line-height:1.6">{html.escape(intro)}</div></td></tr>'

    # 5 puncte
    inner += h_section("Cele 5 lucruri de azi")
    rows = ""
    for i, it in enumerate(items, 1):
        t = html.escape((it.get("titlu") or "")[:140])
        fapt = html.escape((it.get("fapt") or "")[:200])
        src = html.escape(it.get("src") or "")
        link = html.escape(it.get("link") or SITE)
        rows += f'''<tr><td style="padding:11px 0;border-bottom:1px solid {LINE}" valign="top">
          <table role="presentation" cellpadding="0" cellspacing="0"><tr>
            <td valign="top" style="font-family:{SERIF};font-size:18px;color:{GOLD};font-weight:bold;padding-right:12px;width:24px">{i}</td>
            <td><div style="font-family:{SANS};font-size:14px;color:{INK};font-weight:700;line-height:1.4">{t}</div>
            <div style="font-family:{SANS};font-size:13px;color:{MUT};line-height:1.55;margin-top:3px">{fapt} <a href="{link}" style="color:{GOLD};text-decoration:none">{src} →</a></div></td>
          </tr></table></td></tr>'''
    inner += f'<tr><td style="padding:2px 28px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">{rows}</table></td></tr>'

    # snapshot
    def macro_val(label):
        for g in macro.get("groups", []):
            for it in g.get("items", []):
                if label.lower() in it.get("label", "").lower() and it.get("value") is not None:
                    return it
        return None
    ecb = macro_val("ECB")
    usd = byc.get("USD", {}); xau = byc.get("XAU", {})
    # dividend lider (randament maxim cu sens, din top companii cunoscute)
    big = ["H2O", "SNN", "SNP", "TGN", "TLV", "SNG", "BRD"]
    ditems = (div.get("items") or {})
    divlead = None
    for s in big:
        if s in ditems and ditems[s].get("y"):
            divlead = (ditems[s].get("n"), ditems[s]["y"]); break

    def snap_row(k, v):
        return f'<tr><td style="font-family:{SANS};font-size:13px;color:{MUT};padding:7px 0;border-bottom:1px solid {LINE}">{k}</td><td align="right" style="font-family:{SANS};font-size:14px;color:{INK};font-weight:700;padding:7px 0;border-bottom:1px solid {LINE}">{v}</td></tr>'
    snap = ""
    if eur: snap += snap_row("EUR / RON", lei(eur.get("rate"), 4) + " lei")
    if usd: snap += snap_row("USD / RON", lei(usd.get("rate"), 4) + " lei")
    if ecb: snap += snap_row("Dobânda ECB", lei(ecb.get("value"), 2) + "%")
    if xau: snap += snap_row("Aur (1 g)", lei(xau.get("rate"), 2) + " lei")
    if divlead: snap += snap_row(f"Top dividend · {html.escape(divlead[0])}", lei(divlead[1], 2) + "% randament")
    inner += h_section("Snapshot piață")
    inner += f'<tr><td style="padding:2px 28px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">{snap}</table></td></tr>'

    # conceptul zilei (din glosar, rotație pe zi)
    gl = glosar()
    if gl:
        idx = datetime.date.today().toordinal() % len(gl)
        term = gl[idx]
        inner += h_section("Conceptul zilei")
        inner += f'''<tr><td style="padding:2px 28px 4px">
          <div style="background:{PANEL};border:1px solid {LINE};border-left:3px solid {GOLD};border-radius:12px;padding:14px 16px">
            <div style="font-family:{SERIF};font-size:16px;color:{GOLD};font-weight:bold">{html.escape(term["term"])}</div>
            <div style="font-family:{SANS};font-size:13px;color:{INK};line-height:1.6;margin-top:5px">{html.escape(term["definition"])}</div>
            <a href="{SITE}/glosar.html" style="font-family:{SANS};font-size:12px;color:{GOLD};text-decoration:none;display:inline-block;margin-top:8px">Vezi tot glosarul (807 termeni) →</a>
          </div></td></tr>'''

    # CTA soft text
    inner += f'<tr><td style="padding:18px 28px 2px"><div style="font-family:{SANS};font-size:14px;color:{MUT};line-height:1.6">Vrei și <i>cum</i> să gândești despre asta, nu doar <i>ce</i> s-a întâmplat? Newsletterul Premium îți dă analiza, nu doar faptele.</div></td></tr>'

    return shell("Dimineața pe scurt — Clubul Financiar", "Dimineața pe scurt", inner)


# ---------- PREMIUM / PRO (autor, LLM cu fallback) ----------
def build_premium():
    news = load("news.json"); items = (news.get("items") or [])[:6]
    headlines = "\n".join(f"- {it.get('titlu','')}: {it.get('fapt','')[:160]} (sursă: {it.get('src','')})" for it in items)
    body = llm([
        {"role": "system", "content": "Ești autorul unui newsletter financiar românesc premium, cu voce personală, spirituală și ușor sceptică față de narațiunea oficială — un «Matt Levine românesc». Scrii pentru oameni educați, nu pentru începători. Didactic fără să fie condescendent. Diacritice corecte."},
        {"role": "user", "content": f"Pe baza acestor știri economice ale săptămânii, scrie newsletterul «Ordinea din zgomot» de azi: un hook de 2-3 fraze cu teza zilei, apoi 2-3 secțiuni, fiecare cu un titlu-rubrică jucăuș (NU headline factual) și 150-250 de cuvinte de analiză care reframează — «cum să gândești despre asta». Termină cu un footnote tăios. Format text simplu cu titluri pe linie separată prefixate cu «## ». ȘTIRI:\n{headlines}"}
    ], max_tokens=1400)
    if not body:
        body = "## Ordinea din zgomot\nAstăzi piețele au făcut ce fac de obicei: s-au agitat din motive pe care le vom raționaliza retroactiv. (Conținutul de autor se generează automat la rulare cu chei LLM.)"
    inner = render_author(body)
    return shell("Ordinea din zgomot — Premium", "Ordinea din zgomot", inner)


def build_pro():
    news = load("news.json"); div = load("dividends.json"); fx = load("fx.json")
    items = (news.get("items") or [])[:5]
    headlines = "\n".join(f"- {it.get('titlu','')}: {it.get('fapt','')[:140]}" for it in items)
    body = llm([
        {"role": "system", "content": "Ești analist senior care scrie un newsletter financiar pentru PFA, antreprenori și freelanceri din România. Rigoare + acționabil. Faci «chemări» argumentate cu cifre concrete. Diacritice corecte."},
        {"role": "user", "content": f"Scrie newsletterul «Masa de lucru» de azi: un hook de 1-2 fraze, apoi o «Chemarea zilei» (o decizie concretă argumentată cu matematică simplă, ex. depozit vs titluri de stat), apoi o rubrică «Acționabil PFA/SRL» (termene/praguri fiscale RO). Format text cu titluri pe linie prefixate «## ». ȘTIRI:\n{headlines}"}
    ], max_tokens=1200)
    if not body:
        body = "## Chemarea zilei\nCu dobânzile unde sunt, banii în cont curent pierd teren în fața inflației. (Conținut acționabil generat automat la rulare cu chei LLM.)"
    inner = render_author(body)
    # calendar dividende din date
    ditems = (div.get("items") or {})
    top = sorted([(s, ditems[s]) for s in BIG_TICKERS if s in ditems and ditems[s].get("y") and ditems[s].get("d")],
                 key=lambda x: -x[1]["y"])[:6]
    if top:
        rows = ""
        for s, v in top:
            rows += f'<tr><td style="font-family:{SANS};font-size:13px;color:{INK};padding:6px 0;border-bottom:1px solid {LINE}">{html.escape(v.get("n",s))}</td><td align="right" style="font-family:{SANS};font-size:13px;color:{GOLD};font-weight:700;padding:6px 0;border-bottom:1px solid {LINE}">{lei(v["y"],2)}% · {lei(v["d"], 2 if v["d"]>=1 else 4)} lei/acț.</td></tr>'
        inner += h_section("Radar dividende BVB")
        inner += f'<tr><td style="padding:2px 28px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">{rows}</table></td></tr>'
    return shell("Masa de lucru — Pro", "Masa de lucru", inner)


def build_ultra():
    # DEMO — live = per-user din ultra_profile (CF.U). Aici un exemplu de structură.
    inner = f'''<tr><td style="padding:14px 28px 4px"><div style="font-family:{SANS};font-size:15px;color:{MUT};line-height:1.6">
      <i>Exemplu de structură. La trimiterea reală, fiecare abonat Ultra primește acest raport calculat din profilul lui (cockpit, simulator, alocare).</i></div></td></tr>'''
    inner += h_section("Poziția ta săptămâna asta")
    inner += f'''<tr><td style="padding:2px 28px"><div style="background:{PANEL};border:1px solid {LINE};border-radius:12px;padding:16px">
      <div style="font-family:{SERIF};font-size:24px;color:{INK};font-weight:bold">142.300 lei <span style="color:{POS};font-size:14px">+0,8%</span></div>
      <div style="font-family:{SANS};font-size:13px;color:{MUT};margin-top:4px">34% din ținta FIRE · alocare 40% titluri / 35% acțiuni / 25% cash</div>
    </div></td></tr>'''
    inner += h_section("Ce te-a mișcat pe tine")
    inner += f'<tr><td style="padding:2px 28px"><div style="font-family:{SANS};font-size:13px;color:{INK};line-height:1.6">Decizia BNR îți păstrează randamentul pe cei 60.000 lei în Fidelis, dar cash-ul tău (35.500 lei) pierde ~1,4% real/an — ~500 lei erodare. Hidroelectrica (120 acțiuni) plătește dividend: +840 lei brut.</div></td></tr>'
    inner += h_section("Recomandarea ta")
    inner += f'<tr><td style="padding:2px 28px"><div style="background:{PANEL};border:1px solid {LINE};border-left:3px solid {GOLD};border-radius:12px;padding:14px 16px;font-family:{SANS};font-size:13px;color:{INK};line-height:1.6">Ai 25% cash, peste banda ta țintă de 15%. Mutarea a 14.000 lei în Fidelis = +85 lei/an real, lichiditate păstrată.</div></td></tr>'
    return shell("Raportul tău — Ultra", "Raportul tău", inner, accent_cta=False)


def render_author(text):
    out = ""
    for block in text.split("\n"):
        b = block.strip()
        if not b:
            continue
        if b.startswith("##"):
            t = b.lstrip("#").strip()
            out += f'<tr><td style="padding:18px 28px 2px"><div style="font-family:{SERIF};font-size:18px;color:{GOLD};font-weight:bold;font-style:italic">{html.escape(t)}</div></td></tr>'
        else:
            style = f"font-size:12px;color:{MUT};font-style:italic" if b.startswith(("¹", "*", "—", "Nota")) else f"font-size:14px;color:{INK}"
            out += f'<tr><td style="padding:4px 28px"><div style="font-family:{SANS};{style};line-height:1.65">{html.escape(b)}</div></td></tr>'
    return out


# ---------- trimitere (GATED) ----------
def send_email(to, subject, html_body):
    if not RESEND:
        print("  RESEND_API_KEY lipsește — nu trimit."); return False
    body = json.dumps({"from": FROM, "to": [to], "subject": subject, "html": html_body}).encode()
    req = urllib.request.Request("https://api.resend.com/emails", data=body,
        headers={"Authorization": "Bearer " + RESEND, "Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=30); return True
    except Exception as e:
        print("  send FAIL", str(e)[:80]); return False


def fetch_recipients(tier):
    """Cheamă RPC-ul newsletter_recipients(tier) din Supabase (service key)."""
    if not SB_KEY:
        print("  SUPABASE_SERVICE_KEY lipsește — nu pot lua abonații."); return []
    body = json.dumps({"want_tier": tier}).encode()
    req = urllib.request.Request(SB_URL.rstrip("/") + "/rest/v1/rpc/newsletter_recipients", data=body,
        headers={"apikey": SB_KEY, "Authorization": "Bearer " + SB_KEY, "Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=30).read())
    except Exception as e:
        print("  fetch abonați FAIL", str(e)[:100]); return []


def send_tier(tier, limit=None):
    """Trimite newsletterul unui tier tuturor abonaților lui, cu link de dezabonare real."""
    subj, fn = TIERS[tier]
    recips = fetch_recipients(tier)
    if limit:
        recips = recips[:int(limit)]
    print(f"[--send {tier}] {len(recips)} abonați")
    html_body = fn()
    sent = 0
    for r in recips:
        em = r.get("email"); tok = r.get("unsub_token", "")
        if not em:
            continue
        unsub = f"{SITE}/dezabonare.html?t={tok}"
        personal = html_body.replace("%unsubscribe_url%", unsub)
        if send_email(em, subj + " — Clubul Financiar", personal):
            sent += 1
        import time as _t; _t.sleep(0.25)   # politicos cu Resend
    print(f"  trimise: {sent}/{len(recips)}")


TIERS = {
    "free": ("Dimineața pe scurt", build_free),
    "premium": ("Ordinea din zgomot", build_premium),
    "pro": ("Masa de lucru", build_pro),
    "ultra": ("Raportul tău", build_ultra),
}


def main():
    args = sys.argv[1:]
    os.makedirs(PREVIEW, exist_ok=True)
    # 1) PREVIEW (mereu) — scrie HTML pentru fiecare tier
    built = {}
    for key, (subj, fn) in TIERS.items():
        try:
            html_body = fn()
            built[key] = (subj, html_body)
            open(os.path.join(PREVIEW, key + ".html"), "w", encoding="utf-8").write(html_body)
            print(f"✅ preview {key}: docs/newsletter/preview/{key}.html")
        except Exception as e:
            print(f"❌ {key}: {e}")

    # 2) --test EMAIL  → trimite Free la o adresă
    if "--test" in args:
        to = args[args.index("--test") + 1]
        subj, body = built.get("free", ("", ""))
        print(f"trimit test «{subj}» → {to}:", "OK" if send_email(to, subj + " — Clubul Financiar", body) else "EȘUAT")

    # 3) --send TIER  → LIVE abonaților (necesită Supabase + Resend verificat).
    #    Cere și --confirm ca să nu trimită din greșeală. Opțional --limit N.
    if "--send" in args:
        tier = args[args.index("--send") + 1]
        if tier not in TIERS:
            print(f"tier necunoscut: {tier} (alege: {', '.join(TIERS)})"); return
        if "--confirm" not in args:
            recips = fetch_recipients(tier)
            print(f"[DRY-RUN] aș trimite «{TIERS[tier][0]}» către {len(recips)} abonați '{tier}'.")
            print("Adaugă --confirm ca să trimit pe bune. Opțional --limit N pentru un test parțial.")
            return
        limit = args[args.index("--limit") + 1] if "--limit" in args else None
        send_tier(tier, limit=limit)


if __name__ == "__main__":
    main()
