# ULTRA BUILD BRIEF — „Biroul tău financiar privat"

Construim suita **Ultra** a clubulfinanciar.ro: un birou financiar privat / CFO personal
pentru români (PFA/SRL, familii, investitori). Toate paginile sunt **statice** în `docs/`,
gated pe tier `ultra`, în idiomul existent. Limbă: română, sentence case, ton calm-premium.

Citește acest brief integral. Folosește **EXACT** API-ul, clasele CSS și skeletonul de mai jos.
Nu inventa alte librării. Tot calculul vine din `CF.U` (determinist) — niciodată din text hardcodat.

---

## 0. REGULI DE DESIGN (obligatorii — Ultra = „extras de bancă privată, nu dashboard SaaS")

- Conținutul Ultra trăiește într-un `<main class="u-page">` care aplică paleta aurie pe navy
  nocturn (dark) / hârtie caldă (light). Nu folosi `.card`/`.btn` brand pentru zona Ultra —
  folosește componentele `.u-*` din `cf-ultra.css`.
- **Auriu = accent prețios, subțire.** Un singur accent auriu per panou (hairline sus + eyebrow).
  Restul, tăcut. Fără umbre stridente, fără gradient stridente.
- **Eyebrow & titluri-crest = serif Fraunces** (deja încărcat). Clase: `.u-eyebrow`, `.u-crest`,
  `.u-label`. Restul textului = Plus Jakarta Sans (implicit). Cifrele mari = `.u-kpi` (Sora,
  tabular-nums, aliniate la dreapta ca într-un extras de cont).
- Verde (`.u-pos`) doar pentru pozitiv/creștere, roșu (`.u-neg`) pentru negativ. Auriu (`.u-gold-t`)
  pentru identitate/valori-cheie Ultra.
- Componente-semnătură: **inelul** (FIRE/scor) via `CF.U.ringSVG(...)`, **gauge-linie** `.u-gauge`
  pentru praguri, **timeline** `.u-timeline` pentru calendar. Folosește-le — nu reinventa.
- Spațiu generos. Responsive până la mobil (grid-urile `.u-grid-*` colapsează deja). Focus vizibil
  (input-urile `.u-*` au deja focus auriu). Respectă `prefers-reduced-motion`.
- Fiecare unealtă cu cifre fiscale pune un disclaimer discret: „Estimare educativă pe regulile RO
  2026. Nu e consultanță fiscală." (folosește `.cf-mini` sau `.u-kpi-sub`).

---

## 1. SKELETON DE PAGINĂ (copiază-l; schimbă DOAR title/desc/canonical + conținutul din `<main>`)

```html
<!DOCTYPE html><html lang="ro"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLU} — Clubul Financiar</title>
<meta name="description" content="{DESC}"><meta name="robots" content="noindex,follow">
<meta name="theme-color" content="#0f2540">
<link rel="canonical" href="https://clubulfinanciar.ro/ultra/{SLUG}.html">
<link rel="icon" type="image/png" href="/favicon.png"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<script>(function(){var t=localStorage.getItem("cf-theme");if(t)document.documentElement.setAttribute("data-theme",t);})();</script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400..800&family=Sora:wght@600;700;800&family=Fraunces:opsz,ital,wght@9..144,0,400;9..144,0,600;9..144,1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v=24">
<link rel="stylesheet" href="/assets/upgrade.css?v=23">
<link rel="stylesheet" href="/assets/cf-tool.css?v=1">
<link rel="stylesheet" href="/assets/cf-ultra.css?v=1">
</head><body>
<header class="nav"><div class="container nav-in">
    <a class="brand-logo" href="/index.html"><img class="brand-img" src="/icon-64.png" alt="Clubul Financiar" width="34" height="34"> <span class="brand-txt">Clubul Financiar</span></a>
    <nav class="nav-links" id="navLinks"><a href="/incepe-aici.html">Începe aici</a><a href="/educatie.html">Învață</a><a href="/masterclass.html">Masterclass</a><a href="/calculatoare.html">Calculatoare</a><a href="/instrumente.html">Instrumente</a><a href="/stiri.html">Știri</a><a href="/premium.html">Premium</a><a href="/feedback.html">Feedback</a></nav>
    <div class="nav-right">
      <button class="icon-btn" id="searchBtn" aria-label="Caută">🔍</button>
      <button class="icon-btn" id="themeBtn" aria-label="Temă"><span class="theme-ic">🌙</span></button>
      <span id="acctSlot"><a class="btn btn-primary" href="/login.html" style="padding:9px 18px">Cont</a></span>
      <button class="icon-btn burger" id="burger" aria-label="Meniu" aria-controls="navLinks" aria-expanded="false">☰</button>
    </div>
  </div></header>

<main class="u-page">
  <section class="section"><div class="container">
    <!-- ============ CONȚINUTUL PAGINII AICI ============ -->
    <!-- Pune zona interactivă într-un container cu id pe care îl gated la final. -->
  </div></section>
</main>

<!-- footer-ul e injectat automat de site.js; NU-l scrie manual -->
<script defer src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<script defer src="/assets/tilt.js?v=23"></script>
<script defer src="/assets/site.js?v=23"></script>
<script src="/assets/fiscal-2026.js?v=1"></script>
<script src="/assets/cf-tool.js?v=1"></script>
<script src="/assets/cf-ultra.js?v=1"></script>
<script>
(function(){
  "use strict";
  var U = CF.U, $ = CF.$;
  var p = U.getProfil();
  function render(){ p = U.getProfil(); /* ... desenează din p ... */ }
  render();
  window.addEventListener("cf-profil", render);   // re-randează când profilul se schimbă
  window.addEventListener("cf-auth", function(){ U.syncCloud().then(render); }); // pull cloud la login
  CF.requireTier("uTool","ultra",{msg:"{MESAJ_GATE}"});  // gated zona interactivă (id='uTool')
})();
</script>
</body></html>
```

