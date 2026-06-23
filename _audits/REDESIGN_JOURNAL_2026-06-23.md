# Clubul Financiar — Redesign Journal (2026-06-23, autonomous session)

Mandat (Cristian, pleacă 8–9h): redesign al ÎNTREGULUI site. Vrea, simultan:
**extrem de profesional · extrem de modern · extrem de lizibil · extrem de addictive.**
Să-l surprindă. Să nu mă opresc la prima variantă; loop continuu, check la 20 min.
Bază actuală: „cream gold premium / old money". Permis: 3D, rearanjare, idei noi.

Branch sigur: `redesign-2026-06-23` (NU ating `main` = live via GitHub Pages docs/).

---

## Starea reală (verificată, nu presupusă)

- Fonturi DEJA încărcate în `index.html`: **Fraunces** (serif display+italic, opsz),
  **Plus Jakarta Sans**, **Sora**. Nu e site pe fonturi de sistem.
- **3D real**: Three.js (importmap) + `assets/three3d.js` → hero `#hero3d` (grafic creștere 3D).
- Skin „Pilot Ultra": `cf-preview.css` (16KB) remapează tokenii verzi vechi → navy/auriu
  „birou privat", peste `style.css` (18KB, tokeni de bază) + `upgrade.css` (34KB).
- Paletă tokeni de bază: `--emerald #10b981 · --blue #2563eb · --navy #0f2540 ·
  --gold #E8C268 · crem #f5f8fc/#eef4fb`. Temă light/dark.
- Pagina premium: crem + navy + auriu + serif italic; 4 tiere 0/49/99/199 lei.
- Deploy: GitHub Pages din `main`/`docs/`. Commit pe main = LIVE. → lucrez pe branch.

Baseline screenshots: `_audits/redesign_shots/00_baseline_{index,premium}.png`.

## Diagnostic critic

Designul actual e BUN, dar stă periculos de aproape de clișeul AI-default #1
(„cream + serif înalt-contrast + accent auriu/teracotă"). Ca să fie EXTRAORDINAR,
nu repet auriu+serif — îl împing într-un loc unde un site generic nu poate ajunge.

## Teza de design v0 — „Birou financiar privat, dar VIU"

Păstrez gravitas-ul old-money; îl fac să respire DATE REALE RO și să răsplătească atenția.
Trei mișcări (de rafinat cu deep-research + agenți):

1. **Tipografie cu autoritate + cifre de terminal.** Scală deliberată; Fraunces cu
   restrângere (nu peste tot); un grotesc sigur pentru UI; **mono cu tabular figures
   pentru TOȚI banii/cifrele** (credibilitate financiară — acum lipsește). Cifrele =
   substanța brandului, tratate ca într-un terminal.
2. **Date RO live ca textură + momente interactive.** Au deja buildere fx/macro/BVB/news.
   „Bandă" live discretă + hero = instrument REAL de dobândă compusă (slider → curbă
   aurie crește live, cifre reale). Semnătura non-templated, imposibil de confundat.
3. **Profunzime disciplinată, nu decor.** Lumină hârtie/aur stratificată, 3D rafinat pe
   hero, un SINGUR page-load orchestrat, tilt doar unde merită. Boldness într-un loc;
   restul liniștit, lizibil, aer mult. Lizibilitate: line-height ↑, măsură ~66ch,
   contrast AA, bază mai mare.

**Riscul (unul):** prima impresie = „midnight" — ink-navy profund + lumină aurie + cifre
live (private banking after-hours), apoi pagina se rezolvă în crem cald spre zona de
învățare. Dualitatea noapte→zi = surpriza memorabilă. DE VALIDAT — poate fi prea mult.

## Infrastructură iterație
- `_screenshot.sh <label> [pages]` → desktop 1440 + mobile 390 în scratchpad/shots/.
- Skill: `.claude/skills/run-cf-site/SKILL.md` (run-skill-generator deliverable).
- Deep-research în fundal (premium-modern-addictive, piața RO).
- Explore agent în fundal: cartografiază tot designul curent.

