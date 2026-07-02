# Redesign / îmbunătățire site — sesiunea 2026-07-02 (FAZA DE IMPLEMENTARE ÎNCHEIATĂ)

Cererea: „îmbunătățește designul pentru clubulfinanciar.ro și tot site-ul" (ultracode, full-max).
Starea: **audit + implementare COMPLETE pe branch `design-2026-07-02` (10 commit-uri). NEPUSH-uit — merge pe main doar cu OK-ul lui Cristian (deploy live).**

## Commit-urile (în ordine)
1. `20cdb665` — split-brain: 692 articole premium pe skinul auriu (main.u-page)
2. `2190179a` — audit 150 findings (12 auditori + verificare adversarială) + JSON
3. `7822dac3` — P0-uri + CSS partajat: hero mobil, dark newsletter, cuprins cu lacăte,
   fade lockbox pe crem, share SVG, bare aurii, focus ring, tokeni gold-ink (a11y), footer cald
4. `422b12e7` — iconografie SVG nav/căutare/cont (zero emoji de sistem în UI-ul global)
5. `3c2beb31` — tile-urile homepage pe iconuri stroke gravate (14, zero emoji)
6. `a19c0f85` — news: P0 placeholdere + igienă text la sursă (gate anti-placeholder,
   unescape ×2, elipsă la graniță de cuvânt, «The post» strip, _scrub_store auto)
7. `7694e119` — premium: toggle anual fără sticker-shock, CTA tier-aware (#plan-X + inel),
   waitlist vizibil ambele teme
8. `b12aff8f` — coerență: unelte×4 + teste + login/account pe identitatea aurie,
   contact reconstruit, docs/404.html NOU brand
9. `1a5f556d` — glosar: navigare litere funcțională, bară alfabetică sticky, back-to-top,
   _build_glosar.py oglindit byte-for-byte
10. `c87d4a11` — polish site-wide 1277 pagini (fonts non-blocking, 948 meta emoji, 54 label
    for=, 226 theme-color navy, gate-uri #plan-X, sitemap 1260 cu unelte) + **cache bump
    UNIFICAT v33** (pagini + toate builderele — nu mai regresează)

## Verificare
- Fiecare val verificat cu screenshot (light+dark, 1440+390): shots în
  `_audits/design_shots_2026-07-02/` (baseline) + scratchpad sesiune (wave-*/final*).
- Audit JSON cu toate findings: `_audits/design_audit_2026-07-02_partial.json`.
- Workflow-uri re-rulabile: `_audits/design_audit_workflow_2026-07-02.js`.

## Ce a rămas pe lista de viitor (nefăcut, decizii/efort separat)
- **Masterclass dedup**: ~90/200 lecții near-duplicate vizibile în grid + 21 titluri fără
  diacritice (content-level, cere regen prin _build_masterclass.py + sursele _data).
- **Manual/hub instrumente**: numere contradictorii („Ai 35 lecții" vs „0 din 22") + 22/37
  unelte invizibile la prima vizită pe hub (IA de prezentare, decizie de produs).
- **Emoji rămase în conținut** (nu în UI global): pills/secțiuni premium.html (📋🎯🔥💡🎁),
  gate-uri 🔒 din cf-tool.js, CATNAMES teste, titluri grupuri unelte. Setul SVG există
  (site.js UI_IC + tile-urile din index) — de extins consistent.
- **Supabase UMD pe articole** (51,7KB gz ×1000 pagini doar pt analytics/auth-slot) —
  decizie de arhitectură (defer condiționat / bundle mic separat).
- **Nav sticky**: upgrade.css §nav îl ține position:relative (suprascrie style.css sticky) —
  descoperit de agentul glosar; glosarul se adaptează runtime oricum. Decizie de UX.
- **82 carduri netraduse pe stiri-externe**: cere LLM cloud; buclele de vindecare din cron
  le repară treptat; gate-ul nou împiedică placeholder-ele.
- Consolidarea celor ~30 de copii inline .u-page în cf-ultra.css (css-arch P1) — făcut doar
  parțial (fișierele partajate au acum sursa de adevăr; inline-urile rămase sunt identice).

## Note operaționale
- stiri-externe.html/stiri.html/data/news*.json sunt regenerate de cron DE PE MAIN la ~30min
  — HTML-urile din branch vor fi suprascrise post-merge; fixurile durabile sunt în
  news_external.py/news_build.py (+ _scrub_store auto-curăță store-ul la prima rulare).
- La merge pe main: dacă stiri*/data diverg, ia versiunea de pe main pentru ele (auto-generate).
- NU rula `_build_site.py` integral (GLOS_SRC mort → regresie search-index).
- Screenshot pe pagini-gigant (masterclass, glosar) cu `./_screenshot.sh` (fix-window),
  nu `_shot.js` (îngheață Chrome la 14.000px). `_shot.js` are `CF_THEME=dark`.