Note:
- `<main class="u-page">` e OBLIGATORIU — el aplică paleta Ultra.
- Gating: pune interactivitatea într-un element `id="uTool"` și cheamă `CF.requireTier("uTool","ultra",{msg})`.
  Conținutul rămâne în DOM (se revelează instant când userul devine ultra; adminul e ultra automat).
- Dacă userul n-are profil completat (`!U.areDate(p)`), arată un **empty state** elegant cu buton
  „Completează profilul" → `/ultra/profil.html`. Niciun calcul nu trebuie să arate NaN.

---

## 2. API DISPONIBIL

### 2.1 Format & utilitare (din `cf-tool.js`, namespace `CF`)
- `CF.lei(n)` → „1.234.567 lei” · `CF.lei2(n)` (2 zecimale) · `CF.pct(n)` (n e fracție: 0.2→„20%”)
- `CF.dataRO(d)` → „22 iunie 2026” · `CF.zilePana(d)` → nr zile până la dată · `CF.$(id)`
- `CF.requireTier(containerId, "ultra", {msg})` — montează lock Ultra peste container
- `CF.logEntry(tool, period, payload)` / `CF.getLog(tool)` / `CF.syncLog(tool)` / `CF.perioadaCurenta()` (→ "YYYY-MM")
- `CF.icsDownload(titlu, desc, data)` — descarcă .ics · `CF.printResult(titlu, htmlBody)` — print-to-PDF
- `CF.aiChat(messages, {context})` → Promise<{content, provider, sources}> (Edge Function ai-anaf)
- `CF.setReminder(tool, {kind:"monthly"|"deadline", note, date, channel:"telegram"|"email"})`

### 2.2 Profil (din `cf-ultra.js`, namespace `CF.U`)
- `U.gol()` → profil gol cu valori implicite (folosește-l ca să construiești formele)
- `U.getProfil()` → profilul curent (sincron, din localStorage)
- `U.salveaza(p)` → salvează (local + cloud dacă `p.sync`), emite event `cf-profil`, întoarce profil normalizat
- `U.syncCloud()` → Promise<profil> (trage din cloud, cross-device)
- `U.areDate(p)` → bool (are destule date cât să aibă sens uneltele)
- `U.STRUCTURI` → `[{v,t}]` pentru dropdown structură · `U.structuraLabel(s)` → etichetă

