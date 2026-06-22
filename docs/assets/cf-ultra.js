/* =============================================================================
   cf-ultra.js — CREIERUL PARTAJAT al suitei ULTRA ("Biroul tău financiar privat").
   -----------------------------------------------------------------------------
   Un singur Profil Financiar al utilizatorului alimentează TOATE uneltele Ultra:
   Cockpit, Concierge AI, Simulator "Și dacă...", Optimizator de structură,
   Calendar fiscal, Raportul "Drumul spre Libertate", Scor de sănătate.

   Stocare HIBRIDĂ: scrie întotdeauna în localStorage (privat, instant, offline)
   și, dacă userul e logat + a activat sync, oglindește în Supabase `ultra_profile`
   (RLS pe user). Niciun calcul nu vine din AI — totul determinist, pe fiscal-2026.js.

   Depinde de: cf-tool.js (CF.*), fiscal-2026.js (CF_FISCAL). Toate funcțiile sub CF.U.
   ============================================================================= */
(function (root) {
  "use strict";

  var CF = root.CF = root.CF || {};
  var U = {};
  var F = function () { return root.CF_FISCAL; };

  /* ===========================================================================
     1. PROFILUL FINANCIAR — schemă + store hibrid
     =========================================================================== */
  U.SCHEMA_V = 1;
  U.LS_KEY = "cf-ultra-profil";

  // Profil gol cu valori implicite — sursa unică de adevăr pentru forme.
  U.gol = function () {
    return {
      v: U.SCHEMA_V,
      updated: null,
      sync: false,                 // userul a cerut sincronizare în cloud?
      // --- Persoană ---
      nume: "",
      varsta: 35,
      dependenti: 0,               // copii / persoane în întreținere
      oras: "",
      stareCivila: "necasatorit",  // necasatorit | casatorit
      // --- Structură & venituri ---
      structura: "salariat",       // salariat | pfa_real | pfa_norma | srl_micro | srl_real | mixt
      tvaPlatitor: false,
      venituri: {
        salariuNet: 0,             // lei/lună, în mână
        pfaIncasari: 0,            // lei/an (brut)
        pfaCheltuieli: 0,          // lei/an (deductibile)
        srlCifraAfaceri: 0,        // lei/an
        srlCheltuieli: 0,          // lei/an
        srlDividendePct: 100,      // % din profit scos ca dividend
        chiriiLunar: 0,            // lei/lună (brut)
        dividendeAnual: 0,         // lei/an (din alte firme / portofoliu)
        alteLunar: 0               // lei/lună (net)
      },
      // --- Cheltuieli lunare (lei) ---
      cheltuieli: {
        locuinta: 0, mancare: 0, transport: 0, utilitati: 0,
        rate: 0, abonamente: 0, copii: 0, sanatate: 0, distractie: 0, alte: 0
      },
      // --- Datorii (listă) ---
      datorii: [],                 // { nume, sold, dobanda(%), rataLunara }
      // --- Avere (active, lei) ---
      active: {
        cash: 0,                   // conturi curente + economii lichide
        depozite: 0,               // depozite bancare
        investitii: 0,             // acțiuni / ETF / fonduri
        crypto: 0,
        titluriStat: 0,            // Fidelis / Tezaur
        pensiePilon3: 0,
        imobiliareInvestitii: 0,   // proprietăți care produc venit / de vânzare
        locuintaProprie: 0,        // locuința în care stai (NU intră în FIRE)
        auto: 0,
        alte: 0
      },
      // --- Obiective ---
      obiective: {
        fondUrgentaLuni: 6,        // câte luni de cheltuieli vrei în fondul de urgență
        varstaLibertate: 55,       // vârsta la care vrei independență financiară
        randamentReal: 5,          // % randament real anual estimat al investițiilor
        custom: []                 // { nume, suma, termen(YYYY-MM) }
      },
      toleranteRisc: "medie"       // mica | medie | mare
    };
  };

  // Migrează un profil vechi la schema curentă (umple câmpuri lipsă).
  U.normalizeaza = function (p) {
    var g = U.gol();
    if (!p || typeof p !== "object") return g;
    function deep(dst, src) {
      Object.keys(dst).forEach(function (k) {
        if (src[k] == null) return;
        if (dst[k] && typeof dst[k] === "object" && !Array.isArray(dst[k]))
          deep(dst[k], src[k]);
        else dst[k] = src[k];
      });
    }
    deep(g, p);
    if (Array.isArray(p.datorii)) g.datorii = p.datorii;
    if (p.obiective && Array.isArray(p.obiective.custom)) g.obiective.custom = p.obiective.custom;
    g.v = U.SCHEMA_V;
    return g;
  };

  U._cache = null;
  // Citește profilul (localStorage). Sincron — pentru randare instant.
  U.getProfil = function () {
    if (U._cache) return U._cache;
    var raw = null;
    try { raw = JSON.parse(localStorage.getItem(U.LS_KEY) || "null"); } catch (e) {}
    U._cache = U.normalizeaza(raw);
    return U._cache;
  };

  // Salvează profilul: localStorage întotdeauna + Supabase dacă sync activ & logat.
  U.salveaza = function (p) {
    p = U.normalizeaza(p);
    p.updated = new Date().toISOString();
    U._cache = p;
    try { localStorage.setItem(U.LS_KEY, JSON.stringify(p)); } catch (e) {}
    var sb = root.cfSupabase || root.__cfSB, uid = root.cfUserId;
    if (p.sync && sb && uid) {
      try {
        sb.from("ultra_profile").upsert(
          { user_id: uid, data: p, updated_at: p.updated },
          { onConflict: "user_id" }
        ).then(function () {}, function () {});
      } catch (e) {}
    }
    try { root.dispatchEvent(new CustomEvent("cf-profil", { detail: p })); } catch (e) {}
    return p;
  };

  // Trage profilul din cloud (cross-device). Întoarce Promise<profil>.
  U.syncCloud = function () {
    var sb = root.cfSupabase || root.__cfSB, uid = root.cfUserId;
    if (!sb || !uid) return Promise.resolve(U.getProfil());
    return sb.from("ultra_profile").select("data").eq("user_id", uid).maybeSingle()
      .then(function (res) {
        if (res && res.data && res.data.data) {
          var cloud = U.normalizeaza(res.data.data);
          var local = U.getProfil();
          // Cea mai recentă versiune câștigă.
          var win = (cloud.updated || "") >= (local.updated || "") ? cloud : local;
          U._cache = win;
          try { localStorage.setItem(U.LS_KEY, JSON.stringify(win)); } catch (e) {}
          return win;
        }
        return U.getProfil();
      }, function () { return U.getProfil(); });
  };

  // Profilul are date suficiente ca uneltele să aibă sens?
  U.areDate = function (p) {
    p = p || U.getProfil();
    return U.venitNetLunar(p) > 0 || U.activeTotal(p) > 0 || (p.cheltuieli && U.cheltuieliLunar(p) > 0);
  };

  /* ===========================================================================
     2. CALCUL — venituri, taxe, cash-flow (determinist, pe CF_FISCAL)
     =========================================================================== */

  // Venit net lunar din TOATE sursele, după taxe.
  U.venitNetLunar = function (p) {
    p = p || U.getProfil();
    var f = F(), v = p.venituri, total = 0;
    total += +v.salariuNet || 0;
    total += (+v.alteLunar || 0);
    // chirii: net pe lună (deducere 20% + impozit 10% + CASS pe trepte estimat anual)
    var chiriiAn = (+v.chiriiLunar || 0) * 12;
    if (chiriiAn > 0 && f) total += f.impozitChirii(chiriiAn).netInMana / 12;
    else total += (+v.chiriiLunar || 0);
    // venit din structura principală (PFA / SRL) — net anual / 12
    var s = U.venitStructuraAnual(p);
    total += s.netInMana / 12;
    // dividende din alte surse (portofoliu) — 16% + CASS trepte
    var divAn = +v.dividendeAnual || 0;
    if (divAn > 0 && f) {
      var imp = divAn * f.cote.dividende, cass = f.cassPasiv(divAn).cass;
      total += (divAn - imp - cass) / 12;
    }
    return total;
  };

  // Venitul net ANUAL din structura principală (PFA real / SRL micro / SRL real).
  // Salariații nu au "structură de firmă" — întoarce 0 aici (salariul intră separat).
  U.venitStructuraAnual = function (p) {
    p = p || U.getProfil();
    var f = F(), v = p.venituri;
    if (!f) return { tip: p.structura, netInMana: 0, totalTaxe: 0, baza: 0 };
    if (p.structura === "pfa_real" || p.structura === "pfa_norma") {
      var r = f.pfaReal(+v.pfaIncasari || 0, +v.pfaCheltuieli || 0);
      return { tip: "PFA", netInMana: r.netInMana, totalTaxe: r.totalTaxe, baza: r.venitNet };
    }
    if (p.structura === "srl_micro") {
      var m = f.srlMicro(+v.srlCifraAfaceri || 0, +v.srlCheltuieli || 0, (+v.srlDividendePct || 100) / 100);
      return { tip: "SRL micro", netInMana: m.netInMana, totalTaxe: m.totalTaxe, baza: m.profit, extra: m };
    }
    if (p.structura === "srl_real") {
      var ca = +v.srlCifraAfaceri || 0, ch = +v.srlCheltuieli || 0;
      var profit = Math.max(0, ca - ch);
      var impProfit = profit * f.cote.microProfit; // 16% impozit pe profit
      var profitNet = profit - impProfit;
      var brutDiv = profitNet * ((+v.srlDividendePct || 100) / 100);
      var impDiv = brutDiv * f.cote.dividende;
      var cass = f.cassPasiv(brutDiv).cass;
      var net = brutDiv - impDiv - cass;
      return { tip: "SRL real", netInMana: net, totalTaxe: impProfit + impDiv + cass, baza: profit };
    }
    return { tip: p.structura, netInMana: 0, totalTaxe: 0, baza: 0 };
  };

  U.cheltuieliLunar = function (p) {
    p = p || U.getProfil();
    var c = p.cheltuieli || {}, t = 0;
    Object.keys(c).forEach(function (k) { t += +c[k] || 0; });
    return t;
  };

  U.cashFlow = function (p) {
    p = p || U.getProfil();
    var venit = U.venitNetLunar(p);
    var chelt = U.cheltuieliLunar(p);
    var rateDatorii = (p.datorii || []).reduce(function (s, d) { return s + (+d.rataLunara || 0); }, 0);
    // Notă: dacă userul a trecut rate și în cheltuieli.rate, nu dublăm — folosim max.
    var rateInChelt = +(p.cheltuieli && p.cheltuieli.rate) || 0;
    var rateEfectiv = Math.max(rateDatorii, rateInChelt);
    var cheltFaraRate = chelt - rateInChelt;
    var economii = venit - cheltFaraRate - rateEfectiv;
    return {
      venit: venit, cheltuieli: cheltFaraRate, rate: rateEfectiv,
      economii: economii,
      rataEconomisire: venit > 0 ? economii / venit : 0
    };
  };

  /* ===========================================================================
     3. AVERE NETĂ
     =========================================================================== */
  U.activeTotal = function (p) {
    p = p || U.getProfil();
    var a = p.active || {}, t = 0;
    Object.keys(a).forEach(function (k) { t += +a[k] || 0; });
    return t;
  };
  // Avere investibilă (lichidă + investiții) — exclude locuința proprie + auto.
  U.avereInvestibila = function (p) {
    p = p || U.getProfil();
    var a = p.active || {};
    return (+a.cash || 0) + (+a.depozite || 0) + (+a.investitii || 0) + (+a.crypto || 0) +
           (+a.titluriStat || 0) + (+a.pensiePilon3 || 0) + (+a.imobiliareInvestitii || 0);
  };
  U.datoriiTotal = function (p) {
    p = p || U.getProfil();
    return (p.datorii || []).reduce(function (s, d) { return s + (+d.sold || 0); }, 0);
  };
  U.avereNeta = function (p) {
    p = p || U.getProfil();
    return { active: U.activeTotal(p), datorii: U.datoriiTotal(p), net: U.activeTotal(p) - U.datoriiTotal(p) };
  };

  /* ===========================================================================
     4. PROIECȚIE FISCALĂ AN-END — cât vei datora la Declarația Unică
     =========================================================================== */
  U.proiectieFiscala = function (p) {
    p = p || U.getProfil();
    var f = F();
    var s = U.venitStructuraAnual(p);
    var v = p.venituri || {};
    var componente = [];
    var totalDU = 0; // ce se declară în Declarația Unică (PFA + chirii + dividende + invest.)

    if (s.totalTaxe > 0 && (p.structura.indexOf("pfa") === 0)) {
      componente.push({ nume: "PFA (CAS+CASS+impozit)", suma: s.totalTaxe });
      totalDU += s.totalTaxe;
    }
    var chiriiAn = (+v.chiriiLunar || 0) * 12;
    if (chiriiAn > 0 && f) {
      var ch = f.impozitChirii(chiriiAn);
      componente.push({ nume: "Chirii (impozit+CASS)", suma: ch.totalTaxe });
      totalDU += ch.totalTaxe;
    }
    var divAn = +v.dividendeAnual || 0;
    if (divAn > 0 && f) {
      var cassDiv = f.cassPasiv(divAn).cass;
      componente.push({ nume: "CASS pe dividende", suma: cassDiv });
      totalDU += cassDiv; // impozitul pe dividende e reținut la sursă, dar CASS se declară
    }
    var termen = f ? f.urmatorulTermenDU() : null;
    return {
      total: totalDU,
      componente: componente,
      termen: termen,
      zileRamase: termen ? CF.zilePana(termen) : null,
      structura: p.structura,
      tvaPlatitor: p.tvaPlatitor
    };
  };

  /* ===========================================================================
     5. FIRE — "Drumul spre Libertate"
     =========================================================================== */
  U.fire = function (p) {
    p = p || U.getProfil();
    var cf = U.cashFlow(p);
    var cheltAnual = (U.cheltuieliLunar(p) + cf.rate) * 12;
    if (cheltAnual <= 0) cheltAnual = cf.cheltuieli * 12;
    var capitalTinta = cheltAnual * 25;             // regula 4%
    var capitalCurent = U.avereInvestibila(p);
    var economiiLunare = Math.max(0, cf.economii);
    var r = (p.obiective.randamentReal || 5) / 100;
    var aniRamasi = U._aniPanaLa(capitalCurent, economiiLunare, capitalTinta, r);
    var dataLibertate = null;
    if (isFinite(aniRamasi)) {
      var d = new Date();
      d.setMonth(d.getMonth() + Math.round(aniRamasi * 12));
      dataLibertate = d;
    }
    return {
      cheltAnual: cheltAnual,
      capitalTinta: capitalTinta,
      capitalCurent: capitalCurent,
      progres: capitalTinta > 0 ? Math.min(1, capitalCurent / capitalTinta) : 0,
      economiiLunare: economiiLunare,
      aniRamasi: aniRamasi,
      dataLibertate: dataLibertate,
      varstaLibertate: isFinite(aniRamasi) ? (p.varsta + aniRamasi) : null,
      venitPasivLunar: capitalCurent * 0.04 / 12   // ce produce azi averea, la 4%
    };
  };
  // Câți ani până capitalul atinge ținta, cu economisire lunară + randament.
  U._aniPanaLa = function (capital, economiiLunare, tinta, randamentAnual) {
    if (capital >= tinta) return 0;
    if (economiiLunare <= 0 && randamentAnual <= 0) return Infinity;
    var r = randamentAnual / 12, bal = capital, luni = 0;
    while (bal < tinta && luni < 1200) { bal = bal * (1 + r) + economiiLunare; luni++; }
    return luni >= 1200 ? Infinity : luni / 12;
  };

  /* ===========================================================================
     6. SCOR DE SĂNĂTATE FINANCIARĂ (0–100) — cu top sfaturi
     =========================================================================== */
  U.scorSanatate = function (p) {
    p = p || U.getProfil();
    var cf = U.cashFlow(p), comp = [];
    var a = p.active || {};

    // a) Fond de urgență — luni de cheltuieli acoperite din lichidități. Țintă 6.
    var cheltLunar = U.cheltuieliLunar(p) + cf.rate;
    var lichid = (+a.cash || 0) + (+a.depozite || 0);
    var luniFond = cheltLunar > 0 ? lichid / cheltLunar : (lichid > 0 ? 6 : 0);
    var sFond = Math.max(0, Math.min(100, (luniFond / 6) * 100));
    comp.push({ nume: "Fond de urgență", scor: sFond, pondere: 25,
      detaliu: luniFond.toFixed(1) + " luni acoperite (țintă: 6)",
      sfat: luniFond < 6 ? "Mai pune " + CF.lei(Math.max(0, 6 * cheltLunar - lichid)) + " în fondul de urgență (cont separat, lichid)." : "Fond solid. Restul economiilor pot lucra investit." });

    // b) Rată de economisire — % din venit care rămâne. Țintă 20%.
    var sEcon = Math.max(0, Math.min(100, (cf.rataEconomisire / 0.20) * 100));
    comp.push({ nume: "Rată de economisire", scor: sEcon, pondere: 25,
      detaliu: CF.pct(Math.max(0, cf.rataEconomisire)) + " din venit (țintă: 20%)",
      sfat: cf.rataEconomisire < 0.20 ? "Țintește 20% din venit economisit. Acum: " + CF.lei(Math.max(0, cf.economii)) + "/lună." : "Excelent — economisești peste 20%. Automatizează transferul." });

    // c) Grad de îndatorare — rate / venit. Sub 20% = sănătos, peste 40% = risc.
    var grad = cf.venit > 0 ? cf.rate / cf.venit : 0;
    var sDat = cf.rate <= 0 ? 100 : Math.max(0, Math.min(100, (1 - (grad - 0.15) / 0.35) * 100));
    comp.push({ nume: "Grad de îndatorare", scor: sDat, pondere: 20,
      detaliu: CF.pct(grad) + " din venit pe rate (sănătos: < 30%)",
      sfat: grad > 0.30 ? "Ratele depășesc 30% din venit — prioritizează achitarea datoriilor scumpe." : "Datorii sub control." });

    // d) Datorii toxice — există datorii cu dobândă > 15%?
    var toxice = (p.datorii || []).filter(function (d) { return (+d.dobanda || 0) > 15; });
    var soldToxic = toxice.reduce(function (s, d) { return s + (+d.sold || 0); }, 0);
    var sTox = soldToxic <= 0 ? 100 : Math.max(0, 100 - Math.min(100, soldToxic / Math.max(1, U.venitNetLunar(p)) * 20));
    comp.push({ nume: "Datorii scumpe", scor: sTox, pondere: 15,
      detaliu: toxice.length ? CF.lei(soldToxic) + " cu dobândă > 15%" : "Fără datorii scumpe",
      sfat: toxice.length ? "Achită întâi datoriile cu dobândă mare (card, IFN) — costă cel mai mult." : "Niciun credit toxic. Bravo." });

    // e) Diversificare avere — în câte clase de active e împărțită averea investibilă.
    var clase = ["investitii", "crypto", "titluriStat", "pensiePilon3", "imobiliareInvestitii", "depozite"];
    var clNz = clase.filter(function (k) { return (+a[k] || 0) > 0; }).length;
    var inv = U.avereInvestibila(p);
    var sDiv = inv <= 0 ? 0 : Math.max(0, Math.min(100, (clNz / 3) * 100));
    comp.push({ nume: "Diversificare", scor: sDiv, pondere: 15,
      detaliu: inv <= 0 ? "Încă nu investești" : clNz + " clase de active",
      sfat: inv <= 0 ? "Începe cu un ETF global + titluri de stat. Banii care stau în cont pierd la inflație." : (clNz < 2 ? "Diversifică: adaugă o a doua clasă (ex. titluri de stat alături de acțiuni)." : "Portofoliu rezonabil de diversificat.") });

    var pondTot = comp.reduce(function (s, c) { return s + c.pondere; }, 0);
    var scor = comp.reduce(function (s, c) { return s + c.scor * c.pondere; }, 0) / pondTot;
    var sfaturi = comp.slice().filter(function (c) { return c.scor < 80; })
      .sort(function (x, y) { return (x.scor * x.pondere) - (y.scor * y.pondere); })
      .slice(0, 3);
    return {
      scor: Math.round(scor),
      eticheta: scor >= 80 ? "Excelent" : scor >= 60 ? "Bun" : scor >= 40 ? "De îmbunătățit" : "Fragil",
      componente: comp,
      prioritati: sfaturi
    };
  };

  /* ===========================================================================
     7. OPTIMIZATOR DE STRUCTURĂ — ce formă îți lasă cei mai mulți bani
     Compară: PFA real, SRL micro 1%, SRL real 16%, salariat-echivalent.
     Pe un venit brut anual (cifră de afaceri) + cheltuieli deductibile date.
     =========================================================================== */
  U.optimStructura = function (cifraAnuala, cheltuieliAnuale, dependenti) {
    var f = F();
    if (!f) return { variante: [], best: null };
    cifraAnuala = Math.max(0, cifraAnuala || 0);
    cheltuieliAnuale = Math.max(0, cheltuieliAnuale || 0);
    dependenti = dependenti || 0;
    var variante = [];

    // PFA real
    var pfa = f.pfaReal(cifraAnuala, cheltuieliAnuale);
    variante.push({ tip: "PFA — sistem real", net: pfa.netInMana, taxe: pfa.totalTaxe,
      nota: "Simplu, fără contabil obligatoriu. CAS doar peste 12 salarii minime." });

    // SRL micro 1% (presupune tot profitul scos ca dividend)
    var micro = f.srlMicro(cifraAnuala, cheltuieliAnuale, 1);
    variante.push({ tip: "SRL micro 1%", net: micro.netInMana, taxe: micro.totalTaxe,
      nota: micro.depasestePlafonMicro ? "⚠️ Depășești plafonul micro (100.000 €) — nu mai e eligibil." : "Necesită min. 1 salariat cu normă întreagă. Plafon 100.000 €." });

    // SRL real 16% pe profit + dividend
    var profit = Math.max(0, cifraAnuala - cheltuieliAnuale);
    var impProfit = profit * f.cote.microProfit;
    var profitNet = profit - impProfit;
    var impDiv = profitNet * f.cote.dividende;
    var cassDiv = f.cassPasiv(profitNet).cass;
    var netReal = profitNet - impDiv - cassDiv;
    variante.push({ tip: "SRL real 16%", net: netReal, taxe: impProfit + impDiv + cassDiv,
      nota: "Pentru cheltuieli mari/marje mici. Impozit doar pe profit, nu pe cifra de afaceri." });

    // Salariat-echivalent (dacă cifra ar fi salariu brut)
    var sal = f.salariuNet((cifraAnuala) / 12, dependenti);
    variante.push({ tip: "Salariat (echivalent)", net: sal.net * 12, taxe: (sal.cas + sal.cass + sal.impozit) * 12,
      nota: "Reper: dacă ai primi aceeași sumă ca salariu brut. Include pensie + concedii." });

    variante.sort(function (a, b) { return b.net - a.net; });
    variante.forEach(function (vr, i) { vr.rang = i + 1; vr.best = i === 0; });
    return { variante: variante, best: variante[0],
      diferenta: variante.length > 1 ? variante[0].net - variante[1].net : 0 };
  };

  /* ===========================================================================
     8. CALENDAR FISCAL PERSONAL — termene pe structura userului
     =========================================================================== */
  U.deadlines = function (p, an) {
    p = p || U.getProfil();
    var f = F();
    var anBaza = an || (new Date()).getFullYear();
    var ev = [];
    // fereastră rulantă: anul curent + următorul, ca să existe mereu termene viitoare
    [anBaza, anBaza + 1].forEach(function (anul) { populaAn(anul); });
    function populaAn(an) {
    function add(luna, zi, titlu, tip, desc) {
      ev.push({ data: new Date(an, luna - 1, zi), titlu: titlu, tip: tip, desc: desc || "" });
    }
    var arePFA = p.structura.indexOf("pfa") === 0;
    var areSRL = p.structura.indexOf("srl") === 0;
    var areChirii = (p.venituri && +p.venituri.chiriiLunar > 0);
    var areInvest = (+(p.active && p.active.investitii) || 0) > 0 || (+(p.active && p.active.crypto) || 0) > 0 ||
                    (+(p.venituri && p.venituri.dividendeAnual) || 0) > 0;

    if (arePFA || areChirii || areInvest) {
      add(4, 15, "Declarația Unică — bonificație 3%", "du", "Plătește integral până azi pentru reducerea de 3%.");
      add(5, 25, "Declarația Unică — depunere & plată", "du", "Termen final D212: venituri " + (an - 1) + " + estimat " + an + ".");
    }
    if (p.tvaPlatitor) {
      for (var m = 1; m <= 12; m++) add(m, 25, "Decont TVA (D300) + plată", "tva", "Lunar/trimestrial, până pe 25.");
    }
    if (areSRL) {
      add(1, 25, "Impozit micro/profit trim. IV + D100", "srl", "Declarare și plată impozit trimestrul precedent.");
      add(4, 25, "Impozit micro/profit trim. I", "srl", "");
      add(7, 25, "Impozit micro/profit trim. II", "srl", "");
      add(10, 25, "Impozit micro/profit trim. III", "srl", "");
      add(3, 25, "Situații financiare anuale (bilanț)", "srl", "Depunere bilanț an precedent (termen uzual).");
    }
    if ((+(p.venituri && p.venituri.salariuNet) || 0) > 0 || areSRL) {
      // angajatori / cei cu salariați: D112 lunar
      add((new Date()).getMonth() + 1, 25, "D112 — salarii & contribuții", "salarii", "Lunar, pentru cei cu salariați.");
    }
    } // populaAn
    // Doar termenele viitoare, sortate, dedublate.
    var azi = new Date(); azi.setHours(0, 0, 0, 0);
    var vazut = {};
    return ev.filter(function (e) { return e.data >= azi; })
             .filter(function (e) { var k = e.data.getTime() + e.titlu; if (vazut[k]) return false; vazut[k] = 1; return true; })
             .sort(function (a, b) { return a.data - b.data; });
  };

  /* ===========================================================================
     9. CONTEXT PENTRU CONCIERGE AI — "cunoaște cifrele tale"
     Produce un obiect compact + un rezumat text injectat ca `context` în ai-anaf.
     =========================================================================== */
  U.profileContext = function (p) {
    p = p || U.getProfil();
    if (!U.areDate(p)) return null;
    var f = F();
    var an = U.avereNeta(p), cf = U.cashFlow(p), fire = U.fire(p), scor = U.scorSanatate(p);
    var rez = [];
    rez.push("Profil utilizator (cifrele LUI, folosește-le în răspuns):");
    rez.push("- Vârstă: " + p.varsta + ", persoane în întreținere: " + p.dependenti +
             (p.oras ? ", oraș: " + p.oras : "") + ".");
    rez.push("- Structură: " + U.structuraLabel(p.structura) + (p.tvaPlatitor ? " (plătitor TVA)" : "") + ".");
    rez.push("- Venit net lunar (toate sursele): " + CF.lei(U.venitNetLunar(p)) + ".");
    rez.push("- Cheltuieli lunare: " + CF.lei(U.cheltuieliLunar(p)) + "; economisește " + CF.lei(cf.economii) + "/lună (" + CF.pct(Math.max(0, cf.rataEconomisire)) + ").");
    rez.push("- Avere netă: " + CF.lei(an.net) + " (active " + CF.lei(an.active) + ", datorii " + CF.lei(an.datorii) + ").");
    rez.push("- Avere investibilă: " + CF.lei(fire.capitalCurent) + "; obiectiv FIRE " + CF.lei(fire.capitalTinta) +
             " (progres " + CF.pct(fire.progres) + (isFinite(fire.aniRamasi) ? ", ~" + fire.aniRamasi.toFixed(1) + " ani rămași" : "") + ").");
    rez.push("- Scor sănătate financiară: " + scor.scor + "/100 (" + scor.eticheta + ").");
    if (scor.prioritati.length) rez.push("- De îmbunătățit: " + scor.prioritati.map(function (s) { return s.nume; }).join(", ") + ".");
    var prog = U.proiectieFiscala(p);
    if (prog.total > 0) rez.push("- Estimare de plată la Declarația Unică: " + CF.lei(prog.total) +
             (prog.zileRamase != null ? " (peste " + prog.zileRamase + " zile)" : "") + ".");

    return {
      tip: "profil_ultra",
      an: f ? f.an : 2026,
      structura: p.structura,
      tvaPlatitor: p.tvaPlatitor,
      varsta: p.varsta,
      dependenti: p.dependenti,
      venitNetLunar: Math.round(U.venitNetLunar(p)),
      cheltuieliLunar: Math.round(U.cheltuieliLunar(p)),
      economiiLunar: Math.round(cf.economii),
      avereNeta: Math.round(an.net),
      avereInvestibila: Math.round(fire.capitalCurent),
      scorSanatate: scor.scor,
      rezumat: rez.join("\n"),
      nota: "Răspunde personalizat, pe cazul ACESTUI utilizator. Cifrele din profil sunt date reale introduse de el. Estimările fiscale sunt pe regulile RO 2026."
    };
  };

  /* ===========================================================================
     10. UTILITARE UI partajate (etichete, ring SVG, bară)
     =========================================================================== */
  U.structuraLabel = function (s) {
    return ({ salariat: "Salariat", pfa_real: "PFA (sistem real)", pfa_norma: "PFA (normă de venit)",
      srl_micro: "SRL microîntreprindere (1%)", srl_real: "SRL (impozit pe profit 16%)", mixt: "Mixt (salariu + firmă)" })[s] || s;
  };
  U.STRUCTURI = [
    { v: "salariat", t: "Salariat" }, { v: "pfa_real", t: "PFA — sistem real" },
    { v: "pfa_norma", t: "PFA — normă de venit" }, { v: "srl_micro", t: "SRL micro 1%" },
    { v: "srl_real", t: "SRL — profit 16%" }, { v: "mixt", t: "Mixt (salariu + firmă)" }
  ];

  /* ===========================================================================
     11. PLAN DE PROTECȚIE — "scutul familiei": asigurare de viață + succesiune
     Cât ar avea nevoie familia ta dacă ție ți s-ar întâmpla ceva azi.
     =========================================================================== */
  U.protectie = function (p) {
    p = p || U.getProfil();
    var venitAnual = U.venitNetLunar(p) * 12;
    var datorii = U.datoriiTotal(p);
    var aniSprijin = p.dependenti > 0 ? 10 : (p.stareCivila === "casatorit" ? 5 : 0);
    // Fond educație estimativ: ~80.000 lei/copil până la facultate.
    var fondCopii = (+p.dependenti || 0) * 80000;
    // Nevoia de acoperire = datorii (să nu rămână familia cu ele) + ani de venit + studii.
    var nevoie = datorii + venitAnual * aniSprijin + fondCopii;
    var active = U.avereInvestibila(p); // ce ar acoperi deja averea lichidă
    var gap = Math.max(0, nevoie - active);
    var areAvereDeTransmis = (+(p.active && p.active.imobiliareInvestitii) || 0) +
                             (+(p.active && p.active.locuintaProprie) || 0) > 0 ||
                             p.structura.indexOf("srl") === 0;
    return {
      venitAnual: venitAnual, datorii: datorii, aniSprijin: aniSprijin, fondCopii: fondCopii,
      nevoie: nevoie, acoperitDeAvere: Math.min(nevoie, active), gap: gap,
      areDependenti: p.dependenti > 0,
      necesitaSuccesiune: areAvereDeTransmis,
      areFirma: p.structura.indexOf("srl") === 0
    };
  };

  /* ===========================================================================
     12. HARTA BANILOR — alocare țintă vs reală (educativ, nu sfat de investiții)
     "Am bani, ce fac cu ei?" — fond urgență, titluri stat, acțiuni/ETF, etc.
     =========================================================================== */
  U.alocare = function (p) {
    p = p || U.getProfil();
    var a = p.active || {};
    var risc = p.toleranteRisc || "medie";
    // Procent acțiuni țintă pe vârstă (regula 110-vârstă), ajustat pe risc.
    var baseEq = Math.max(20, Math.min(90, 110 - (p.varsta || 35)));
    if (risc === "mica") baseEq = baseEq * 0.7;
    else if (risc === "mare") baseEq = Math.min(95, baseEq * 1.2);
    var eq = Math.round(baseEq);
    // Restul: titluri de stat / obligațiuni, puțin cash tactic, alternative mici.
    var bonds = Math.round((100 - eq) * 0.7);
    var cashTactic = 100 - eq - bonds;
    var alt = risc === "mare" ? 5 : 0;
    if (alt) { eq = Math.max(0, eq - alt); }
    var tinta = [
      { clasa: "Acțiuni / ETF global", pct: eq, cheie: "investitii",
        nota: "Motor de creștere pe termen lung (ex. ETF pe indici globali, prin broker)." },
      { clasa: "Titluri de stat (Fidelis/Tezaur)", pct: bonds, cheie: "titluriStat",
        nota: "Stabilitate + dobândă, scutite de impozit. Reazemul portofoliului." },
      { clasa: "Cash tactic / depozit", pct: cashTactic, cheie: "depozite",
        nota: "Lichiditate pentru oportunități, peste fondul de urgență." }
    ];
    if (alt) tinta.push({ clasa: "Alternative (crypto/aur)", pct: alt, cheie: "crypto",
      nota: "Doar bani pe care ți-i permiți să-i pierzi. Volatilitate mare." });

    var investibil = U.avereInvestibila(p);
    var curent = {
      investitii: (+a.investitii || 0), titluriStat: (+a.titluriStat || 0),
      depozite: (+a.depozite || 0) + (+a.cash || 0), crypto: (+a.crypto || 0)
    };
    tinta.forEach(function (t) {
      t.sumaTinta = investibil * t.pct / 100;
      t.sumaCurenta = curent[t.cheie] || 0;
      t.pctCurent = investibil > 0 ? (t.sumaCurenta / investibil * 100) : 0;
      t.diferenta = t.sumaTinta - t.sumaCurenta;
    });
    return { tinta: tinta, investibil: investibil, risc: risc };
  };

  // Inel SVG de progres (pentru scor / FIRE). val 0..1.
  U.ringSVG = function (val, opts) {
    opts = opts || {};
    var sz = opts.size || 140, sw = opts.stroke || 12, r = (sz - sw) / 2, c = 2 * Math.PI * r;
    var off = c * (1 - Math.max(0, Math.min(1, val)));
    var col = opts.color || (val >= 0.8 ? "#10b981" : val >= 0.5 ? "#E8C268" : "#ef5350");
    var label = opts.label != null ? opts.label : Math.round(val * 100);
    var sub = opts.sub || "";
    return '<svg class="cf-ring" viewBox="0 0 ' + sz + ' ' + sz + '" width="' + sz + '" height="' + sz + '">' +
      '<circle cx="' + sz / 2 + '" cy="' + sz / 2 + '" r="' + r + '" fill="none" stroke="var(--border)" stroke-width="' + sw + '"/>' +
      '<circle cx="' + sz / 2 + '" cy="' + sz / 2 + '" r="' + r + '" fill="none" stroke="' + col + '" stroke-width="' + sw +
      '" stroke-linecap="round" stroke-dasharray="' + c + '" stroke-dashoffset="' + off +
      '" transform="rotate(-90 ' + sz / 2 + ' ' + sz / 2 + ')"/>' +
      '<text x="50%" y="48%" text-anchor="middle" dominant-baseline="middle" font-size="' + (sz * 0.26) + '" font-weight="800" fill="var(--text)">' + label + '</text>' +
      (sub ? '<text x="50%" y="66%" text-anchor="middle" font-size="' + (sz * 0.1) + '" fill="var(--muted)">' + sub + '</text>' : '') +
      '</svg>';
  };

  // Sigiliu-monogramă CF (crest de bancă privată) — folosit o dată per pagină.
  U.sealSVG = function () {
    return '<svg class="u-seal" viewBox="0 0 100 100" role="img" aria-label="Clubul Financiar">' +
      '<circle cx="50" cy="50" r="47" fill="none" stroke="var(--u-gold)" stroke-width="1.3"/>' +
      '<circle cx="50" cy="50" r="40" fill="none" stroke="var(--u-gold)" stroke-width=".6" stroke-dasharray="1 3.4"/>' +
      '<text x="50" y="59" text-anchor="middle" font-family="Fraunces,Georgia,serif" font-weight="600" font-size="30" letter-spacing="-1" fill="var(--u-gold)">CF</text>' +
      '</svg>';
  };

  // Count-up animat pentru cifra-erou. Respectă prefers-reduced-motion.
  U.countUp = function (el, target, opts) {
    el = typeof el === "string" ? CF.$(el) : el;
    if (!el) return;
    opts = opts || {};
    var fmt = opts.fmt || function (n) { return CF.lei(n); };
    var dur = opts.dur || 900;
    var reduce = root.matchMedia && root.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce || !isFinite(target)) { el.textContent = fmt(target || 0); return; }
    var t0 = null, from = 0;
    function step(ts) {
      if (t0 == null) t0 = ts;
      var k = Math.min(1, (ts - t0) / dur), e = 1 - Math.pow(1 - k, 3);
      el.textContent = fmt(from + (target - from) * e);
      if (k < 1) root.requestAnimationFrame(step);
    }
    root.requestAnimationFrame(step);
  };

  // Variația averii nete față de luna trecută (din snapshot-urile tool_logs).
  // Întoarce {pct, abs, are} sau {are:false} dacă nu există istoric.
  U.deltaAvere = function (netAcum, tool) {
    try {
      var log = CF.getLog(tool || "ultra-cockpit") || {};
      var curent = CF.perioadaCurenta();
      var perioade = Object.keys(log).filter(function (k) { return k < curent && log[k] && isFinite(log[k].avere); }).sort();
      if (!perioade.length) return { are: false };
      var prev = log[perioade[perioade.length - 1]].avere;
      if (!prev) return { are: false };
      return { are: true, abs: netAcum - prev, pct: (netAcum - prev) / Math.abs(prev) };
    } catch (e) { return { are: false }; }
  };

  CF.U = U;

  // Auto-semnătură: pune sigiliul-monogramă + guilloche pe orice hero Ultra care
  // nu le are deja (paginile-erou cockpit/hub/libertate le pun manual). DRY peste suită.
  function initHeroSeal() {
    try {
      var heroes = document.querySelectorAll(".u-page .u-hero");
      Array.prototype.forEach.call(heroes, function (h) {
        if (h.querySelector(".u-seal") || h.querySelector("#uSeal,#ckSeal") || h.getAttribute("data-no-seal")) return;
        if (!h.style.position) h.style.position = "relative";
        var g = document.createElement("div");
        g.className = "u-guilloche"; g.setAttribute("aria-hidden", "true");
        h.insertBefore(g, h.firstChild);
        var s = document.createElement("div");
        s.style.marginBottom = "14px"; s.innerHTML = U.sealSVG();
        h.insertBefore(s, g.nextSibling);
      });
    } catch (e) {}
  }
  if (root.document) {
    if (document.readyState !== "loading") initHeroSeal();
    else document.addEventListener("DOMContentLoaded", initHeroSeal);
  }
})(typeof window !== "undefined" ? window : this);
