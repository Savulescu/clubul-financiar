/* =============================================================================
   cf-tool.js — helper PARTAJAT pentru toate uneltele Hub Fiscal / Pro.
   Oferă: formatare, gating pe tier, logare lunară (localStorage + Supabase),
   export .ics, client AI (Edge Function multi-provider), remindere.
   Depinde de: fiscal-2026.js (opțional), @supabase/supabase-js (din site.js).
   ============================================================================= */
(function (root) {
  "use strict";

  var CF = {};

  /* ---------- FORMATARE ---------- */
  CF.lei = function (n) {
    if (!isFinite(n)) n = 0;
    return Math.round(n).toLocaleString("ro-RO") + " lei";
  };
  CF.lei2 = function (n) {
    if (!isFinite(n)) n = 0;
    return n.toLocaleString("ro-RO", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " lei";
  };
  CF.pct = function (n) { return (n * 100).toLocaleString("ro-RO", { maximumFractionDigits: 2 }) + "%"; };
  CF.dataRO = function (d) {
    if (!(d instanceof Date)) d = new Date(d);
    return d.toLocaleDateString("ro-RO", { day: "numeric", month: "long", year: "numeric" });
  };
  CF.zilePana = function (d) {
    if (!(d instanceof Date)) d = new Date(d);
    return Math.ceil((d - new Date()) / 86400000);
  };
  CF.$ = function (id) { return document.getElementById(id); };

  /* ---------- TIER / GATING ----------
     Tier-ul real vine din site.js (window.cfTier). Ierarhie: free<premium<pro<ultra.
     O unealtă declară de ce tier are nevoie; CF.requireTier afișează lock dacă nu. */
  var RANK = { free: 0, premium: 1, pro: 2, ultra: 3 };
  CF.tier = function () { return root.cfTier || (root.cfPremium ? "premium" : "free"); };
  CF.hasTier = function (needed) { return RANK[CF.tier()] >= RANK[needed || "pro"]; };

  // Montează un gate peste un container dacă userul n-are tier-ul cerut.
  // Conținutul rămâne în DOM (SEO + revelare instant la login premium).
  CF.requireTier = function (containerId, needed, opts) {
    needed = needed || "pro";
    opts = opts || {};
    var el = typeof containerId === "string" ? CF.$(containerId) : containerId;
    if (!el) return;
    function apply() {
      var ok = CF.hasTier(needed) || root.cfAdmin;
      el.classList.toggle("cf-locked", !ok);
      var g = el.querySelector(".cf-gate");
      if (!ok && !g) {
        g = document.createElement("div");
        g.className = "cf-gate";
        var label = needed.charAt(0).toUpperCase() + needed.slice(1);
        g.innerHTML =
          '<div class="cf-gate-in">' +
          '<div class="cf-gate-ic">🔒</div>' +
          '<h3>Unealtă ' + label + '</h3>' +
          '<p>' + (opts.msg || "Deblochează această unealtă cu planul " + label + ".") + '</p>' +
          '<a class="btn btn-primary" href="/premium#alege">Vezi planul ' + label + '</a>' +
          '</div>';
        el.appendChild(g);
      } else if (ok && g) { g.remove(); }
    }
    apply();
    root.addEventListener("cf-auth", apply);
  };

  /* ---------- STOCARE date-user (logare lunară) ----------
     Strategie hibridă: scrie ÎNTOTDEAUNA în localStorage (instant, offline) și,
     dacă userul e logat, sincronizează în Supabase tabelul `tool_logs`
     (cheie: user_id + tool + period). Citirea preferă Supabase, fallback local. */
  function sb() { return root.cfSupabase || (root.supabase && root.__cfSB) || null; }
  CF.uid = function () { return root.cfUserId || null; };

  CF.lsKey = function (tool, key) { return "cf-tool:" + tool + ":" + (key || "data"); };

  CF.saveLocal = function (tool, data, key) {
    try { localStorage.setItem(CF.lsKey(tool, key), JSON.stringify(data)); } catch (e) {}
  };
  CF.loadLocal = function (tool, key) {
    try { return JSON.parse(localStorage.getItem(CF.lsKey(tool, key)) || "null"); }
    catch (e) { return null; }
  };

  // Loghează o intrare pentru o perioadă (ex. "2026-06") — pentru recurență.
  CF.logEntry = function (tool, period, payload) {
    var all = CF.loadLocal(tool, "log") || {};
    all[period] = Object.assign({}, all[period], payload, { _ts: new Date().toISOString() });
    CF.saveLocal(tool, all, "log");
    var client = sb(), uid = CF.uid();
    if (client && uid) {
      try {
        client.from("tool_logs").upsert({
          user_id: uid, tool: tool, period: period, payload: all[period]
        }, { onConflict: "user_id,tool,period" }).then(function () {}, function () {});
      } catch (e) {}
    }
    return all;
  };

  CF.getLog = function (tool) {
    return CF.loadLocal(tool, "log") || {};
  };

  // Citește din Supabase (cross-device) și suprascrie cache-ul local.
  CF.syncLog = function (tool) {
    var client = sb(), uid = CF.uid();
    if (!client || !uid) return Promise.resolve(CF.getLog(tool));
    return client.from("tool_logs").select("period,payload").eq("user_id", uid).eq("tool", tool)
      .then(function (res) {
        if (res && res.data) {
          var all = {};
          res.data.forEach(function (r) { all[r.period] = r.payload; });
          CF.saveLocal(tool, all, "log");
          return all;
        }
        return CF.getLog(tool);
      }, function () { return CF.getLog(tool); });
  };

  CF.perioadaCurenta = function () {
    var d = new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0");
  };

  /* ---------- REMINDERE (alerte recurente) ----------
     Setează o preferință de reminder în tabelul `reminders` (citit de cronul lunar
     GitHub Actions care trimite Telegram/email). Fallback: doar local. */
  CF.setReminder = function (tool, opts) {
    opts = opts || {};
    var rec = { tool: tool, kind: opts.kind || "monthly", note: opts.note || "",
                next_date: opts.date || null, channel: opts.channel || "telegram" };
    CF.saveLocal(tool, rec, "reminder");
    var client = sb(), uid = CF.uid();
    if (client && uid) {
      try {
        client.from("reminders").upsert(Object.assign({ user_id: uid }, rec),
          { onConflict: "user_id,tool" }).then(function () {}, function () {});
      } catch (e) {}
    }
  };

  /* ---------- EXPORT CALENDAR (.ics) ---------- */
  CF.icsDownload = function (titlu, descriere, data) {
    var d = (data instanceof Date) ? data : new Date(data);
    function z(n) { return String(n).padStart(2, "0"); }
    var dt = d.getFullYear() + z(d.getMonth() + 1) + z(d.getDate());
    var uid = "cf-" + dt + "-" + Math.abs(hash(titlu)) + "@clubulfinanciar.ro";
    var ics = [
      "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Clubul Financiar//RO",
      "BEGIN:VEVENT", "UID:" + uid, "DTSTART;VALUE=DATE:" + dt,
      "SUMMARY:" + esc(titlu), "DESCRIPTION:" + esc(descriere || ""),
      "BEGIN:VALARM", "TRIGGER:-P7D", "ACTION:DISPLAY", "DESCRIPTION:" + esc(titlu), "END:VALARM",
      "END:VEVENT", "END:VCALENDAR"
    ].join("\r\n");
    var blob = new Blob([ics], { type: "text/calendar" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = (titlu.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")) + ".ics";
    document.body.appendChild(a); a.click(); a.remove();
  };
  function esc(s) { return String(s).replace(/[,;\\]/g, "\\$&").replace(/\n/g, "\\n"); }
  function hash(s) { var h = 0; for (var i = 0; i < s.length; i++) { h = (h << 5) - h + s.charCodeAt(i) | 0; } return h; }

  /* ---------- EXPORT PDF (print-to-PDF, fără librărie) ---------- */
  CF.printResult = function (titlu, htmlBody) {
    var w = window.open("", "_blank");
    if (!w) return;
    w.document.write(
      '<html><head><meta charset="utf-8"><title>' + esc(titlu) + ' — Clubul Financiar</title>' +
      '<style>body{font-family:system-ui,Segoe UI,Arial;max-width:720px;margin:30px auto;color:#0f2540;padding:0 20px}' +
      'h1{color:#0e2750;border-bottom:2px solid #caa44a;padding-bottom:8px}table{width:100%;border-collapse:collapse;margin:16px 0}td{padding:8px 6px;border-bottom:1px solid #e6edf5}' +
      'td:last-child{text-align:right;font-weight:700}.muted{color:#5b7088;font-size:.85rem}.big{font-size:2rem;font-weight:800;color:#9a7414}' +
      '</style></head><body><h1>' + esc(titlu) + '</h1>' + htmlBody +
      '<p class="muted">Clubul Financiar · clubulfinanciar.ro · ' + CF.dataRO(new Date()) +
      ' · Estimare educativă, nu consultanță fiscală.</p>' +
      '<script>window.onload=function(){window.print()}<\/script></body></html>');
    w.document.close();
  };

  /* ---------- CLIENT AI (Asistent ANAF) ----------
     Cheamă Supabase Edge Function `ai-anaf` (multi-provider free-LLM, ține cheile).
     Fallback grațios dacă endpoint-ul nu e încă deployat. */
  CF.AI_ENDPOINT = "https://maumjqciuxdbwjtvcpsy.functions.supabase.co/ai-anaf";
  CF.aiChat = function (messages, opts) {
    opts = opts || {};
    var body = JSON.stringify({ messages: messages, context: opts.context || null, maxTokens: opts.maxTokens || null });
    var tries = opts.retries != null ? opts.retries : 3;
    function fail(content) { return /momentan asistentul ai nu e disponibil|nu am putut obține/i.test(content || ""); }
    function attempt(n) {
      return fetch(CF.AI_ENDPOINT, { method: "POST", headers: { "Content-Type": "application/json" }, body: body })
        .then(function (r) { return r.json().catch(function () { return {}; }); })
        .then(function (j) {
          var content = j.content || j.answer || "";
          // funcția întoarce 200 + {error,...} sau mesajul de fallback când toți providerii pică → reîncearcă
          if ((j.error || !content || fail(content)) && n < tries) {
            return new Promise(function (res) { setTimeout(res, 1000 * n); }).then(function () { return attempt(n + 1); });
          }
          return { content: content, provider: j.provider || "ai", sources: j.sources || [], failed: !!(j.error || !content || fail(content)) };
        })
        .catch(function () {
          if (n < tries) return new Promise(function (res) { setTimeout(res, 1000 * n); }).then(function () { return attempt(n + 1); });
          return { content: "Momentan nu am putut obține un răspuns. Mai încearcă o dată în câteva momente.", provider: "none", sources: [], failed: true };
        });
    }
    return attempt(1);
  };

  /* ---------- QUOTA AI (pe tier) ---------- */
  CF.aiQuota = function () {
    var t = CF.tier();
    if (t === "ultra") return Infinity;
    if (t === "pro") return 60;
    if (t === "premium") return 5;
    return 0;
  };
  CF.aiUsedThisMonth = function () {
    var k = "cf-ai-quota:" + CF.perioadaCurenta();
    return parseInt(localStorage.getItem(k) || "0", 10);
  };
  CF.aiConsume = function () {
    var k = "cf-ai-quota:" + CF.perioadaCurenta();
    var n = CF.aiUsedThisMonth() + 1;
    try { localStorage.setItem(k, String(n)); } catch (e) {}
    return n;
  };

  root.CF = Object.assign(root.CF || {}, CF);
})(typeof window !== "undefined" ? window : this);
