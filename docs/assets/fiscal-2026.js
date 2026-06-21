/* =============================================================================
   fiscal-2026.js — SURSA UNICĂ DE ADEVĂR pentru constantele fiscale RO 2026
   -----------------------------------------------------------------------------
   Toate uneltele Clubul Financiar (Hub Fiscal) consumă acest fișier.
   O cifră greșită aici = pierdem încrederea instant → se actualizează RELIGIOS
   anual, cu sursă oficială ANAF pentru fiecare valoare.

   Surse (fact-checked, articolele proprii ale site-ului):
     - OUG 89/2025  → deducere personală
     - Legea 239/2025 → impozit investiții/dividende 16%
     - OG 22/2025   → plafon TVA 395.000 lei (din 1 sept 2025)
     - OUG 8/2026   → bonificație 3% Declarația Unică (plată până 15 apr 2026)
   Ultima verificare: 2026-06-21. Verifică pe anaf.ro înainte de decizii mari.
   ============================================================================= */
(function (root) {
  "use strict";

  var AN = 2026;
  var SAL_MIN = 4050;              // salariu minim brut 2026 (sem. I)

  // Praguri exprimate în "salarii minime" — folosite peste tot pentru CASS/CAS.
  var SM = function (n) { return n * SAL_MIN; };
  var PRAG = {
    p6:  SM(6),    // 24.300 lei  — prag intrare CASS pasiv
    p12: SM(12),   // 48.600 lei  — prag CAS PFA + treaptă CASS
    p24: SM(24),   // 97.200 lei  — plafon maxim CASS pasiv
    p72: SM(72)    // 291.600 lei — bază maximă CASS pe venit real PFA
  };

  var F = {
    an: AN,
    actualizat: "2026-06-21",
    salariuMinim: SAL_MIN,
    SM: SM,
    praguri: PRAG,

    // ---- COTE GENERALE ----
    cote: {
      cas: 0.25,            // contribuție pensie (salariat: pe brut)
      cass: 0.10,           // contribuție sănătate
      impozitVenit: 0.10,   // impozit pe venit (salariu, chirii, PFA net)
      dividende: 0.16,      // impozit dividende (din 2026, Legea 239/2025)
      microProfit: 0.16,    // impozit pe profit SRL (sistem normal)
      micro: 0.01,          // microîntreprindere — cotă unică 1% (3% eliminată)
      tvaStandard: 0.21,    // cota standard TVA
      tvaRedusa: 0.11,      // cota redusă TVA
      // investiții pe câștig (capital gains)
      invBrokerRoLong: 0.03,  // broker RO, deținere > 1 an
      invBrokerRoShort: 0.06, // broker RO, deținere < 1 an
      invBrokerStrain: 0.16,  // broker străin, declari în DU
      chiriiDeducere: 0.20    // deducere forfetară 20% la chirii (sistem real simplificat)
    },

    // ---- MICROÎNTREPRINDERE ----
    micro: {
      plafonEUR: 100000,      // plafon cifră de afaceri (coborât de la 250.000)
      cota: 0.01,             // cotă unică 1%
      conditieSalariat: true  // minim 1 salariat cu normă întreagă
    },

    // ---- TVA ----
    tva: {
      plafonInregistrare: 395000, // lei cifră de afaceri anuală (OG 22/2025, din 1 sept 2025)
      cotaStandard: 0.21,
      cotaRedusa: 0.11
    },

    // ---- DECLARAȚIA UNICĂ ----
    declaratiaUnica: {
      termen: AN + "-05-25",          // termen standard depunere + plată
      bonificatie: 0.03,              // bonificație plată integrală
      termenBonificatie: AN + "-04-15" // OUG 8/2026
    }
  };

  /* ===========================================================================
     FUNCȚII DE CALCUL — deterministe, pure. NICIODATĂ din AI.
     =========================================================================== */

  // Deducere personală 2026 (OUG 89/2025): procent din salariul minim.
  // Bază 20% la nivelul salariului minim, +5%/persoană în întreținere (max 4),
  // scade liniar la 0 pentru brut peste salariul minim + 2.000 lei.
  F.deducerePersonala = function (brut, dependenti) {
    dependenti = Math.max(0, Math.min(4, dependenti || 0));
    if (brut > SAL_MIN + 2000) return 0;
    var procent = 0.20 + 0.05 * dependenti; // 20%..40%
    var deducereMax = procent * SAL_MIN;
    if (brut <= SAL_MIN) return deducereMax;
    // scădere liniară de la deducereMax (la SAL_MIN) la 0 (la SAL_MIN+2000)
    var factor = 1 - (brut - SAL_MIN) / 2000;
    return Math.max(0, deducereMax * factor);
  };

  // Salariu net dintr-un brut (regim standard, fără scutiri IT/construcții).
  F.salariuNet = function (brut, dependenti) {
    brut = Math.max(0, brut || 0);
    var cas = brut * F.cote.cas;
    var cass = brut * F.cote.cass;
    var ded = F.deducerePersonala(brut, dependenti);
    var baza = Math.max(0, brut - cas - cass - ded);
    var impozit = baza * F.cote.impozitVenit;
    var net = brut - cas - cass - impozit;
    return { brut: brut, cas: cas, cass: cass, deducere: ded, baza: baza, impozit: impozit, net: net,
             costAngajator: brut * 1.0225 }; // CAM 2.25% în sarcina angajatorului
  };

  // CASS pe venituri pasive (chirii, dividende, dobânzi, investiții, crypto) —
  // pe TREPTE FIXE 6/12/24 salarii minime, cumulat pe total venit pasiv anual.
  F.cassPasiv = function (venitAnual) {
    venitAnual = Math.max(0, venitAnual || 0);
    var baza;
    if (venitAnual < PRAG.p6) return { datoreaza: false, baza: 0, cass: 0, treapta: "sub 6 salarii minime" };
    if (venitAnual < PRAG.p12) baza = PRAG.p6;        // 6 sal.min
    else if (venitAnual < PRAG.p24) baza = PRAG.p12;  // 12 sal.min
    else baza = PRAG.p24;                              // 24 sal.min (plafon maxim)
    return { datoreaza: true, baza: baza, cass: baza * F.cote.cass,
             treapta: (baza / SAL_MIN) + " salarii minime" };
  };

  // CASS pe venit din activitate independentă (PFA, sistem real):
  // 10% pe venitul net REAL, dar cu bază minimă 6 sal.min (dacă > prag intrare)
  // și bază maximă 72 sal.min.
  F.cassPFA = function (venitNet) {
    venitNet = Math.max(0, venitNet || 0);
    if (venitNet < PRAG.p6) return { datoreaza: false, baza: 0, cass: 0 };
    var baza = Math.min(Math.max(venitNet, PRAG.p6), PRAG.p72);
    return { datoreaza: true, baza: baza, cass: baza * F.cote.cass };
  };

  // CAS (pensie) PFA — datorat doar dacă venitul net > 12 salarii minime.
  // 25% pe o bază aleasă: 12 sal.min (între 12–24) sau 24 sal.min (peste 24).
  F.casPFA = function (venitNet) {
    venitNet = Math.max(0, venitNet || 0);
    if (venitNet < PRAG.p12) return { datoreaza: false, baza: 0, cas: 0 };
    var baza = venitNet < PRAG.p24 ? PRAG.p12 : PRAG.p24;
    return { datoreaza: true, baza: baza, cas: baza * F.cote.cas };
  };

  // PFA — sistem real: venit net = încasări - cheltuieli deductibile.
  // Returnează impozit + CAS + CASS + net în mână.
  F.pfaReal = function (incasari, cheltuieli) {
    incasari = Math.max(0, incasari || 0);
    cheltuieli = Math.max(0, cheltuieli || 0);
    var venitNet = Math.max(0, incasari - cheltuieli);
    var cas = F.casPFA(venitNet);
    var cass = F.cassPFA(venitNet);
    // baza de impozit = venit net - CAS - CASS (contribuțiile sunt deductibile)
    var bazaImpozit = Math.max(0, venitNet - cas.cas - cass.cass);
    var impozit = bazaImpozit * F.cote.impozitVenit;
    var netInMana = venitNet - cas.cas - cass.cass - impozit;
    return { tip: "PFA real", venitNet: venitNet, cas: cas, cass: cass,
             impozit: impozit, totalTaxe: cas.cas + cass.cass + impozit, netInMana: netInMana };
  };

  // SRL micro (1% pe cifra de afaceri) cu scoatere de dividende.
  // dividendePct = ce procent din profitul net distribui ca dividend.
  F.srlMicro = function (cifraAfaceri, cheltuieli, dividendePct) {
    cifraAfaceri = Math.max(0, cifraAfaceri || 0);
    cheltuieli = Math.max(0, cheltuieli || 0);
    dividendePct = dividendePct == null ? 1 : Math.max(0, Math.min(1, dividendePct));
    var impozitFirma = cifraAfaceri * F.cote.micro; // 1% pe venituri
    var profit = Math.max(0, cifraAfaceri - cheltuieli - impozitFirma);
    var brutDividend = profit * dividendePct;
    var impozitDividend = brutDividend * F.cote.dividende; // 16%
    // CASS pe dividende (venit pasiv) — pe trepte, dacă depășește pragul
    var cass = F.cassPasiv(brutDividend);
    var netInMana = brutDividend - impozitDividend - cass.cass;
    var depasestePlafonMicro = cifraAfaceri > F.micro.plafonEUR * F.cursEUR();
    return { tip: "SRL micro 1%", impozitFirma: impozitFirma, profit: profit,
             impozitDividend: impozitDividend, cassDividend: cass.cass,
             totalTaxe: impozitFirma + impozitDividend + cass.cass, netInMana: netInMana,
             depasestePlafonMicro: depasestePlafonMicro };
  };

  // Impozit pe chirii (sistem real simplificat): deducere forfetară 20%,
  // impozit 10% pe net + CASS pe trepte dacă depășește pragul.
  F.impozitChirii = function (chirieAnualaBruta) {
    chirieAnualaBruta = Math.max(0, chirieAnualaBruta || 0);
    var venitNet = chirieAnualaBruta * (1 - F.cote.chiriiDeducere);
    var impozit = venitNet * F.cote.impozitVenit;
    var cass = F.cassPasiv(venitNet);
    return { brut: chirieAnualaBruta, venitNet: venitNet, impozit: impozit,
             cass: cass.cass, totalTaxe: impozit + cass.cass,
             netInMana: chirieAnualaBruta - impozit - cass.cass };
  };

  // Impozit pe investiții (capital gains) — vezi cotele de mai sus.
  F.impozitInvestitii = function (suma, opts) {
    suma = Math.max(0, suma || 0);
    opts = opts || {};
    var rate;
    if (opts.tip === "dividende") rate = F.cote.dividende;
    else if (opts.broker === "strain") rate = F.cote.invBrokerStrain;
    else if (opts.detinere === "long") rate = F.cote.invBrokerRoLong;
    else rate = F.cote.invBrokerRoShort;
    return { rata: rate, impozit: suma * rate, net: suma * (1 - rate) };
  };

  // Curs EUR/RON — fallback static (se poate suprascrie din feed BNR live).
  F._cursEUR = 5.07;
  F.cursEUR = function () { return root.CF_EUR_RON || F._cursEUR; };

  // Următorul termen fiscal (Declarația Unică) ca obiect Date.
  F.urmatorulTermenDU = function () {
    return new Date(F.declaratiaUnica.termen + "T23:59:59");
  };

  root.CF_FISCAL = F;
})(typeof window !== "undefined" ? window : this);
