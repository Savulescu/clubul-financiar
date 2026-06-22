#!/usr/bin/env python3
# =============================================================================
# macro_build.py — construiește docs/data/macro.json din surse publice keyless.
# Surse legal-comercial cu atribuire: FRED (fredgraph.csv, fără cheie; date SUA
# public domain), Eurostat (CC BY 4.0, fără cheie). Rulat zilnic în GitHub Actions.
# Fără dependențe externe (urllib + json). Fiecare serie e izolată în try/except.
# =============================================================================
import json, os, ssl, subprocess, time, urllib.request
from datetime import datetime, timezone, timedelta

OUT = os.path.join(os.path.dirname(__file__), "docs", "data", "macro.json")
# doar ultimii ~2.2 ani → răspuns mic & rapid (evită timeout pe istoricul complet)
_COSD = (datetime.now(timezone.utc) - timedelta(days=820)).strftime("%Y-%m-%d")
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}&cosd=" + _COSD
EUROSTAT = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
            "prc_hicp_manr?geo={}&coicop=CP00&format=JSON&lastTimePeriod=1")
UA = {"User-Agent": "ClubulFinanciar/1.0 (+clubulfinanciar.ro)"}


def _once(url):
    req = urllib.request.Request(url, headers=UA)
    try:
        return urllib.request.urlopen(req, timeout=8).read()
    except Exception:
        return subprocess.run(
            ["curl", "-fsSL", "--http1.1", "--max-time", "8", "-A", UA["User-Agent"], url],
            capture_output=True, timeout=12, check=True).stdout


def fetch(url):
    last = None
    for i in range(2):  # 1 retry; circuit-breaker-ul oprește restul seriilor FRED
        try:
            return _once(url)
        except Exception as e:
            last = e
            time.sleep(1 + i)
    raise last


_fred_down = [False]  # circuit breaker: dacă FRED e jos (ex. throttle local), nu mai insistăm


def fred_series(sid):
    """Întoarce listă [(date, value)] din fredgraph.csv, ignorând valorile lipsă ('.')."""
    if _fred_down[0]:
        return []
    try:
        rows = fetch(FRED.format(sid)).decode("utf-8").splitlines()
    except Exception:
        _fred_down[0] = True  # prima cădere FRED → sărim restul rapid
        raise
    out = []
    for ln in rows[1:]:
        parts = ln.split(",")
        if len(parts) < 2:
            continue
        d, v = parts[0], parts[-1].strip()
        try:
            out.append((d, float(v)))
        except ValueError:
            continue
    return out


def fred_last(sid):
    s = fred_series(sid)
    return s[-1] if s else (None, None)


def fred_yoy(sid):
    """Variație anuală (%) dintr-un index lunar: ultima vs acum 12 luni."""
    s = fred_series(sid)
    if len(s) < 13:
        return (None, None)
    d, last = s[-1]
    prev = s[-13][1]
    return (d, round((last / prev - 1) * 100, 1)) if prev else (None, None)


def ecb_obs(key):
    """Ultima observație dintr-o serie ECB SDW (csvdata): (TIME_PERIOD, OBS_VALUE)."""
    url = ("https://data-api.ecb.europa.eu/service/data/" + key +
           "?lastNObservations=1&format=csvdata")
    rows = fetch(url).decode("utf-8").splitlines()
    if len(rows) < 2:
        return (None, None)
    cols = rows[-1].split(",")
    try:
        return (cols[8], round(float(cols[9]), 2))
    except (IndexError, ValueError):
        return (None, None)


EUROSTAT_BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"


def eurostat_last(dataset, query):
    """Ultima valoare DISPONIBILĂ dintr-un dataset Eurostat (lunile recente pot lipsi)."""
    j = json.loads(fetch(EUROSTAT_BASE + dataset + "?format=JSON&lastTimePeriod=4&" + query).decode("utf-8"))
    vals = j.get("value", {})
    if not vals:
        return (None, None)
    times = list(j.get("dimension", {}).get("time", {}).get("category", {}).get("index", {}).keys())
    k = max(vals, key=lambda x: int(x))
    period = times[int(k)] if int(k) < len(times) else None
    return (period, round(float(vals[k]), 1))


def eurostat_infl(geo):
    j = json.loads(fetch(EUROSTAT.format(geo)).decode("utf-8"))
    val = list(j.get("value", {}).values())
    t = j.get("dimension", {}).get("time", {}).get("category", {}).get("index", {})
    period = list(t.keys())[0] if t else None
    return (period, round(float(val[0]), 1)) if val else (None, None)


def item(label, pair, unit="%", src="", note=""):
    d, v = pair if isinstance(pair, tuple) else (None, pair)
    return {"label": label, "value": v, "date": d, "unit": unit, "src": src, "note": note}


def safe(fn, *a):
    try:
        return fn(*a)
    except Exception as e:
        print("  skip:", a, e)
        return (None, None)


def main():
    groups = []

    # ---- Dobânzi de politică monetară ----
    dob = [
        item("Dobânda Fed (SUA)", safe(fred_last, "FEDFUNDS"), src="Rezerva Federală / FRED"),
        item("Dobânda ECB (refinanțare)", safe(ecb_obs, "FM/D.U2.EUR.4F.KR.MRR_FR.LEV"), src="BCE"),
        item("Euribor 3 luni", safe(ecb_obs, "FM/M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA"), src="BCE / EMMI"),
        item("Dobânda-cheie BNR", (None, None), src="BNR",
             note="Vezi valoarea oficială la zi pe bnr.ro"),
    ]
    groups.append({"title": "Dobânzi de politică monetară", "items": dob})

    # ---- Inflație anuală ----
    infl = [
        item("România", safe(eurostat_infl, "RO"), src="Eurostat"),
        item("Zona euro", safe(eurostat_infl, "EA20"), src="Eurostat"),
        item("SUA", safe(fred_yoy, "CPIAUCSL"), src="BLS / FRED"),
    ]
    groups.append({"title": "Inflație (rata anuală)", "items": infl})

    # ---- Piețe & randamente ----
    piete = [
        item("Titluri de stat SUA, 10 ani", safe(fred_last, "DGS10"), src="FRED"),
        item("Petrol Brent", safe(fred_last, "DCOILBRENTEU"), unit=" $/baril", src="FRED"),
    ]
    groups.append({"title": "Piețe & randamente", "items": piete})

    # ---- Economia României ----
    ro = [
        item("Creștere PIB (anual)", safe(eurostat_last, "namq_10_gdp", "geo=RO&na_item=B1GQ&s_adj=SCA&unit=CLV_PCH_SM"), src="Eurostat"),
        item("Șomaj", safe(eurostat_last, "une_rt_m", "geo=RO&age=TOTAL&unit=PC_ACT&s_adj=SA&sex=T"), src="Eurostat"),
    ]
    groups.append({"title": "Economia României", "items": ro})

    data = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "atribuire": "Surse: Rezerva Federală a SUA (FRED), Banca Centrală Europeană, Eurostat. Orientativ.",
        "groups": groups,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    n = sum(1 for g in groups for it in g["items"] if it["value"] is not None)
    print("wrote", OUT, "·", n, "indicatori cu valoare")


if __name__ == "__main__":
    main()
