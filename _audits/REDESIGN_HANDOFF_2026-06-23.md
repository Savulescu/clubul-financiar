# Redesign Clubul Financiar — Handoff (2026-06-23)

Sesiune autonomă de redesign, pe branch **`redesign-2026-06-23`** (NU pe `main` — site-ul live
e neatins). Când ești mulțumit, faci merge. **Citește „⚠️ ÎNAINTE DE MERGE" mai jos.**

## Cum revizuiești rapid
```bash
cd ~/clubul-financiar && git checkout redesign-2026-06-23
node _shot.js review            # screenshot toate paginile (desktop 1440 + mobil 390)
# sau live:  cd docs && python3 -m http.server 8765   → http://localhost:8765
```
Screenshots before/after: `_audits/redesign_shots/` (00_baseline… → 07_…).
Jurnalul complet al deciziilor: `_audits/REDESIGN_JOURNAL_2026-06-23.md`.

## Ce s-a schimbat (rezumat)

**1. Tipografie modernă, lizibilă, unificată** (cea mai mare pârghie)
- **Inter** pentru UI/corp/cifre (variable, gratis, diacritice RO, **figuri tabulare** aliniate
  pentru bani — credibilitate financiară), **Fraunces** serif pentru titluri (suflet „old money").
- Încărcat din sursă unică (`@import` în `upgrade.css`) → se aplică pe TOATE paginile fără a
  atinge cele 1287 de link-uri de font.

**2. Coerență totală — split-brain rezolvat**
- Înainte: unele pagini premium auriu/navy, altele pe vechiul verde/albastru (contact = alb+albastru).
- Acum: remap-ul de skin premium e CONSOLIDAT în `cf-ultra.css .u-page` → orice pagină devine
  premium cu `class="u-page"` + link cf-ultra (înainte era duplicat inline în 6 pagini).
- Aduse în limbaj premium: **contact, despre, statistici, teste, glosar** (+ builder glosar).
- Nav consistent peste tot: hairline auriu (era verde/albastru), buton „Cont" auriu, brandul nu
  se mai rupe pe 2 rânduri, link-urile încap pe un rând la desktop.

**3. Semnătura homepage — instrument interactiv de dobândă compusă** (`assets/compound.js`)
- Înlocuiește cardul static din hero: slider „pun pe lună" + orizont (10/20/30 ani) + curbă aurie
  SVG care se desenează + cifră mare cu count-up tabular. **100% local, zero network.**
- Ex: 500 lei/lună × 20 ani → 294.510 lei (din care 174.510 dobândă).

**4. Moment memorabil — intrare orchestrată a hero-ului**
- La încărcare: eyebrow → titlu → lead → CTA → panou instrument alunecă în scenă → curba se
  desenează singură (~1.5s coregrafiat). Respectă `prefers-reduced-motion` (conținut instant).

**5. Pricing premium — toggle Lunar/Anual interactiv**
- Numărul mare reflectă facturarea aleasă (lunar `/lună` ↔ total anual `/an`); pastilă „2 luni
  gratis". NU am schimbat tierele/prețurile/features (deciziile tale de business) + reparat € → lei.

## Ce e VERIFICAT (screenshot)
- Desktop 1440 + mobil 390; **dark mode** (contact + homepage = navy corect);
- Tool pages complexe (ultra/terminal, ultra/cockpit, instrumente/asistent-anaf) — zero regresie;
- Articole generate, premium, educatie, calculatoare, glosar — coerente;
- `masterclass.html` triat: sănătos (doar foarte înalt, nu buclă infinită).

## ⚠️ ÎNAINTE DE MERGE (OBLIGATORIU — altfel se rupe pe lansare)
**Bump cache `?v=` + regenerare.** Am schimbat `upgrade.css` (v23), `cf-ultra.css` (v1), `site.js`
(v24), dar referințele `?v=` au rămas. Vizitatorii care revin + CDN-ul vor servi **CSS-ul vechi
cache-uit la HTML-ul nou** (contact/despre/glosar au acum `.u-page` care AȘTEAPTĂ remap-ul nou) →
pagini rupte exact pentru userii fideli. De făcut:
1. Bump `?v=` în toate `docs/**/*.html` + cele 4 buildere (`_build_*.py`).
2. Regenerează paginile generate din buildere (ca glosar.html editat direct să nu divergă).
3. Verifică din nou cu `node _shot.js`.
(Status: gata de făcut ca PASUL FINAL — vezi task-ul gated. Îl fac eu la final dacă apuc.)

## De considerat (opțional, nu blocant)
- Densitatea meniului nav (8 link-uri) — încape acum, dar e plin; eventual grupare/IA.
- Pagini legal (privacy/terms/reset/dezabonare) — încă pe skin base; ROI mic, le pot aduce premium.
- Strat „date live RO" (BVB/FX) ca textură ambientală — idee pentru viitor (necesită pipeline-ul tău).