---

## LOG (cel mai nou jos)

- **[setup]** Branch creat, baseline salvat, infra gata, research+map pornite în fundal.
  Next: sintetizez map+research → blochez tokenii (fonturi/paletă/mișcare) → prototip hero.

- **[map done]** Explore agent → DESCOPERIRE CHEIE: site SPLIT-BRAIN.
  `.u-page` (cf-ultra.css) = skin premium navy/auriu pe: index, educatie, instrumente,
  ultra, ~1600 articole. DAR multe pagini NU au .u-page → încă look-ul vechi emerald/blue:
  premium, calculatoare, investitii, credite, stiri, statistici, glosar, contact, despre,
  account, login, masterclass, incepe-aici, feedback, cursuri, teste.
  6 straturi CSS: style(base tokens)→upgrade(scale,--font-display:Sora,--font-body:Jakarta)
  →cf-ultra(.u-page navy/gold)→cf-tool→cf-preview→cf-article(remap 13 linii, critic).
  Token .u-* se aplică la request-time → retunarea paletei = INSTANT pe toate cele 1600
  articole, FĂRĂ rebuild. Pârghie sigură.
  Fonturi: Fraunces(serif, headings .u-page), Sora(--font-display), Plus Jakarta(--font-body).

  STRATEGIE CRISTALIZATĂ (ordine de impact):
  1. UNIFICARE: ridic limbajul premium la nivel de site întreg (nu doar .u-page) →
     rezolvă split-brain = cel mai mare câștig de coerență. Promovez paleta/typo „birou
     privat" pe body, .u-page devine accent, nu insulă.
  2. ELEVARE limbaj: scală tipografică rafinată + cifre mono tabulare pt bani; profunzime
     disciplinată; mișcare orchestrată (1 page-load); semnătura = instrument dobândă compusă.
  3. PER-PAGINĂ bespoke: home, premium, educatie, instrumente, calculatoare + restul.
  Verific fiecare pas cu _screenshot.sh (1440 + 390). Boldness într-un singur loc.

- **[verifier fixed]** Built `_shot.js` — Chrome+CDP full-page capture: waits fonts+images,
  sizes viewport to full content height (so .reveal scroll-anims show, nu jumătate goală),
  2.2s settle for WebGL hero. Verified 3D bars paint EVERY run (2/2). Skill `run-cf-site`
  documents it. ⚠️ Inconsistență găsită: homepage pricing în € (0/9.99/19.99/49.99) vs
  premium.html în lei (0/49/99/199) — de unificat. Baseline 25 pagini în /tmp/cf_baseline.
  Next wake: review baseline (sample old-look pages), sintetizez deep-research, încep ELEVAREA
  homepage (task #3): tokeni + scală tipografică + cifre mono tabulare + instrument compus.

## ════ SISTEM DE DESIGN v1 — LOCKED (bazat pe dovezi) ════
Brief construit din deep-research (111 agenți, 19 claim-uri confirmate, 6 respinse).

RESPINSE (de respectat): „trebuie RON" (multe servicii RO afișează €; contează CONSISTENȚA,
nu moneda) · „mono necesar pt cifre" (ajunge tabular-nums pe Inter) · „streaks = motor #1"
(nu supra-licita) · „3-tier convert 1.4×" (nestabilit).

TIPOGRAFIE (cea mai mare pârghie + rezolvă split-brain tipografic Sora/Fraunces):
- DISPLAY/headings → **Fraunces** peste tot (suflet old-money, deja încărcat). Acum: Sora pe
  paginile vechi, Fraunces pe .u-page = inconsistent. Unific la Fraunces.
