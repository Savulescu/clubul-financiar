#!/usr/bin/env python3
# =============================================================================
# fx_build.py — construiește docs/data/fx.json din cursul oficial BNR.
# Sursă: bnr.ro/nbrfxrates.xml (azi) + files/xml/years/nbrfxratesYYYY.xml (istoric).
# Licență: date publice BNR, utilizabile comercial. Rulat zilnic prin GitHub Actions.
# Fără dependențe externe (urllib + ElementTree).
# =============================================================================
import json, os, ssl, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone

NS = "{http://www.bnr.ro/xsd}"
TODAY_URL = "https://www.bnr.ro/nbrfxrates.xml"
YEAR_URL = "https://www.bnr.ro/files/xml/years/nbrfxrates{}.xml"
OUT = os.path.join(os.path.dirname(__file__), "docs", "data", "fx.json")
SPARK_DAYS = 30

# Nume RO pentru valutele uzuale (restul -> codul).
NAMES = {
    "EUR": "Euro", "USD": "Dolar american", "GBP": "Liră sterlină", "CHF": "Franc elvețian",
    "AUD": "Dolar australian", "CAD": "Dolar canadian", "JPY": "Yen japonez", "CNY": "Yuan chinezesc",
    "HUF": "Forint maghiar", "PLN": "Zlot polonez", "BGN": "Leva bulgărească", "CZK": "Coroană cehă",
    "DKK": "Coroană daneză", "SEK": "Coroană suedeză", "NOK": "Coroană norvegiană", "TRY": "Liră turcească",
    "MDL": "Leu moldovenesc", "UAH": "Hryvna ucraineană", "RSD": "Dinar sârbesc", "AED": "Dirham UAE",
    "BRL": "Real brazilian", "INR": "Rupie indiană", "KRW": "Won sud-coreean", "MXN": "Peso mexican",
    "NZD": "Dolar neozeelandez", "RUB": "Rublă rusească", "ZAR": "Rand sud-african", "HKD": "Dolar Hong Kong",
    "SGD": "Dolar singaporez", "THB": "Baht thailandez", "EGP": "Liră egipteană", "XAU": "Aur (1 gram)",
    "XDR": "DST (FMI)",
}
# Ordinea preferată sus în board (cele mai urmărite de români).
TOP = ["EUR", "USD", "GBP", "CHF", "HUF", "XAU"]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ClubulFinanciar/1.0 (+clubulfinanciar.ro)"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.read()
    except urllib.error.URLError as e:
        # fallback local: CA store lipsă (homebrew). În CI verificarea reușește normal.
        if "CERTIFICATE_VERIFY_FAILED" not in str(e):
            raise
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            return r.read()


def parse_cubes(xml_bytes):
    """Întoarce listă de (date_str, {CUR: per_unit_rate}) sortată crescător după dată."""
    root = ET.fromstring(xml_bytes)
    out = []
    for cube in root.iter(NS + "Cube"):
        d = cube.get("date")
        rates = {}
        for rate in cube.findall(NS + "Rate"):
            cur = rate.get("currency")
            mult = float(rate.get("multiplier") or 1)
            try:
                val = float(rate.text)
            except (TypeError, ValueError):
                continue
            rates[cur] = val / mult  # normalizat la 1 unitate
        out.append((d, rates))
    out.sort(key=lambda x: x[0])
    return out


def main():
    today_cubes = parse_cubes(fetch(TODAY_URL))
    if not today_cubes:
        raise SystemExit("BNR today feed empty")
    cur_date, cur_rates = today_cubes[-1]
    year = cur_date[:4]

    # istoric pe an pentru trend + variația zilnică
    try:
        hist = parse_cubes(fetch(YEAR_URL.format(year)))
    except Exception:
        hist = today_cubes
    # asigură că ziua curentă e inclusă
    if not hist or hist[-1][0] != cur_date:
        hist = hist + [(cur_date, cur_rates)]

    # serie per valută
    series = {}
    for d, rates in hist:
        for cur, val in rates.items():
            series.setdefault(cur, []).append(val)

    all_curs = list(cur_rates.keys())
    ordered = [c for c in TOP if c in all_curs] + sorted(c for c in all_curs if c not in TOP)

    rows = []
    for cur in ordered:
        s = series.get(cur, [cur_rates[cur]])
        rate = cur_rates[cur]
        prev = s[-2] if len(s) >= 2 else rate
        chg = (rate - prev) / prev * 100 if prev else 0.0
        spark = [round(v, 4) for v in s[-SPARK_DAYS:]]
        rows.append({
            "cur": cur, "name": NAMES.get(cur, cur),
            "rate": round(rate, 4), "prev": round(prev, 4),
            "chg": round(chg, 3), "spark": spark, "top": cur in TOP,
        })

    data = {
        "source": "Banca Națională a României (curs oficial)",
        "date": cur_date,
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "base": "RON",
        "count": len(rows),
        "rates": rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print("wrote", OUT, "·", len(rows), "valute ·", cur_date)


if __name__ == "__main__":
    main()