**Schema profilului** (câmpurile pe care le poți citi/scrie):
```
{ v, updated, sync(bool), nume, varsta, dependenti, oras, stareCivila("necasatorit"|"casatorit"),
  structura("salariat"|"pfa_real"|"pfa_norma"|"srl_micro"|"srl_real"|"mixt"), tvaPlatitor(bool),
  venituri:{ salariuNet(lună), pfaIncasari(an), pfaCheltuieli(an), srlCifraAfaceri(an),
             srlCheltuieli(an), srlDividendePct(0-100), chiriiLunar, dividendeAnual(an), alteLunar },
  cheltuieli:{ locuinta, mancare, transport, utilitati, rate, abonamente, copii, sanatate, distractie, alte },
  datorii:[ {nume, sold, dobanda(%), rataLunara} ],
  active:{ cash, depozite, investitii, crypto, titluriStat, pensiePilon3,
           imobiliareInvestitii, locuintaProprie, auto, alte },
  obiective:{ fondUrgentaLuni, varstaLibertate, randamentReal(%), custom:[{nume,suma,termen}] },
  toleranteRisc("mica"|"medie"|"mare") }
```

### 2.3 Calcul (toate primesc profilul `p`; dacă-l omiți, ia profilul curent)
- `U.venitNetLunar(p)` → number (venit net lunar, toate sursele, după taxe)
- `U.venitStructuraAnual(p)` → `{tip, netInMana, totalTaxe, baza}` (net anual din PFA/SRL)
- `U.cheltuieliLunar(p)` → number · `U.cashFlow(p)` → `{venit, cheltuieli, rate, economii, rataEconomisire}`
- `U.activeTotal(p)` · `U.avereInvestibila(p)` (exclude locuința proprie+auto) · `U.datoriiTotal(p)`
- `U.avereNeta(p)` → `{active, datorii, net}`
- `U.proiectieFiscala(p)` → `{total, componente:[{nume,suma}], termen(Date), zileRamase, structura, tvaPlatitor}`
- `U.fire(p)` → `{cheltAnual, capitalTinta, capitalCurent, progres(0..1), economiiLunare,
                  aniRamasi(poate fi Infinity), dataLibertate(Date|null), varstaLibertate, venitPasivLunar}`
- `U.scorSanatate(p)` → `{scor(0-100), eticheta, componente:[{nume,scor,pondere,detaliu,sfat}], prioritati:[top3]}`
- `U.optimStructura(cifraAnuala, cheltuieliAnuale, dependenti)` →
      `{variante:[{tip,net,taxe,nota,rang,best}], best, diferenta}` (sortate desc după net)
- `U.deadlines(p, an?)` → `[{data(Date), titlu, tip("du"|"tva"|"srl"|"salarii"), desc}]` (doar viitoare, sortate)
- `U.protectie(p)` → `{venitAnual, datorii, aniSprijin, fondCopii, nevoie, acoperitDeAvere, gap,
                       areDependenti, necesitaSuccesiune, areFirma}`
- `U.alocare(p)` → `{tinta:[{clasa,pct,cheie,nota,sumaTinta,sumaCurenta,pctCurent,diferenta}], investibil, risc}`
- `U.profileContext(p)` → obiect pentru AI `{..., rezumat(text), nota}` sau `null` dacă n-are date

### 2.4 Componente vizuale gata făcute
- `U.ringSVG(val, {size, stroke, color, label, sub})` → string SVG (inel de progres). `val`=0..1.
  Ex: `U.ringSVG(fire.progres, {size:160, label:CF.pct(fire.progres), sub:"spre libertate"})`

### 2.5 Constante fiscale (din `fiscal-2026.js`, namespace `CF_FISCAL`)
`F.salariuMinim` (4050), `F.praguri{p6,p12,p24,p72}`, `F.cote{...}`, `F.micro{plafonEUR:100000,cota:.01}`,
`F.tva{plafonInregistrare:395000}`, `F.declaratiaUnica{termen}`, `F.cursEUR()`,
funcții: `F.pfaReal()`, `F.srlMicro()`, `F.salariuNet()`, `F.impozitChirii()`, `F.cassPasiv()` etc.

---

## 3. CLASE CSS (din `cf-ultra.css`)

Layout: `.u-page` (wrapper obligatoriu), `.u-hero`, `.u-grid .u-grid-2/3/4`, `.u-span-2`
Text: `.u-eyebrow` (serif auriu majuscul), `.u-crest` (titlu mare; `.u-crest em` = auriu italic),
      `.u-lead`, `.u-badge-ultra` (◆ Ultra)
Panou: `.u-panel` (secțiune-extras cu hairline auriu sus), `.u-label` (eyebrow în panou),
       `.u-panel-h`, `.u-hr` (divider auriu)
