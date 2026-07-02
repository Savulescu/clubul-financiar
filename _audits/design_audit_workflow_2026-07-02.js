export const meta = {
  name: 'cf-design-site-audit',
  description: 'Audit complet design + site clubulfinanciar.ro: 12 auditori paraleli + verificare adversarială',
  phases: [
    { title: 'Audit', detail: '12 auditori paraleli (vizual + cod)' },
    { title: 'Verify', detail: 'verificare adversarială P0/P1' },
  ],
}

const REPO = '/Users/savulescucristian/clubul-financiar'
const SHOTS = '/private/tmp/claude-501/-Users-savulescucristian/9d08327c-1daf-4acb-bb12-651622834e53/scratchpad/shots'

const FINDINGS_SCHEMA = {
  type: 'object', required: ['findings'], additionalProperties: false,
  properties: {
    findings: {
      type: 'array', maxItems: 14,
      items: {
        type: 'object', required: ['title', 'severity', 'area', 'evidence', 'recommendation', 'effort'],
        additionalProperties: false,
        properties: {
          title: { type: 'string' },
          severity: { type: 'string', enum: ['P0', 'P1', 'P2', 'P3'] },
          area: { type: 'string' },
          files: { type: 'array', items: { type: 'string' } },
          evidence: { type: 'string', description: 'Ce ai văzut concret (screenshot/linie de cod), verificabil' },
          recommendation: { type: 'string', description: 'Fix concret, acționabil' },
          effort: { type: 'string', enum: ['S', 'M', 'L'] },
        },
      },
    },
  },
}

const VERDICT_SCHEMA = {
  type: 'object', required: ['isReal', 'reason'], additionalProperties: false,
  properties: {
    isReal: { type: 'boolean' },
    reason: { type: 'string' },
    correctedSeverity: { type: 'string', enum: ['P0', 'P1', 'P2', 'P3'] },
  },
}

const CONTEXT = `
CONTEXT (obligatoriu de respectat):
- Site: clubulfinanciar.ro — educație financiară RO. Repo static site: ${REPO}, paginile live în ${REPO}/docs (GitHub Pages).
- Identitate vizuală EXISTENTĂ și APROBATĂ de owner: „birou financiar privat" — navy (#081728/#0f2540), auriu, crem, verde-emerald accent; fonturi Fraunces (titluri serif), Inter (corp/cifre tabulare), Sora (display). CSS: docs/assets/style.css + upgrade.css + cf-ultra.css (tokeni u-*, clasa .u-page face remap premium) + cf-tool.css. site.js aurește nav-ul dacă există main.u-page.
- Ownerul (Cristian) vrea „ultra mega premium", a respins lucruri „banale/fade". NU propune înlocuirea identității — propune ELEVARE, rafinare, coerență, detalii premium.
- Screenshot-uri existente (PNG, citește-le cu Read): ${SHOTS}/baseline/ (15 pagini × 1440+390, light), ${SHOTS}/baseline2/ (restul paginilor, posibil încă în curs de generare), ${SHOTS}/baseline-dark/ (dark mode), ${SHOTS}/after-upage/ (articol premium DUPĂ fixul split-brain deja aplicat în working tree).
- Fix deja aplicat în working tree (branch design-2026-07-02): cele 692 articole premium au primit <main class="u-page"> — deci articolele sunt acum pe skin auriu. Nu raporta asta ca problemă.
- Dacă un screenshot lipsește, poți genera singur: cd ${REPO} && CF_SHOTDIR=${SHOTS} node _shot.js <label-unic-al-tău> <pagini...> (desktop 1440 + mobil 390 automat; CF_THEME=dark pentru dark mode). Folosește un label unic ca să nu suprascrii.
- AUDIT ONLY: NU modifica niciun fișier din repo.
- Răspunde cu findings concrete, verificabile, cu file paths. Severity: P0=rupt/inacceptabil, P1=slăbește serios calitatea premium, P2=rafinare valoroasă, P3=nice-to-have. Max 14 findings, cele mai valoroase.
`

phase('Audit')

