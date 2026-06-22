#!/usr/bin/env python3
"""Construiește docs/assets/ai-knowledge.json = bază de cunoștințe verificată
pentru RAG-ul asistentului AI ANAF. Surse (toate deja fact-checkate, fără LLM):
glosar + explicațiile testelor (5000) grupate pe lecție + constante 2026."""
import json, glob, re, html, os

def _norm(s):
    s=(s or "").lower()
    for a,b in [("ă","a"),("â","a"),("î","i"),("ș","s"),("ț","t"),("ş","s"),("ţ","t")]: s=s.replace(a,b)
    return s
def kw(text):
    text=_norm(re.sub(r'<[^>]+>','',text or ''))
    words=re.findall(r'[a-z0-9]{4,}', text)
    stop=set("este care cum sunt pentru dintr daca trebuie acest aceasta avea face poate fiecare conform articol lectie cele unei unui mai pe la in si cu de din ce".split())
    # radacini de 6 caractere (potrivire diacritic-insensitiv + forme de cuvant: taxare/taxarea -> taxare)
    return list(dict.fromkeys(w[:6] for w in words if w not in stop))[:22]

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
 "Titluri de stat (Fidelis, Tezaur): dobânda/cupoanele sunt SCUTITE de impozit pe venit pentru persoane fizice. Dobânda la depozite bancare = 10% reținut la sursă. Câștigul din vânzarea titlurilor înainte de scadență = impozabil ca venit din investiții.",
 "Nerezidenți: dividende/dobânzi/redevențe/comisioane plătite de o firmă din RO unui nerezident = 16% reținut la sursă, redus prin convenția de dublă impunere (cu certificat de rezidență fiscală).",
 "Impozitul pe construcții speciale este ABROGAT. OSS: servicii digitale B2C în UE peste 10.000 €/an se taxează la cota statului clientului, declarat prin decont OSS unic.",
]
for c in consts:
    entries.append({"t":"Constante fiscale 2026","x":c,"k":kw(c),"src":"constante"})

# 3b) FAPTE AVANSATE VERIFICATE (proceduri/contabilitate frecvente unde modelul ezita)
facts=[
 "Taxare inversă TVA: la operațiuni precum deșeuri/fier vechi, anumite construcții, cereale, lemn, beneficiarul datorează ȘI deduce simultan TVA (4426=4427), fără plată efectivă de TVA. Se aplică între plătitori de TVA din România.",
 "TVA la încasare: regim OPȚIONAL pentru firme cu cifra de afaceri sub ~4,5 milioane lei; exigibilitatea TVA apare la momentul încasării facturii, nu la emitere.",
 "Rambursare TVA: când TVA deductibilă > TVA colectată, ai TVA de recuperat; ceri rambursarea bifând opțiunea în decontul D300; ANAF poate aproba cu sau fără inspecție fiscală.",
 "Declarații TVA: D300 = decont de TVA (lunar sau trimestrial, după cifra de afaceri); D390 = declarație recapitulativă pentru operațiuni intracomunitare (VIES); D394 = declarație informativă privind livrările/achizițiile pe teritoriul național între plătitori RO.",
 "Eșalonare datorii ANAF: forma SIMPLIFICATĂ = maxim 12 luni, fără garanții; forma CLASICĂ = maxim 60 de luni (5 ani), cu garanții. Se cere prin cerere la ANAF, nu prin D100.",
 "Inspecția fiscală: ANAF verifică obligațiile pe perioada de prescripție (5 ani); primești un aviz de inspecție; la final, raport de inspecție + eventual decizie de impunere (pe care o poți contesta în 45 de zile).",
 "Concediu medical (boală obișnuită): primele 5 zile suportate de angajator, restul din FNUASS; indemnizația = 75% din baza de calcul; indemnizațiile de concediu medical sunt SCUTITE de CAS și CASS, se reține DOAR impozit 10%.",
 "PFA la normă de venit: ANAF stabilește un venit anual fix (norma) pe tipul de activitate; NU deduci cheltuieli reale; CAS/CASS și impozitul 10% se raportează la normă (cu pragurile 6/12/24 salarii minime).",
 "Avans de la client: se înregistrează 5121=419 (clienți-creditori) la încasare, cu TVA colectată la avans (411=4427 sau prin 419); la livrare se regularizează cu factura finală.",
 "Stornarea unei facturi greșite: se emite o factură de storno (sumă în roșu/negativă) sau o factură de corecție; în contabilitate se înregistrează în roșu aceleași conturi ca factura inițială.",
 "Notă de recepție (NIR): document care atestă primirea mărfii/materialelor în gestiune; stă la baza înregistrării 371/301 = 401.",
 "Vânzare marfă cu adaos: 411 = 707 (venit) + 4427 (TVA colectată); scoaterea din gestiune 607 = 371 (la cost).",
 "Salariu (înregistrări): 641 = 421 (brut datorat); reținerile angajatului 421 = 4315 (CAS 25%) + 4316 (CASS 10%) + 444 (impozit 10%); CAM angajator 646 = 436 (2,25%); plata netă 421 = 5121.",
 "Inspecția/poprirea: poprirea = ANAF blochează sumele din conturi pentru recuperarea datoriilor; se ridică după plata/eșalonarea datoriei.",
 "Amenzile/penalitățile către stat = cont 6581 (NEdeductibile fiscal), NU 635. Reducere comercială primită de la furnizor = 609; acordată clienților = 709. Sconturi: primite 767, acordate 667.",
 "Cote TVA 2026: standard 21%; redusă 11% pentru alimente, medicamente, cărți/ziare, cazare, restaurant/catering, apă, lemne de foc.",
 "Neplătitor de TVA: NU colectezi TVA pe facturi, dar NICI nu deduci TVA-ul de la achiziții (îl treci pe cheltuială/cost). Devii plătitor obligatoriu la depășirea plafonului de 395.000 lei.",
]
for fct in facts:
    entries.append({"t":"Fapt fiscal verificat","x":fct,"k":kw(fct),"src":"fapt"})

# 4) Articole avansate (din search-index) neacoperite de teste — acoperire pe toate articolele
have=set(e["src"] for e in entries)
for e in si.values():
    s=e.get("s")
    if not s or s in have: continue
    t=e.get("t",""); d=e.get("d","")
    if not t or len(d)<30: continue
    entries.append({"t":t,"x":(t+". "+d)[:900],"k":kw(t+" "+d),"src":s}); have.add(s)

# corecție: „broker străin 10%" e cota VECHE → 16% din 2026 (Legea 239/2025); aliniez sursele RAG
for e in entries:
    x=e["x"]
    x=re.sub(r'(broker\w*\s+str[ăa]in\w*[^.]{0,70}?)10(\s?%)', r'\g<1>16\g<2>', x, flags=re.I)
    x=re.sub(r'(str[ăa]in\w*,?\s+impozitul\s+(?:este\s+)?de\s+)10(\s?%)', r'\g<1>16\g<2>', x, flags=re.I)
    x=re.sub(r'10(\s?%[^.]{0,50}?broker\w*\s+str[ăa]in)', r'16\g<1>', x, flags=re.I)
    e["x"]=x

json.dump(entries,open("docs/assets/ai-knowledge.json","w"),ensure_ascii=False)
sz=os.path.getsize("docs/assets/ai-knowledge.json")
print(f"ai-knowledge.json: {len(entries)} intrări, {sz//1024} KB (glosar:{sum(1 for e in entries if e['src']=='glosar')}, lecții:{sum(1 for e in entries if e['src'] not in ('glosar','constante'))}, constante:{len(consts)})")