- UI/body/CIFRE → **Inter** (variable, gratis, diacritice RO complete, tabular by default;
  #1 în fintech per research). Înlocuiește Plus Jakarta + Sora ca workhorse.
- BANI/DATE → `font-variant-numeric: tabular-nums lining-nums` pe orice sumă/preț/ticker/KPI.
  „Zecimale nealiniate erodează încrederea instant."

CULOARE (judecata mea — research n-a dat finding verificat; advisor: surpriza din stratul VIU,
nu inversare paletă): păstrez navy+auriu „birou privat", dar ESCAPE clișeu prin:
(a) culoarea = SEMNIFICAȚIE de date (verde=up, roșu=down, financiar-adevărat), nu decor;
(b) aur ca structură/accent (hairlines, cifre-cheie), nu peste tot; (c) mai mult aer/restrângere;
(d) diferențiatorul real = stratul interactiv/viu.

MIȘCARE: restrângere + intenție. Reveal pe transform/opacity (IntersectionObserver, deja există).
UN singur page-load orchestrat în hero. Microinteracțiuni pe hover. ZERO scrolljacking
(rău pt site educațional de scanat). Respect prefers-reduced-motion.

ENGAGEMENT (etic; Duolingo: motivația e bottleneck-ul, nu conținutul): progres vizibil
(citire/lecții), personalizare („numărul TĂU" prin instrumentul compus), continuitate blândă.

SEMNĂTURĂ: instrument interactiv de dobândă compusă în hero — date SEED/local, ZERO network,
cifre tabulare, curbă aurie. Elementul „addictive" + unic, imposibil de confundat.

PRICING: 3 tiere cu ancoră ANUALĂ (15-20% off = „2 luni gratis") + structură decoy (Ariely
32%→84%). Monedă CONSISTENTĂ (înclin RON pt retail; ACUM bug: homepage € vs premium lei).
Recurent RO = card-on-file + 3DS2.

PLAN BUILD: prove-on-homepage întâi → propagare la sursă (componente .btn/.card/.stat),
consolidare NU al 7-lea strat. Commit per increment verificat cu _shot.js.

- **[tick 2]** Pixel-audit: harta GREȘITĂ — `calculatoare` e DEJA premium (Fraunces/auriu/crem),
  NU emerald vechi. Trust pixels. _shot.js robustness fix (profil+port Chrome unic per PID, era
  stall pe profil partajat). Baseline complet relansat (bg). Citit markup hero index.html:
  `.hero` = #hero3d (Three.js, aria-hidden, ambient) + text stânga + `.hero-caption` static dreapta.
  Pricing homepage în € (0/9.99/19.99/49.99) vs premium.html lei → bug consistență.
  SEMNĂTURĂ draftată + math-verificată (scratchpad/compound_component.html): instrument
  dobândă compusă interactiv (slider lună + pills ani + sparkline auriu SVG + count-up tabular),
  100% local. 500lei×20ani→294.510 lei (174.510 dobândă). Înlocuiește .hero-caption static.
  Contact-sheet generator gata. NEXT: contact sheet → vezi toate paginile → integrez instrumentul
  în hero → screenshot → iterez. Apoi fundație Inter+tabular la sursă.

- **[tick 3 — HOMEPAGE HERO ELEVAT ✓]** Semnătura LIVE pe index.html, verificată desktop+mobil:
  • Font link: Inter + Fraunces (dropped Sora+Plus Jakarta de pe homepage).
  • `html{--font-body:Inter}` + cifre tabulare pe stats/preț/instrument. Toate 'Sora'→'Inter'.
  • `.hero-caption` static ÎNLOCUIT cu instrument dobândă compusă interactiv (assets/compound.js):
    slider lună + pills ani + sparkline auriu SVG + count-up tabular, 100% local. 3D rămâne ambient.
  • Pricing € → lei (0/49/99/199) — consistent cu premium.html.
  • Verificat: 294.510 lei la 500/lună×20ani (corect), 3D pictat, mobil stivuit OK.
  Shots: _audits/redesign_shots/01_home_hero_after{,_mobile}.png.
  NEXT iterație homepage: rafinez (3D să stea mai mult backdrop sub panou? secțiunile de jos?);
  apoi PROPAGARE Inter+tabular la sursă (upgrade.css + restul paginilor) = task #4.

- **[tick 4 — TIPOGRAFIE PROPAGATĂ SITE-WIDE ✓]** Contact-sheet 13 pagini → split-brain MAI MIC
  decât zicea harta: majoritatea deja premium crem/auriu. Outlieri vechi: contact (alb+albastru
  „Vorbește cu noi"), cursuri (parțial), pagini-utilitar. Propagare la SURSĂ unică:
  upgrade.css @import → Inter+Fraunces+Sora pe TOATE paginile (fără a atinge 1287 link-uri);
  `--font-body: Inter`; `--font-num` nou; cifre tabulare globale (.stat .num, .price .amt, .u-kpi…).
  Verificat: articol generat + cursuri + premium = corp Inter curat, zero breakage; contact =
  corp Inter dar SKIN încă vechi → bespoke. masterclass.html ATÂRNĂ la captura CDP (de investigat).
  NEXT: bespoke skin pe stragglers (contact întâi) + unificare titluri Fraunces cu grijă (atenție:
  --font-display=Sora e folosit și la cifre); apoi a doua iterație homepage.

- **[tick 5 — SPLIT-BRAIN REZOLVAT pe conținut ✓]** Cauză reală: remap-ul --emerald→auriu era
  duplicat inline doar în 6 pagini; altele premium doar prin clase .u-* în markup; contact n-avea
  nimic. FIX consolidare: mutat remap-ul de tokeni de bază + heading Fraunces + butoane aurii în
  cf-ultra.css `.u-page` (sursă unică). Acum o pagină devine premium DOAR cu class="u-page" +
  link cf-ultra.css. Convertit: contact, despre, statistici, teste, glosar (+ builder _build_glosar.py
  pt durabilitate). Verificat zero regresie pe index/premium/educatie/articole. Buton .btn-primary
  aurit global pe .u-page (nu mai depinde de class="nav ultra").
  REDIRECT-uri (skip): account, credite, cursuri, investitii, login. Legal/utilitar rămas
  (privacy, terms, reset, dezabonare) = impact mic, TODO. ⚠️ hairline verde/albastru sub nav pe
  nav non-ultra = pas de consistență nav (schimb _shell_nav.html → "nav ultra" + navurile hand-authored).
  NEXT: pas consistență nav + a 2-a iterație homepage + pricing psychology premium.

- **[tick 6 — consistență nav]** Hairline `.nav::after` + underline + dot-glow erau verde/albastru
  (--grad-tri/--grad-cool); aurite global în upgrade.css. site.js nav dinamic → "nav ultra".
  Verificat hairline auriu pe glosar+articol. ⚠️ TODO găsit: nav AGLOMERAT la 1440 (8 link-uri →
  „Premium"+brand pe 2 rânduri) = densitate meniu, ține de structura IA (nu schimb autonom).
  ⚠️ TODO: bump cache ?v= pe CSS/JS înainte de merge live (altfel browserele servesc stale).

- **[tick 6b — COERENȚĂ ATINSĂ ✓]** Nav layout fix (brand nowrap + nav-links pe un rând la 1280+).
  Overview 9 pagini (_audits/redesign_shots/05_current_overview.png): index/premium/educatie/
  calculatoare/glosar/contact/despre/instrumente/stiri = TOATE acum același limbaj premium
  auriu/navy/crem + tipografie unită + hairline auriu. Split-brain REZOLVAT pe conținut.
  Task #4 (propagare) ~90%: rămas doar legal/utilitar (privacy/terms/reset/dezabonare, impact mic).
  NEXT (task #5): pricing psychology premium (ancoră anuală + decoy, research) = valoare business;
  a 2-a iterație homepage; legal pages; investigat hang masterclass; FINAL: bump ?v= + doc before/after.