const AUDITORS = [
  { key: 'home-pages', prompt: `${CONTEXT}
Ești design lead. Auditează VIZUAL paginile de prezentare: index (homepage), incepe-aici, despre, contact, feedback. Citește screenshot-urile din ${SHOTS}/baseline/ și ${SHOTS}/baseline2/ (index__1440.png, index__390.png, incepe-aici__*, despre__*, contact__*, feedback__*) și HTML-ul lor din ${REPO}/docs/. Evaluează: ierarhie vizuală, tipografie (scale, ritm), spacing, calitate hero, CTA-uri, micro-detalii premium (umbre, borduri, hover), copy-ul din UI, coerența cu identitatea navy/auriu. Ce ar face un studio premium diferit? Findings concrete.` },
  { key: 'article', prompt: `${CONTEXT}
Ești design lead specializat în experiențe editoriale. Auditează ÎN PROFUNZIME template-ul de articol (cea mai importantă suprafață — 1000 de pagini, intrarea principală din Google). Citește ${SHOTS}/after-upage/articole_actiuni-defensive-vs-actiuni-ciclice__1440.png și __390.png, ${SHOTS}/baseline/articole_*__*.png (varianta veche), plus HTML: ${REPO}/docs/articole/actiuni-defensive-vs-actiuni-ciclice.html (premium) și abonamentele-uitate-care-iti-mananca-banii.html (gratuit), ${REPO}/docs/assets/article.js, cf-article.css. Evaluează experiența de citit: măsura liniei, leading, mărimea fontului, ierarhia H1/H2/H3, cuprinsul, meta-row, progress widget, lockbox-ul Premium (conversie!), bannerul de test, navigarea lecție-anterioară/următoare, articole conexe, share row. Cum arată vs un editorial premium (Stripe blog / FT / substack-uri bune)? Findings concrete cu recomandări de elevare.` },
  { key: 'hubs', prompt: `${CONTEXT}
Ești design lead. Auditează VIZUAL paginile hub: educatie, calculatoare (hub), cursuri (hub), teste, masterclass, investitii, credite. Screenshots în ${SHOTS}/baseline/ și ${SHOTS}/baseline2/ (educatie__*, calculatoare__*, cursuri__*, teste__*, masterclass__*, investitii__*, credite__*) + HTML în ${REPO}/docs/. Evaluează: grid-uri de carduri (monotonie? ierarhie?), progress bars, badges, densitate, scanabilitate, CTA-uri, diferențiere între niveluri/categorii. Findings concrete.` },
  { key: 'news-glosar', prompt: `${CONTEXT}
Ești design lead. Auditează VIZUAL: stiri, stiri-externe, glosar. Screenshots în ${SHOTS}/baseline/ și ${SHOTS}/baseline2/ + HTML în ${REPO}/docs/. Știrile: carduri sursă+timp, filtre pill, paywall band. Glosarul: pagină FOARTE lungă (14000px+) — navigare alfabetică, scanabilitate, tipografie definiții. Findings concrete.` },
  { key: 'premium-ultra-auth', prompt: `${CONTEXT}
Ești design lead. Auditează VIZUAL: premium.html (pagina de pricing — conversia!), ultra.html (hub Ultra), ultra/cockpit.html, ultra/terminal.html, login.html, account.html. Screenshots în ${SHOTS}/baseline/ și ${SHOTS}/baseline2/ + HTML în ${REPO}/docs/. Pricing: claritate tiere, toggle lunar/anual, ancoraj, trust. Ultra: promisiunea „birou privat" se simte? Auth: login/account premium sau generic? Findings concrete.` },
  { key: 'tools', prompt: `${CONTEXT}
Ești design lead pe product/tools. Auditează VIZUAL instrumentele interactive: calculatoare/dobanda-compusa.html, calculatoare/credit.html, calculatoare/fire.html, instrumente.html (hub), instrumente/asistent-anaf.html, unelte/planul-meu-financiar.html, manual/buget.html. Screenshots în ${SHOTS}/baseline/ și ${SHOTS}/baseline2/ + HTML/CSS/JS relevant (${REPO}/docs/assets/cf-tool.css, cf-tool.js). Evaluează: formulare (labels, inputs, focus), rezultate (ierarhia cifrelor, grafice — bare aurii), stări goale, feedback la interacțiune, mobile. Findings concrete.` },
  { key: 'mobile', prompt: `${CONTEXT}
Ești design lead pe mobile. Auditează TOATE screenshot-urile __390.png din ${SHOTS}/baseline/, ${SHOTS}/baseline2/ și ${SHOTS}/after-upage/. Evaluează: nav/burger (deschide HTML să vezi comportamentul: ${REPO}/docs/assets/site.js, header în orice pagină), tap targets, tipografie la 390px (prea mare/mică?), spacing, tabele/grafice pe ecran îngust, footer, CTA-uri sticky?, orice overflow orizontal sau element rupt. Mobilul e majoritatea traficului SEO. Findings concrete.` },
  { key: 'dark', prompt: `${CONTEXT}
Ești design lead. Auditează DARK MODE: screenshots în ${SHOTS}/baseline-dark/ (index, educatie, premium, stiri, calculator, articole, glosar, contact, despre la 1440+390). Dacă lipsesc pagini importante (ex. articol după fix), generează cu CF_THEME=dark. Evaluează: contrast, suprafețe navy corecte vs pete albe scăpate, auriul pe fundal închis, gradienți, borduri, imagini/grafice, inputuri. Compară cu light. Findings concrete cu selectori/fișiere CSS de fixat (caută [data-theme="dark"] în ${REPO}/docs/assets/*.css).` },
  { key: 'css-arch', prompt: `${CONTEXT}
Ești senior CSS engineer. Auditează ARHITECTURA CSS: ${REPO}/docs/assets/style.css, upgrade.css, cf-ultra.css, cf-article.css, cf-tool.css, cf-preview.css, upgrade vs style overlap, plus <style> inline din pagini (compară index.html, stiri.html, educatie.html, glosar.html, articole/*.html — cât inline style dublat există între pagini? drift?). Verifică: tokeni duplicați/contradictorii, specificitate care se calcă (ex. .u-page remap vs stiluri directe), cod mort, consistența ?v= cache versions între pagini și buildere (${REPO}/_build_site.py, _build_glosar.py, _build_manual.py, _build_masterclass.py, _shell_nav.html, _shell_foot.html). Findings concrete cu numere de linie.` },
  { key: 'perf', prompt: `${CONTEXT}
Ești performance engineer. Auditează PERFORMANȚA site-ului static din ${REPO}/docs: mărimi fișiere (du -sh pe assets, imagini, og-image.jpg/png, media/), fonturi Google (câte familii×greutăți se încarcă? render-blocking? font-display?), three.js de pe CDN (unde se încarcă — doar homepage sau peste tot?), tilt.js/site.js/article.js defer?, CSS render-blocking total (style+upgrade+cf-ultra = câți KB?), imagini fără width/height sau lazy, CSP, cache. Măsoară cu curl/ls, nu presupune. Recomandă fix-uri cu impact real pe LCP/CLS mobile (traficul SEO). Findings concrete.` },
  { key: 'a11y', prompt: `${CONTEXT}
Ești accessibility engineer. Auditează ACCESIBILITATEA: ${REPO}/docs — contrast (auriul #c-ceva pe crem! verifică valorile din cf-ultra.css/upgrade.css cu calcul WCAG real), focus states vizibile (butonul Cont, pill-uri, inputuri), aria pe burger/search/theme (site.js), alt pe imagini, ordinea headingurilor în articole/hub-uri, form labels în calculatoare/login, emoji folosiți ca iconițe (🔍🌙☰ — screen readers), prefers-reduced-motion (upgrade.css/compound.js/three3d.js), touch targets. Findings concrete cu valori de contrast calculate și selectori.` },
  { key: 'integrity', prompt: `${CONTEXT}
Ești QA engineer. Auditează INTEGRITATEA site-ului din ${REPO}/docs: scrie un mic script Python în scratchpad (nu în repo!) care extrage toate href/src interne din TOATE .html (inclusiv articole/) și verifică existența fișierelor țintă (atenție la /path fără .html → path.html sau path/index.html, anchors #, query ?v=). Raportează 404-uri interne. Apoi: sitemap.xml vs fișiere reale (diferențe), robots.txt, canonical-uri corecte pe sample, og-image existent, manifest/favicon-uri, pagini orfane (0 inbound links), drift între _shell_nav.html și nav-ul real din pagini (diff), 404.html există pentru GitHub Pages? Findings concrete.` },
]