Cifre: `.u-kpi` (`.lg`/`.sm`), `.u-kpi-sub`, `.u-pos`/`.u-neg`/`.u-gold-t`, `.u-delta`
Registru: `.u-row` cu `<span class="k">`…`<span class="lead-dots">`…`<span class="v">`
Semnătură: `.u-ringwrap`, `.u-gauge`(`.track`>`.fill`(`.warn`/`.ok`)+`.marker`, `.ends`),
           `.u-timeline`>`.u-tl-item`(`.soon`)>`.u-tl-date`/`.u-tl-title`/`.u-tl-desc`
Alerte: `.u-alert`(`.gold`/`.warn`/`.ok`) cu `.h`
Chips: `.u-chip`, `.u-chips`
Butoane: `.u-btn`(`.u-btn-gold`/`.u-btn-ghost`)
Card-modul (hub): `.u-mod` > `.u-panel` cu `.ic`/`h3`/`p`/`.more`
Forme: `.u-field`>`label`+`.hint`+`.u-input`/`.u-select`, `.u-fieldset`>`legend`

Gauge exemplu:
```html
<div class="u-gauge"><div class="track"><div class="fill" style="width:62%"></div>
  <div class="marker" style="left:62%"></div></div>
  <div class="ends"><span>0</span><span>Plafon 395.000 lei</span></div></div>
```
Registru exemplu:
```html
<div class="u-row"><span class="k">Salariu net</span><span class="lead-dots"></span><span class="v">8.200 lei</span></div>
```

---

## 4. PAGINILE (fiecare agent primește una sau două — vezi prompt)

- **/ultra.html** (HUB): hero crest „Biroul tău financiar privat" + `.u-badge-ultra`, lead, un rând de
  3 KPI live din profil (avere netă, economii/lună, scor sănătate) DACĂ are date — altfel un CTA elegant
  „Începe cu profilul". Apoi grilă `.u-mod` cu toate modulele (cockpit, concierge, simulator, optimizator,
  calendar, libertate, protecție, alocare, seif, profil), fiecare cu iconiță + descriere scurtă. Jos: o bandă
  „de ce Ultra" (3-4 puncte) + disclaimer. Linkuri către `/ultra/<slug>.html`.
- **/ultra/profil.html**: formularul-backbone. Secțiuni (`.u-fieldset`): Persoană, Structură & venituri
  (afișează dinamic câmpurile relevante structurii alese), Cheltuieli lunare, Datorii (listă cu adăugare/
  ștergere rânduri), Avere (active), Obiective & risc. Buton „Salvează" → `U.salveaza(p)`. Toggle „Sincronizează
  în cloud (cross-device)” → setează `p.sync`. La salvare: mic rezumat live (venit net, avere netă, scor) +
  link „Vezi Cockpitul”. Pre-populează din `U.getProfil()`. Profil gated ultra.
- **/ultra/cockpit.html** (CENTRUL DE COMANDĂ): cea mai importantă pagină. Sus: 4 KPI mari (Avere netă cu
  active/datorii, Venit net lunar, Economii/lună + rată, Venit pasiv azi). Apoi panouri: inelul SCOR DE
  SĂNĂTATE (ringSVG) + top 3 priorități; inelul FIRE (progres + ani rămași + data libertății); PROIECȚIE
  FISCALĂ (cât datorezi la DU + zile rămase + componente); FLUX LUNAR (venit/cheltuieli/economii); URMĂTOARELE
  TERMENE (mini-timeline din `U.deadlines`, primele 3); ALERTE proactive (vezi mai jos). Empty state dacă nu e profil.
- **/ultra/concierge.html**: chat ca asistent-anaf DAR personalizat. La fiecare mesaj, trimite
  `CF.aiChat(messages, {context: U.profileContext()})`. Sus, un mic „card de profil" (venit, avere, scor) ca
  userul să vadă că AI-ul îi cunoaște cifrele. Sugestii de întrebări specifice profilului. Ultra = nelimitat
  (`CF.aiQuota()` e Infinity). Markdown→HTML simplu (bold, liste, tabele, fără HTML brut). Persistă conversația
  în localStorage. Dacă n-are profil, oferă să-l completeze (dar lasă chatul să meargă general).
