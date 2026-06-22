#!/usr/bin/env python3
"""Construiește docs/assets/ai-knowledge.json = bază de cunoștințe verificată
pentru RAG-ul asistentului AI ANAF. Surse (toate deja fact-checkate, fără LLM):
glosar + explicațiile testelor (5000) grupate pe lecție + constante 2026."""
import json, glob, re, html, os

def kw(text):
    text=re.sub(r'<[^>]+>','',text or '').lower()
    words=re.findall(r'[a-zăâîșț0-9]{4,}', text)
    stop=set("este care cum sunt pentru dintr daca trebuie acest aceasta avea face poate fiecare conform articol lectie cele unei unui mai pe la in si cu de din ce".split())
    return list(dict.fromkeys(w for w in words if w not in stop))[:18]

entries=[]

# 1) GLOSAR (din glosar.html: <dt>/<dd> sau structura proprie)
g=open("docs/glosar.html",encoding="utf-8").read()
pairs=re.findall(r'<(?:h3|dt|strong)[^>]*>([^<]{2,60})</(?:h3|dt|strong)>\s*<(?:p|dd|div)[^>]*>(.*?)</(?:p|dd|div)>', g, re.S)
for term,defin in pairs:
    term=html.unescape(term.strip()); defin=html.unescape(re.sub(r'<[^>]+>','',defin)).strip()
    if len(defin)>20:
        entries.append({"t":term,"x":f"{term}: {defin}","k":kw(term+" "+defin),"src":"glosar"})

# 2) LECȚII: explicațiile testelor grupate pe lecție + titlu din search-index
si={e["s"]:e for e in json.load(open("docs/search-index.json")) if e.get("s")}
for f in glob.glob("docs/assets/quiz/d/*.json"):
    d=json.load(open(f,encoding="utf-8"))
    for slug,o in d.items():
        exps=[q.get("explain","").strip() for q in o.get("q",[]) if q.get("explain")]
        if not exps: continue
        title=si.get(slug,{}).get("t",slug.replace("-"," "))
        text=title+". "+" ".join(dict.fromkeys(exps))  # dedup
        text=text[:1400]
        entries.append({"t":title,"x":text,"k":kw(title+" "+" ".join(exps[:4])),"src":slug})

# 3) CONSTANTE 2026 (fapte cheie hard-coded, verificate)
consts=[
 "Salariul minim brut 2026 = 4.050 lei. Praguri salarii minime: 6 SM=24.300, 12 SM=48.600, 24 SM=97.200, 72 SM=291.600 lei.",
 "Salariat: CAS 25% + CASS 10% pe tot brutul (fără plafon) + impozit 10% pe (brut-CAS-CASS-deducere personală). Angajatorul plătește doar CAM 2,25%.",
 "Impozit pe dividende 2026 = 16%. Microîntreprindere: 1% pe venituri, plafon 100.000 €, minim 1 salariat. SRL profit: 16%.",
 "TVA 2026: cotă standard 21%, redusă 11%, plafon înregistrare 395.000 lei cifră de afaceri.",
 "Câștig din investiții 2026: broker REZIDENT (român) 3% (deținere >1 an) / 6% (<1 an), reținut la sursă; broker STRĂIN 16% prin Declarația Unică. Dividende 16%.",
 "PFA sistem real: CAS 25% datorat doar dacă venit net ≥12 SM (bază 12 SM între 12-24 SM, 24 SM peste); CASS 10% pe venit net, bază min 6 SM max 72 SM. Impozit 10% pe (venit net-CAS-CASS).",
 "Chirii: impozit 10% pe venit net (după deducere forfetară 20%). CASS pe trepte (6/12/24 SM) pe total venituri pasive.",
 "Declarația Unică (D212): termen 25 mai; bonificație 3% la plata integrală până 15 aprilie.",
 "Penalități ANAF: dobândă 0,02%/zi + penalitate de întârziere 0,01%/zi + penalitate de nedeclarare 0,08%/zi. Contestație decizie de impunere: 45 zile.",
 "Plan de conturi (OMFP 1802/2014): Mărfuri=371, Materii prime=301, Clienți=411, Furnizori=401, Casa=5311, Bancă lei=5121, Capital=101, Profit curent=121, Profit reportat=117, TVA plată=4423/deductibilă=4426/colectată=4427, energie/apă=605, rezervă legală=1061, dividende de plată=457.",
]
for c in consts:
    entries.append({"t":"Constante fiscale 2026","x":c,"k":kw(c),"src":"constante"})

# 4) Articole avansate (din search-index) neacoperite de teste — acoperire pe toate articolele
have=set(e["src"] for e in entries)
for e in si.values():
    s=e.get("s")
    if not s or s in have: continue
    t=e.get("t",""); d=e.get("d","")
    if not t or len(d)<30: continue
    entries.append({"t":t,"x":(t+". "+d)[:900],"k":kw(t+" "+d),"src":s}); have.add(s)

json.dump(entries,open("docs/assets/ai-knowledge.json","w"),ensure_ascii=False)
sz=os.path.getsize("docs/assets/ai-knowledge.json")
print(f"ai-knowledge.json: {len(entries)} intrări, {sz//1024} KB (glosar:{sum(1 for e in entries if e['src']=='glosar')}, lecții:{sum(1 for e in entries if e['src'] not in ('glosar','constante'))}, constante:{len(consts)})")