const results = await pipeline(
  AUDITORS,
  a => agent(a.prompt, { label: `audit:${a.key}`, phase: 'Audit', schema: FINDINGS_SCHEMA }),
  (res, a) => {
    if (!res || !res.findings) return { key: a.key, findings: [] }
    const top = res.findings.filter(f => f.severity === 'P0' || f.severity === 'P1').slice(0, 5)
    return parallel(top.map(f => () =>
      agent(`Ești un sceptic riguros. Încearcă să REFUȚI acest finding despre site-ul static din ${REPO}/docs (identitate navy/auriu premium, vezi contextul). Finding de la auditorul "${a.key}":
TITLU: ${f.title}
SEVERITY: ${f.severity}
FILES: ${(f.files || []).join(', ')}
EVIDENCE: ${f.evidence}
RECOMANDARE: ${f.recommendation}
Verifică TU ÎNSUȚI în repo/screenshots (${SHOTS}) dacă problema e reală, dacă severity e corect, și dacă recomandarea nu strică altceva (ex. remap .u-page, cele 1000 de articole generate, builderele _build_*.py). NU modifica fișiere. isReal=false dacă e speculativ/greșit/deja rezolvat.`,
        { label: `verify:${a.key}:${f.title.slice(0, 40)}`, phase: 'Verify', schema: VERDICT_SCHEMA })
        .then(v => ({ ...f, auditor: a.key, verdict: v }))
    )).then(verified => ({
      key: a.key,
      findings: res.findings.map(f => {
        const vf = verified.filter(Boolean).find(v => v.title === f.title)
        return vf || { ...f, auditor: a.key, verdict: null }
      }),
    }))
  },
)

const all = results.filter(Boolean).flatMap(r => r.findings || [])
const confirmed = all.filter(f => !f.verdict || f.verdict.isReal)
const rejected = all.filter(f => f.verdict && !f.verdict.isReal)
log(`Audit: ${all.length} findings, ${confirmed.length} confirmate/neverificate, ${rejected.length} respinse`)
return {
  confirmed: confirmed.map(f => ({ ...f, severity: (f.verdict && f.verdict.correctedSeverity) || f.severity })),
  rejected: rejected.map(f => ({ title: f.title, auditor: f.auditor, reason: f.verdict.reason })),
}