- **/ultra/simulator.html**: „Și dacă…”. Scenarii cu butoane: pierd jobul, fac un copil, cumpăr casă (rată nouă),
  măresc veniturile cu X%, trec PFA→SRL/SRL→PFA, ies la pensie la vârsta Y. Fiecare scenariu clonează profilul,
  aplică modificarea și RE-rulează `U.cashFlow`/`U.avereNeta`/`U.fire`/`U.scorSanatate`, apoi arată ÎNAINTE→DUPĂ
  pe KPI-uri (cu `.u-delta` colorat). Slider pentru parametri (ex. % creștere venit, mărime rată). Nu salvează profilul real.
- **/ultra/optimizator.html**: optimizatorul de structură. Inputuri: cifră de afaceri anuală, cheltuieli
  deductibile, dependenți (pre-populate din profil dacă există). Cheamă `U.optimStructura(...)`, afișează
  variantele sortate ca panouri (best = evidențiat auriu cu `.u-badge-ultra`/`.u-chip`), fiecare cu net în mână,
  taxe, notă. Sus: „Cu structura ta actuală pierzi/câștigi X lei/an față de optim”. Tabel comparativ + disclaimer.
- **/ultra/calendar.html**: calendar fiscal personal. `U.deadlines(p)` → `.u-timeline` cu toate termenele,
  marcând cu `.soon` ce e sub 30 zile. Fiecare item: buton „Adaugă în calendar” (`CF.icsDownload`) + „Amintește-mi”
  (`CF.setReminder`). Sus, un panou „Următorul termen” mare cu zile rămase. Filtrare pe tip (DU/TVA/SRL/salarii).
- **/ultra/libertate.html**: Raportul „Drumul spre Libertate”. Pagină-raport elegantă: inelul FIRE mare,
  capital curent vs țintă (gauge), economii/lună, ani rămași + data + vârsta libertății, venit pasiv azi vs țintă.
  O proiecție pe ani (tabel: peste 5/10/15/20 ani averea estimată). Buton „Descarcă raportul (PDF)” →
  `CF.printResult(...)`. Mesaj motivant pe situația lui. Snapshot lunar via `CF.logEntry("ultra-cockpit", period, {...})`.
- **/ultra/protectie.html**: „Scutul familiei”. `U.protectie(p)` → nevoia de acoperire (asigurare de viață),
  cât acoperă deja averea, GAP-ul (cu gauge). Explică de ce (datorii + ani de venit pt familie + fond studii copii).
  Checklist succesiune (testament/donație/sediu), „dosarul de urgență” (unde sunt conturile/documentele) ca listă
  pe care o poate bifa (salvată în localStorage). Disclaimer: orientativ, nu sfat juridic/asigurări.
- **/ultra/alocare.html**: „Harta banilor”. `U.alocare(p)` → alocarea țintă (acțiuni/ETF, titluri de stat,
  cash tactic, alternative) pe vârstă+risc, vs alocarea curentă. Bare/gauge pentru fiecare clasă (țintă vs real +
  diferența „mai pune / redu”). Sus: fondul de urgență (câte luni acoperite, gauge). Slider risc (mica/medie/mare)
  care re-rulează. Instrumente RO concrete în note (Fidelis, ETF prin broker). Disclaimer: educativ, nu sfat de investiții.
- **/ultra/seif.html**: „Seiful de documente”. Generatoare de șabloane personalizate pe profil: Decizie AGA
  distribuire dividende, Contract de comodat (sediu social la domiciliu), Contract prestări servicii, Antet factură.
  Userul completează câmpurile rămase, apasă „Generează” → randează documentul + buton „Printează/PDF” (`CF.printResult`).
  Folosește numele/firma din profil unde se poate. Disclaimer: șabloane orientative, verifică cu un specialist.

---

## 5. DEFINITION OF DONE (per pagină)
- Pagina se deschide fără erori în consolă; nicio valoare NaN/undefined afișată.
- Empty state elegant când nu există profil (link la `/ultra/profil.html`).
- Gated `ultra` (adminul vede tot). Arată premium în AMBELE teme (light + dark) — testează mental ambele.
- Cifrele vin din `CF.U` (nu hardcodate). Disclaimer educativ unde sunt cifre fiscale.
- Mobil ok (grid colapsează). Copy în română, sentence case, calm-premium.
- Scrie fișierul direct la calea indicată. NU porni build scripts. NU edita alte fișiere.
