# REEL — „Salariul care se despică singur" (Regula 50/30/20)

**Durată totală: 21,5s · 1080×1920 · funcție frame(t) deterministă**

---

## 1. Hook-ul exact (0,5–2,3s)

Pe ecran, două rânduri:

> **5.843 lei.**
> **Privește cum se despică singuri.**

„5.843" apare uriaș (font ~180px, auriu #E8C268 pe navy #0a1424), cu efect de contor rapid care „aterizează" pe cifră în ~400ms. Rândul doi intră cu fade+slide de jos. Pattern-interrupt: o sumă exactă, nu rotundă — creierul o recunoaște ca „reală" și se oprește să afle a cui e.

---

## 2. Scenariul scenă-cu-scenă (timing în ms)

| Interval (ms) | Scenă | Text EXACT pe ecran |
|---|---|---|
| **0–500** | Brand fade-in: logo mic sus-centru, fundal navy cu vignetă radială subtilă | *(doar logo)* |
| **500–2300** | HOOK (vezi §1) | „5.843 lei." / „Privește cum se despică singuri." |
| **2300–3200** | Context într-o singură linie, mică, sub cifră | „salariul mediu net în România (INS, apr. 2026)" |
| **3200–4800** | LINGOUL: un monolit auriu 3D (blocul de bani) coboară în centru și se așază cu un impact ușor; o linie de scanare verticală îl parcurge | „Regula 50/30/20" (apare pe lingou, gravat) |
| **4800–7500** | DESPICAREA (semnătura vizuală, §4): două tăieturi de lumină cad pe lingou; el se despică în 3 plăci care alunecă în poziție de coloane, cu înălțimi proporționale 50/30/20 | deasupra coloanelor, secvențial: „50%" „30%" „20%" · sub ele: „2.921 lei" „1.753 lei" „1.169 lei" |
| **7500–10.400** | Camera „împinge" spre coloana 1 (auriu plin). Sub ea se derulează 4 rânduri, câte unul la ~600ms | Titlu: „NEVOI — 2.921 lei" · rânduri: „chirie / rată" „facturi" „mâncare" „transport" |
| **10.400–12.900** | Coloana 2 (auriu deschis, ton secundar). 3 rânduri | Titlu: „DORINȚE — 1.753 lei" · rânduri: „ieșiri" „haine" „abonamente" |
| **12.900–16.500** | Coloana 3 devine VERDE (#5cf0aa) și CREȘTE: din vârful ei urcă o curbă-timeline pe 10 ani; contor mare rulează de la 0 la 213.900 | Titlu: „VIITOR — 1.169 lei/lună" · pe timeline: „10 ani · 8%/an" · contorul: „213.900 lei" · dedesubt mic: „tu ai pus doar 140.280" |
| **16.500–18.800** | CLIMAX: totul se întunecă ușor, rămâne coloana verde luminată; fraza-revelație pe două rânduri, centrat | „Primii 20% nu se cheltuie." / „Se plătesc ție." |
| **18.800–21.500** | CTA: logo mare + domeniu + disclaimer mic jos | „clubulfinanciar.ro" / „Educație financiară, pe românește." · jos, mic: „Exemplu educativ, randament ipotetic 8%/an. Nu este sfat de investiții." |

Toate textele: română corectă cu diacritice, max 4–5 cuvinte pe rând, corp ≥54px pentru lizibilitate mobil.

---

## 3. Cifrele — calculate și verificate

**Salariul mediu net RO:** 5.843 lei în aprilie 2026, conform INS (ultima lună publicată la data producției) — surse: [Mediafax](https://www.mediafax.ro/economic/salariul-mediu-net-a-scazut-in-aprilie-2026-cat-au-castigat-in-medie-romanii-23753986), [Capital](https://www.capital.ro/salariul-mediu-in-romania-scade-usor-in-aprilie-2026-brut-9-740-lei-net-5-843-lei.html), [Financiarul](https://financiarul.ro/economie/salariul-mediu-net-a-scazut-la-5-843-de-lei-in-aprilie-2026-ce-arata-reculu/), [INS comunicate](https://insse.ro/cms/ro/tags/comunicat-castig-salarial).

**Despicarea 50/30/20 (suma exactă, se închide la leu):**
- 50% nevoi: 5.843 × 0,50 = 2.921,50 → **2.921 lei**
- 30% dorințe: 5.843 × 0,30 = 1.752,90 → **1.753 lei**
- 20% viitor: 5.843 × 0,20 = 1.168,60 → **1.169 lei**
- Verificare: 2.921 + 1.753 + 1.169 = **5.843 lei** ✓

**Calculul „de ce 20% îți schimbă viața în 10 ani":**
1.169 lei/lună investiți, 8%/an cu capitalizare lunară, 120 de luni (anuitate ordinară):
- r = 0,08/12 = 0,006667; factor FV = ((1+r)¹²⁰ − 1)/r = (2,2196 − 1)/0,006667 ≈ **182,95**
- FV = 1.169 × 182,95 ≈ **213.870 lei** → afișat **213.900 lei** (rotunjire la sută)
- Contribuții proprii: 1.169 × 120 = **140.280 lei**
- Câștig din randament: ≈ **73.600 lei** — banii au lucrat pentru tine cât ~12,6 salarii medii nete

Disclaimerul de 8%/an (randament ipotetic, istoric plauzibil pentru portofolii diversificate de acțiuni, negarantat) apare obligatoriu în cadrul CTA.

---

## 4. Semnătura vizuală: „Despicarea lingoului"

**NU pie chart.** Elementul central e un **lingou auriu 3D** (un bloc masiv cu fațete, gradient #E8C268 → #b8923e, muchii cu highlight specular, perspectivă rotateX ~40° ca la reel-urile anterioare de brand). El coboară, aterizează cu un micro-shake al camerei, apoi:

1. **Două lame de lumină verticale** (linii albe incandescente cu glow auriu) cad pe el la pozițiile 50% și 80% din lățime — ca o tăietură cu laser într-un lingou de aur. La fiecare tăietură: flash de 80ms + particule-scântei.
2. Cele trei plăci rezultate **alunecă lateral și cad în poziție de coloane**, fiecare cu un „thud" propriu, iar înălțimile lor se animă (ease-out elastic) până devin proporționale cu 50/30/20 — banii se re-aranjează fizic, nu se desenează un grafic.
3. **Evoluția pe parcurs:** coloanele 1 și 2 rămân aur (plin / deschis), iar coloana 3 face tranziția aur→verde (#5cf0aa) exact în momentul în care devine „VIITOR" — verdele e culoarea de creștere a brandului. Din vârful ei crește curba de 10 ani, ca și cum coloana „încolțește".
4. La climax, coloanele 1–2 se sting la ~25% opacitate; rămâne doar verdele aprins — memoria vizuală a reel-ului e „bucata care rămâne aprinsă".

Memorabil pentru că banii sunt un obiect fizic tăiat în 3, nu o diagramă: gestul de „despicare" e semnătura.

---

## 5. Familia sonoră (sinteză ffmpeg)

| Moment (ms) | Sunet |
|---|---|
| 0–500 | pad cald jos (sine + puțin detune, ~110Hz), fade-in |
| 500–900 | tick-uri rapide de contor (impulsuri scurte, filtrate highpass) în timp ce cifra 5.843 „aterizează", finalizate cu un „thock" sec |
| 3200–4700 | riser sub-bass (sweep 40→90Hz) pe coborârea lingoului; **boom** surd la aterizare (4.700ms) |
| 5.100 și 5.900 | **două „cleave"-uri metalice** (zgomot alb foarte scurt + rezonanță metalică ~2kHz cu decay 300ms) — tăieturile de laser |
| 6.300 / 6.700 / 7.100 | trei „thud"-uri în trepte descrescătoare de pitch (coloanele aterizează: mare→mic) |
| 7.500–12.900 | tick-uri discrete la fiecare rând de text care intră |
| 12.900–16.300 | **crescendo**: arpegiu ascendent subtil + tick-uri de contor tot mai dese pe rularea spre 213.900; sweep-filter care se deschide |
| 16.500 | **shimmer** (acord înalt cu reverb lung, fade 1,5s) + tăcere sub el — spațiu pentru fraza-revelație |
| 18.800 | boom moale de brand + pad-ul revine scurt pe CTA, fade-out la 21.300 |

---

## 6. Subtitlul-revelație și CTA

**Revelația (16.500ms):**
> **„Primii 20% nu se cheltuie. Se plătesc ție."**

Re-încadrarea: economisirea nu e o rămășiță de la finalul lunii, e prima factură — iar factura ești tu. (Diferențiator față de reel-ul „pay yourself first" existent: acolo era doar principiul; aici e **regula completă**, cu toate cele 3 găleți și sume exacte în lei pe salariul mediu — reel de sistem, nu de mindset.)

**CTA (18.800ms):** logo + „clubulfinanciar.ro" + „Educație financiară, pe românește." + disclaimerul mic.

---

## 7. De ce ar fi distribuit

Emoția dominantă: **„asta e despre salariul MEU"** — suma exactă 5.843 lei din hook face reel-ul personal instant pentru milioane de oameni, iar despicarea în sume concrete (nu procente abstracte) îl face imediat aplicabil: fiecare privitor își recalculează mental propriile trei coloane în timp ce se uită. Al doilea strat: **șocul lui 213.900 vs 140.280** („73.600 lei apar din nimic?!") + vinovăție constructivă („eu nu am nicio coloană verde"). E genul de reel trimis partenerului sau copilului care „nu știe unde se duc banii" — pentru că oferă o regulă completă, cu cifre gata calculate, în 21 de secunde.

Sources: [Mediafax — salariul mediu net aprilie 2026](https://www.mediafax.ro/economic/salariul-mediu-net-a-scazut-in-aprilie-2026-cat-au-castigat-in-medie-romanii-23753986) · [Capital — brut 9.740 / net 5.843 lei](https://www.capital.ro/salariul-mediu-in-romania-scade-usor-in-aprilie-2026-brut-9-740-lei-net-5-843-lei.html) · [Financiarul — 5.843 lei apr. 2026](https://financiarul.ro/economie/salariul-mediu-net-a-scazut-la-5-843-de-lei-in-aprilie-2026-ce-arata-reculu/) · [INS — comunicate câștig salarial](https://insse.ro/cms/ro/tags/comunicat-castig-salarial)