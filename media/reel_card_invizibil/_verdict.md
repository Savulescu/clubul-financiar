# (a) Scoruri per concept

## Concept 1 — „ore-de-viata"
| Criteriu | Scor | Justificare |
|---|---|---|
| Hook 2s | 8 | Paradoxul „NU costă 6.000 lei" neagă o evidență și forțează așteptarea rezolvării — dar telefonul scump e un hook văzut des în nișă. |
| Claritate fără sunet | 8 | Ritualul flip preț→timp, repetat de 4 ori cu miză crescândă, e perfect legibil mut; grila de 22 cadrane se citește instant. |
| Emoție de share | 8 | Livrează o unealtă mentală („preț ÷ 35") + dezbatere telefon vs. vacanțe în comentarii — dublu motor. |
| Fezabilitate frame(t) | 7 | Conic-gradient animat, flip 3D, cascadă 22 cadrane, motion blur pe ac — tot fezabil, dar e de departe cel mai complex de implementat corect. |
| Originalitate | 6 | „Prețul în ore de muncă" e un trop cunoscut global (Your Money or Your Life, nenumărate reels EN); Cadranul de Aur îl salvează parțial. |
| Corectitudine cifre | 10 | Toate calculele verificate: 5.843/168=34,78; 31 min, 1h18, 1,98 zile, 21,6→22 zile, 10,8→11 zile — impecabil, cu surse. |

## Concept 2 — „salariul-se-despica"
| Criteriu | Scor | Justificare |
|---|---|---|
| Hook 2s | 7 | Suma exactă 5.843 e un pattern-interrupt bun („e salariul MEU"), dar „privește cum se despică" e o invitație pasivă, nu o tensiune. |
| Claritate fără sunet | 8 | Lingou → 3 coloane proporționale cu sume în lei = citibil mut; scroll-ul de rânduri sub coloane e puțin dens. |
| Emoție de share | 6 | Util și personal, dar 50/30/20 miroase a temă pentru acasă — impulsul e „salvez", nu „trimit". |
| Fezabilitate frame(t) | 7 | Lingou 3D cu fațete, lame de lumină, scântei, ease elastic — fezabil dar pretențios ca să nu arate ieftin. |
| Originalitate | 4 | 50/30/20 e cel mai saturat subiect din finance short-form, RO și global; despicarea lingoului e singura noutate. |
| Corectitudine cifre | 10 | Se închide la leu (2.921+1.753+1.169=5.843), factor FV 182,95 corect, 213.870→213.900 rotunjit onest. |

## Concept 3 — „cardul-invizibil"
| Criteriu | Scor | Justificare |
|---|---|---|
| Hook 2s | 9 | „CREIERUL TĂU NU SIMTE CARDUL" e neurologic, personal și nou pentru publicul RO — plus flash-ul TAP la 300ms lovește înainte de citit. |
| Claritate fără sunet | 7 | Split-ul cash vs. tap e excelent mut; scena „studiul MIT" e un card de text prea dens — punctul slab de rezolvat. |
| Emoție de share | 9 | Recunoaștere vinovată a unui gest făcut de 10×/zi + fix aplicabil în 10 secunde: share-ul devine grijă, nu predică. Cel mai puternic motor din cele trei. |
| Fezabilitate frame(t) | 9 | Inele concentrice, contoare, text, ritm determinist de tap-uri — cel mai simplu și robust de construit din cod. |
| Originalitate | 8 | „Pain of paying" aproape absent în nișa finance RO; gestul contactless ca metronom al pierderii e o semnătură proprie. |
| Corectitudine cifre | 7 | Prelec & Simester real și matematica internă corectă (260, 31.200, 47.566), dar „12–18%" vine dintr-o sursă slabă (blog fintech) și „2.000 lei flexibili" e o ipoteză — trebuie etichetate explicit ca estimare. |

**Totaluri: C1 = 47 · C2 = 42 · C3 = 49**

# (b) Câștigătorul: „Cardul invizibil"

Argumentul decisiv: e singurul concept al cărui protagonist e un gest pe care privitorul îl face fizic în fiecare zi — recunoașterea de sine e instantanee și viscerală, nu intelectuală. Celelalte două cer să te proiectezi într-un scenariu (îmi cumpăr telefon / îmi împart salariul); acesta te prinde deja în flagrant. În plus, e singurul cu un fix acționabil pe loc (notificarea), ceea ce transformă share-ul în cadou, și e cel mai fezabil tehnic — inele + contoare + ritm sunt teritoriul natural al unui frame(t) determinist, zero risc de a arăta ieftin.

# (c) Grefe care îl fac mai bun

1. **Traducerea în ore de muncă (din C1):** după „~260 lei în fiecare lună", adaugă lovitura „= aproape o ZI de muncă. Gratis." (260 ÷ 34,78 lei/oră = 7,5 ore). Leagă pierderea abstractă de corpul privitorului — cea mai bună idee din C1, altoită în 1,5 secunde.
2. **Studiul devine bare, nu text (limbajul vizual din C2):** înlocuiește cardul de text MIT cu două coloane animate — cash (auriu, 100) vs. card (verde, crește la 200) — cu o singură linie de text. Repară exact punctul slab de la „claritate fără sunet".
3. **Split-ul 31.200 + 16.300 (precizia „tu ai pus doar…" din C2):** la cifra de 47.500, arată vizual că 31.200 e pierderea directă și 16.300 e dobânda pierdută — coloană aurie + segment verde deasupra. Șocul „banii ar fi făcut bani" e gratis.
4. **„Rămâne aprins" (climaxul din C2):** la revelație, totul se stinge la 20% opacitate, iar ultimul inel de tap înghețat își schimbă conturul din verde în auriu — vizual: banii recuperați. Memoria reel-ului = un singur element luminos.
5. **Momeală de comentarii (din capul meu):** sub CTA, mic: „Tu ai notificările pornite?" — întrebare binară, cost zero, hrănește algoritmul cu răspunsuri da/nu.

# (d) SCENARIUL FINAL — „Creierul tău nu simte cardul" (consolidat, gata de implementat)

**21.500 ms · 1080×1920 · frame(t) determinist · navy #0a1424 / auriu #E8C268 / verde #5cf0aa · toate textele cu diacritice, corp ≥54px, max 5 cuvinte/rând**

## Timeline scenă cu scenă

| Interval (ms) | Scenă și mișcare | Text EXACT pe ecran |
|---|---|---|
| **0–300** | Fundal navy fade-in, vignetă radială subtilă. | — |
| **300–500** | **TAP #1**: inel verde #5cf0aa cu glow explodează din centru (scale 0→1,6, opacity 1→0, 400ms) — flash-ul lovește ÎNAINTE de orice text. | — |
| **500–2.300** | **HOOK.** Două rânduri mari centrate, intră cu pop (1,12→1,0); tremur subtil 2px pe „NU SIMTE" (sin 12Hz). La 1.400ms, subtitlu mic fade-in. La 2.100ms totul alunecă în sus și iese. | „CREIERUL TĂU" / „NU SIMTE CARDUL." + mic: „Și te costă mai mult decât crezi." |
| **2.300–6.500** | **SPLIT-SCREEN.** Linie verticală centrală. Stânga (auriu): 4 bancnote stilizate (dreptunghiuri aurii cu bandă) numărate una câte una la 2.700/3.600/4.500/5.400ms, fiecare cu micro-pauză și puls roșiatic (#ff5c5c la 15% opacity, 200ms) pe jumătatea stângă — durerea plății, vizibilă. Dreapta (verde): UN singur tap la 3.000ms, inel + fulger, apoi nimic — contrast prin absență. | Stânga sus: „CASH: creierul SIMTE fiecare leu" / Dreapta sus: „TAP: creierul nu simte NIMIC" |
| **6.500–9.500** | **STUDIUL — ca bare, nu text.** Split-ul se comprimă în fundal (scale 0,85, blur ușor). Două coloane cresc din bazlinie (rotateX ~30° pe plan, consistent cu template-ul brand): cash auriu până la 100 (6.700–7.400ms, ease-out), card verde până la 200 (7.400–8.600ms, depășește vizibil, cu overshoot elastic). O singură linie de text deasupra + sursa mică jos. | Sus: „Cu cardul, oamenii plătesc / până la de 2× mai mult" · sub coloane: „cash" / „card" · jos, mic: „Prelec & Simester, MIT · la cumpărături uzuale: +12–18% (estimare din studii)" |
| **9.500–13.400** | **APLICAREA RO — semnătura vizuală.** Coloanele ies; contor auriu central mare (rotateX ~30°) urcă 0→260, sincron cu tap-uri verzi care accelerează: intervale 800→550→380→260→180ms, fiecare inel cu ~8% mai mare, glow crescător. Text sus intră la 9.700ms; lovitura la 12.000ms sub contor. | Sus, mic: „Cheltuieli flexibile pe card: ~2.000 lei/lună (din salariul mediu net de 5.843 lei)" · contor: „260 lei" · la 12.000ms: „Partea pe care cash / NU ai fi dat-o. În fiecare lună." |
| **13.400–14.900** | **GREFA C1 — traducerea în muncă.** Contorul „260 lei" face flip 180° pe axa Y (gestul preț→timp) și pe verso scrie timpul; un mini-cadran auriu mătură 7,5/8 dintr-o tură lângă text. | „= aproape o ZI de muncă." / mic: „7 ore și jumătate. Gratis." |
| **14.900–17.500** | **10 ANI.** Numărătoare mare accelerată cu tick-uri: 3.120 → 31.200 (aterizează la 15.700ms), apoi coloana aurie „31.200" primește deasupra un segment VERDE care crește (+16.300), iar cifra sare la **47.500** cu boom la 16.600ms. | „10 ani = 31.200 lei" → coloană: segment auriu „31.200 — banii tăi" + segment verde „+16.300 — dobânda pierdută (8%/an)" → mare: „= 47.500 lei" |
| **17.500–19.800** | **REVELAȚIA + TRUCUL.** Tap-urile SE OPRESC brusc; tot ecranul se stinge la 20% opacitate; ultimul inel îngheață în centru și conturul lui face tranziția verde→auriu în 600ms (banii recuperați) — rămâne singurul element aprins, în spatele textului. La 18.600ms intră trucul, cu un „ding" de notificare. | „Nu cardul e problema. / Invizibilitatea e." · apoi: „Trucul: pornește notificarea / la FIECARE plată." / mic: „Durerea se întoarce. Cheltuiala scade." |
| **19.800–21.500** | **CTA.** Inelul auriu înghețat alunecă și devine „o"-ul din logo (semnătura se închide în brand, ca la C1). Logo + domeniu + momeala de comentarii + disclaimer. | „clubulfinanciar.ro" / „Educație financiară, pe românește." · „Tu ai notificările pornite?" · mic: „Conținut educativ. Estimări pe studii; randamentul de 8%/an e o ipoteză. Nu este sfat de investiții." |

## Cifrele (verificate, de hard-codat în frame(t))

- Salariu mediu net RO: **5.843 lei** (INS, apr. 2026) → 5.843 ÷ 168h = **34,78 lei/oră**.
- Ipoteză etichetată pe ecran: cheltuieli flexibile pe card ≈ **2.000 lei/lună** (~34% din net, conservator).
- Supra-cheltuire card vs. cash: 15% (mijlocul intervalului 12–18%) aplicat corect: 2.000 ÷ 1,15 = 1.739 → **260 lei/lună** (interval onest 214–305).
- În muncă: 260 ÷ 34,78 = **7,48 ore ≈ „aproape o zi de muncă"**.
- 10 ani simplu: 260 × 120 = **31.200 lei**.
- 10 ani investiți, 8%/an capitalizare lunară: factor FV = ((1+0,08/12)^120 − 1)/(0,08/12) = **182,95** → 260 × 182,95 = 47.566 ≈ **47.500 lei**; dobânda = 47.500 − 31.200 ≈ **16.300 lei**.
- Studii: Prelec & Simester 2001 (Marketing Letters) — oferte cu card ~duble vs. cash („până la de 2×", formulare corectă); 12–18% etichetat pe ecran „estimare din studii".

## Semnătura vizuală

**„TAP-ul care crește"** — inelul de undă contactless (cerc verde cu glow, stroke 6px, scale+fade 400ms) folosit în 4 faze: (1) flash solitar pre-hook; (2) tap politicos unic în split-screen vs. bancnote numărate cu puls roșiatic; (3) puls cardiac accelerat (800→180ms, +8% rază per inel) ca metronom al pierderii, sincron cu contorul; (4) oprire bruscă + inel înghețat care virează verde→auriu și devine „o"-ul logo-ului. Grefat din C1: flip-ul 180° pe Y care traduce „260 lei" în timp de muncă. Paletă strictă: navy fundal, auriu = bani/contor/cash, verde = tap/card/creștere; rotateX ~30° pe planurile de contor/coloane pentru consistență cu template-ul reel existent.

## Familia sonoră (sinteză ffmpeg)

| ms | Sunet | Rețetă |
|---|---|---|
| 300 | tap-blip #1 | sine 1.200Hz, 60ms, attack instant, ușor pitch-down |
| 500–2.300 | sub-drone | sinus 55Hz, volum mic, fade-in |
| 2.700–5.400 | cash-tick ×4 | noise burst band-pass 2–4kHz (foșnet) + thud 90Hz la +40ms, la 900ms distanță |
| 3.000 | tap-blip unic dreapta | sine 1.200Hz, curat |
| 6.500 | whoosh | noise sweep 400→4.000Hz, 300ms |
| 6.700–8.600 | creștere coloane | două note susținute: 220Hz (cash), apoi 330Hz (card) care urcă peste, + tick la fiecare aterizare |
| 9.500–13.400 | tap-heartbeat | blip-uri 1.200Hz la intervale 800→180ms, pitch +3 semitonuri gradual; riser sinus 200→800Hz dedesubt |
| 13.400 | flip | tic dublu cu gap 30ms (din C1) |
| 14.900–16.500 | counter-roll | tick-uri 2.400Hz la 30ms + riser continuu |
| 16.600 | boom | kick sintetic 50Hz, decay 400ms (aterizarea pe 47.500) |
| 17.500 | BOOM + tăcere | kick 50Hz + cut total 300ms — tap-urile mor |
| 18.600 | ding notificare | sinusuri 1.568+2.093Hz (Sol–Do), 200ms |
| 19.800–21.500 | shimmer CTA | cluster 4–8kHz tremolo lent + pad 220Hz, fade-out; ultimul blip tăiat sec pe cadrul final |