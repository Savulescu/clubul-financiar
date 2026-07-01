# Redesign / îmbunătățire site — RESUME (sesiune 2026-07-02, oprită la cererea lui Cristian)

Cererea: „îmbunătățește designul pentru clubulfinanciar.ro și tot site-ul" (ultracode, full-max).
**Reluare mâine: citește acest doc + `design_audit_2026-07-02_partial.json`, apoi continuă de la „NEXT".**

## Stare git
- Branch de lucru: **`design-2026-07-02`** (din main @ 0263bdbd). **NEPUSH-uit. Main/live neatins.**
- Commit făcut: `20cdb665` — **FIX MAJOR split-brain**: 692 articole premium erau pe vechiul skin
  alb/albastru (aveau CSS-ul `.u-page` în head dar fără `<main class="u-page">` în DOM; cele 308
  gratuite îl aveau). Patch chirurgical `_fix_article_upage.py` (fără rebuild!) + dedup `</main>`
  orfan pre-existent + `_shot.js` cu suport `CF_THEME=dark`. Verificat screenshot 1440+390 light+dark.
- Uncommitted în working tree: doar `_audits/gsc_submitted.json` (modificare veche, NU e a mea — nu o atinge).

## Audit multi-agent TERMINAT (12/12 auditori, workflow wf_f9a6c122-e17, oprit curat)
- **150 findings** (3×P0, ~46×P1) în **`_audits/design_audit_2026-07-02_partial.json`**
  (structură: `auditors[key] = findings[]`, `verdicts[] = {auditor,title,isReal,reason,correctedSeverity}`).
- 35 verdicte adversariale pe P0/P1: **doar 1 respins** (vezi `isReal:false` în JSON). Restul P0/P1 neverificate ≈ de încredere medie — judecă la implementare.
- Scriptul workflow-ului: `_audits/design_audit_workflow_2026-07-02.js` (re-rulabil cu Workflow tool).

### P0 (toate confirmate/solide)
1. **Hero homepage pe mobil lipit de margine** (padding lateral 0 la 390px) — home-pages, confirmat prin CDP.
2. **stiri-externe LIVE cu placeholdere**: `<h2>titlul tradus</h2>`, `<h2>...</h2>`, `&nbsp;` literal pe carduri — pipeline `news_external.py`, nu doar CSS!
3. **Dark mode: banda newsletter homepage aproape albă** cu text auriu (contrast 1.5:1) — inversare tokeni.

### Teme mari P1 (grupate — planul de implementare de mâine)
- **Coerență skin**: `/unelte/*` (4 pagini) încă pe verde vechi; `teste.html` cu u-page pe `<body>` în loc de `<main>` (nav/footer nu se auresc); login/account fără fonturile brand; footer „două temperaturi".
- **Emoji ca iconografie** peste tot (🔍🌙☰, share „f/W/✈") — exact ce Cristian a respins ca „banal"; de înlocuit cu SVG-uri brand (memoria: obiecte vizuale din Canva, cod doar layout — dar iconografie UI SVG e acceptabilă; la nevoie export din Canva).
- **Articol (1000 pagini)**: cuprins cu ancore moarte + listează cardul de vânzare; fade lockbox spre ALB pe fundal crem; preț lockbox contrast 1.6:1; bare progres rămase verde/albastru.
- **Conversie**: premium.html toggle anual = sticker shock + sub-linie dublată; CTA-uri Vreau Premium/Pro/Ultra aterizează pe aceeași bandă generică; mesaj waitlist invizibil pe light.
- **Footer legal rupt pe TOATE paginile** (separator „·" orfan pe rând propriu) — fix o dată în `_shell_foot.html` + pagini live.
- **News quality**: excerpturi tăiate dur fără elipsă, „The post <b>…</b>" escapat vizibil, „Ce înseamnă pentru tine" șablon pe 42% din carduri (pipeline, nu CSS).
- **Glosar**: navigarea pe litere = cod mort (nu derulează), fără nav persistent la 14.000px.
- **Masterclass**: ~90/200 lecții duplicate near-identice vizibile în grid; 21 titluri fără diacritice; CTA „Învață → →" dublat.
- **Manual/hub instrumente**: numere contradictorii pe același ecran („Ai 35 lecții" vs „0 din 22"); 22/37 unelte invizibile la prima vizită.
- **A11y**: focus ring invizibil (1.45:1); auriul #E8C268 ca text pe deschis 1.5:1; `#9a7414` pică AA (3.75:1); formulare fără label-uri programatice (11 calculatoare + login).
- **Perf**: Google Fonts render-blocking pe ~1.274 pagini (cel mai mare cost LCP mobil); Supabase UMD 51,7KB gz pe toate cele 1000 articole doar pentru analytics.
- **CSS arch**: skinul u-page fragmentat în ~30 copii inline divergente; `?v=` hardcodat în 6 locuri, builderele REGRESEAZĂ la versiuni vechi la următorul build (bump obligatoriu ÎN buildere, nu doar în docs!).
- **Integrity**: lipsește `404.html` (GitHub Pages servește pagina default în engleză).
- Toate detaliile + evidence + recomandări: în JSON.

## Screenshots (evidence, 82MB, NU se comitează)
- `_audits/design_shots_2026-07-02/` — baseline (light), baseline2, baseline-dark, after-upage
  (articol DUPĂ fix), + seturile auditorilor. Adăugat în .gitignore.

## NEXT (planul rămas, în ordine)
1. **Val 1 — P0**: hero mobil padding; dark newsletter band; stiri-externe placeholdere (patch `news_external.py` + regen/curățare carduri stricate).
2. **Val 2 — coerență**: unelte/teste/login/account pe skin auriu; footer legal; 404.html brand.
3. **Val 3 — elevare articol** (suprafața principală SEO): cuprins reparat, lockbox premium (fade crem, preț lizibil), bare progres aurii, share row SVG, tipografie citit (mărime/leading/măsură).
4. **Val 4 — conversie premium.html** + CTA-uri tier + waitlist vizibil.
5. **Val 5 — a11y+perf**: focus ring, contrast auriu (ton nou pt text), label-uri, font-display/preload fonts, Supabase doar unde e nevoie (defer/conditional).
6. **Val 6 — glosar nav + news quality + masterclass dedup** (masterclass dedup = content, poate val separat).
7. **Cache bump `?v=`** peste tot + ÎN buildere (`_build_site.py` etc. — vezi P1 css-arch) — pasul FINAL înainte de re-shoot.
8. Re-shoot totul (`node _shot.js`), comparație before/after, commit-uri pe branch, handoff.
9. **Merge/push pe main DOAR cu OK-ul lui Cristian** (deploy live).

## Capcane cunoscute (nu repeta greșelile)
- **NU rula `_build_site.py` integral** (GLOS_SRC mort → regresie search-index; memoria SEO). Patch-uri chirurgicale pe docs/ + țintit în buildere.
- **Screenshot pe pagini-gigant (masterclass, glosar) îngheață Chrome** la full-height 14.000px cu swiftshader → folosește `_screenshot.sh` (fereastră fixă 1440×2600) pentru ele; `_shot.js` pentru restul.
- `_shot.js`: `CF_THEME=dark` acum funcționează (pre-seed localStorage via CDP). Rulările paralele OK (port per PID), dar nu mai mult de ~2-3 simultan.
- Git email deja corect (clubulfinanciar@gmail.com). Commit-uri în stil RO descriptiv.
- Main primește auto-commits (știri la ~30min) — la merge, rebase/merge fără să atingi `docs/stiri*.html`/`docs/data` dacă divergă.
