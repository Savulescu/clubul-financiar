#!/usr/bin/env python3
# =============================================================================
# bvb_div_build.py — construiește docs/data/dividends.json din datele publice BVB.
# Sursă: bvb.ro (lista de acțiuni + pagina de detaliu a fiecărui instrument).
#   - Lista: /FinancialInstruments/Markets/Shares  (toate companiile + nume + preț)
#   - Detaliu: /FinancialInstruments/Details/FinancialInstrumentsDetails.aspx?s=SIMBOL
#     conține: „Dividend (AAAA)" = dividend/acțiune, „DIVY" = randament %, EPS, preț.
# Date publice, informativ. Rulat zilnic prin GitHub Actions. Fără dependențe externe.
# =============================================================================
import json, os, re, ssl, time, urllib.request, urllib.error
from datetime import datetime, timezone

BASE = "https://www.bvb.ro"
LIST_URL = BASE + "/FinancialInstruments/Markets/Shares"
DET_URL = BASE + "/FinancialInstruments/Details/FinancialInstrumentsDetails.aspx?s={}"
OUT = os.path.join(os.path.dirname(__file__), "docs", "data", "dividends.json")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

# Nume „de prietenie" + sector pentru companiile mari (UX mai bun decât denumirea legală).
FRIENDLY = {
    "TLV": ("Banca Transilvania", "Bănci"), "H2O": ("Hidroelectrica", "Energie"),
    "SNP": ("OMV Petrom", "Petrol & gaze"), "SNG": ("Romgaz", "Gaze naturale"),
    "SNN": ("Nuclearelectrica", "Energie nucleară"), "BRD": ("BRD - SocGen", "Bănci"),
    "DIGI": ("Digi Communications", "Telecom"), "EL": ("Electrica", "Distribuție energie"),
    "FP": ("Fondul Proprietatea", "Fond de investiții"), "TGN": ("Transgaz", "Transport gaze"),
    "M": ("MedLife", "Sănătate privată"), "TRP": ("TeraPlast", "Materiale construcții"),
    "AQ": ("Aquila", "Distribuție & logistică"), "WINE": ("Purcari", "Vinuri"),
    "SFG": ("Sphera Franchise", "Restaurante"), "TTS": ("TTS (Transport Trade)", "Transport fluvial"),
    "ATB": ("Antibiotice Iași", "Farma"), "COTE": ("Conpet", "Transport țiței"),
    "BVB": ("Bursa de Valori București", "Piață de capital"), "ONE": ("One United Properties", "Imobiliare"),
    "TEL": ("Transelectrica", "Transport energie"), "ALR": ("Alro Slatina", "Aluminiu"),
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.read().decode("utf-8", "ignore")
    except urllib.error.URLError as e:
        # fallback local: CA store lipsă (homebrew). În CI verificarea reușește normal.
        if "CERTIFICATE_VERIFY_FAILED" not in str(e):
            raise
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            return r.read().decode("utf-8", "ignore")


def ro_num(s):
    """'80.514.659.493,00' -> 80514659493.0 ; '9,571562' -> 9.571562 ; '5,35' -> 5.35"""
    if s is None:
        return None
    s = s.strip()
    if not s or s in ("-", "N/A"):
        return None
    try:
        return float(s.replace(".", "").replace(",", "."))
    except ValueError:
        return None


def parse_list(html):
    """Întoarce listă de (simbol, denumire legală) pentru toate acțiunile."""
    out = []
    # ...?s=SIMBOL"><b>SIMBOL</b></a>[<p>ISIN</p>] </td><td>DENUMIRE</td>
    pat = re.compile(
        r'\?s=([A-Z0-9]{1,6})"><b>[A-Z0-9]{1,6}</b></a>'
        r'(?:\s*<p[^>]*>[^<]*</p>)?\s*</td>\s*<td[^>]*>\s*([^<]{2,90}?)\s*</td>',
        re.I)
    seen = set()
    for sym, name in pat.findall(html):
        sym = sym.upper()
        if sym not in seen:
            seen.add(sym)
            out.append((sym, re.sub(r"\s+", " ", name).strip()))
    return out


def cell(html, label):
    """Valoarea numerică din rândul <td>LABEL...</td><td ...>VALOARE</td>."""
    m = re.search(re.escape(label) + r"[^<]*</td>\s*<td[^>]*>\s*([\d.,]+)\s*</td>", html)
    return ro_num(m.group(1)) if m else None


def parse_detail(html):
    out = {}
    md = re.search(r"Dividend\s*\((\d{4})\)</td>\s*<td[^>]*>\s*([\d.,]+)\s*</td>", html)
    if md:
        out["d"] = ro_num(md.group(2))   # dividend / acțiune
        out["dy"] = int(md.group(1))     # anul dividendului
    out["y"] = cell(html, "DIVY")        # randament %
    out["e"] = cell(html, "EPS")         # profit / acțiune
    p = cell(html, "Pret referinta") or cell(html, "Pret")
    if p:
        out["p"] = p
    return out


def main():
    html = fetch(LIST_URL)
    companies = parse_list(html)
    if not companies:
        raise SystemExit("BVB: lista de acțiuni goală — structură schimbată?")
    print(f"BVB: {len(companies)} companii listate")

    items, ok, withdiv = {}, 0, 0
    for sym, legal in companies:
        try:
            d = parse_detail(fetch(DET_URL.format(sym)))
        except Exception as e:
            print(f"  ! {sym}: {type(e).__name__} {str(e)[:60]}")
            time.sleep(0.4)
            continue
        fn = FRIENDLY.get(sym)
        rec = {"n": fn[0] if fn else legal.title(), "full": legal}
        if fn:
            rec["s"] = fn[1]
        rec.update({k: v for k, v in d.items() if v is not None})
        items[sym] = rec
        ok += 1
        if rec.get("d"):
            withdiv += 1
        time.sleep(0.3)   # politicos cu serverul BVB

    if ok < 20:
        raise SystemExit(f"BVB: doar {ok} companii citite — abandonez (nu suprascriu cu date parțiale).")

    payload = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "source": "bvb.ro (date publice, informativ)",
        "count": ok,
        "withDividend": withdiv,
        "items": items,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, OUT)
    print(f"BVB: scris {OUT} — {ok} companii, {withdiv} cu dividend")


if __name__ == "__main__":
    main()
