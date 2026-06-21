/* Clubul Financiar — UX articol: progres citire, cuprins, articole conexe, share, marcare citit */
(function () {
  const art = document.querySelector("article.article");
  if (!art) return;

  const h1 = art.querySelector("h1");
  const titleText = h1 ? h1.textContent.trim() : document.title;
  const slug = decodeURIComponent(location.pathname.split("/").pop().replace(/\.html$/, ""));

  // ---------- gating premium (preview + lock, SEO-safe: conținutul rămâne în DOM) ----------
  (function () {
    if (art.getAttribute("data-premium") !== "1" || window.cfPremium) return;
    const disc = art.querySelector(".disc");
    if (!h1 || !disc) return;
    const nodes = []; let nn = h1.nextElementSibling;
    while (nn && nn !== disc) { nodes.push(nn); nn = nn.nextElementSibling; }
    if (nodes.length < 4) return;
    let total = 0; nodes.forEach(x => total += (x.textContent || "").length);
    let acc = 0, cut = nodes.length;
    for (let i = 0; i < nodes.length; i++) { acc += (nodes[i].textContent || "").length; if (i >= 1 && acc >= total * 0.25) { cut = i + 1; break; } }
    const heads = [];
    for (let j = cut; j < nodes.length; j++) { if (/^H[23]$/.test(nodes[j].tagName)) { const h = nodes[j].textContent.trim(); if (h) heads.push(h); } }
    const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    const st = document.createElement("style");
    st.textContent = "article.cf-locked .premium-rest{display:none}.premium-gate{position:relative;margin:0 0 10px;text-align:center}.premium-gate .pg-fade{height:90px;margin-top:-110px;margin-bottom:20px;background:linear-gradient(transparent,var(--bg));pointer-events:none;position:relative}.premium-gate .pg-card{border:1px solid color-mix(in srgb,var(--gold) 42%,var(--border));background:linear-gradient(180deg,color-mix(in srgb,var(--gold) 9%,var(--card)),var(--card));border-radius:18px;padding:28px 24px;box-shadow:var(--shadow-lg)}.premium-gate h2{font-size:1.4rem;margin:8px 0 6px}.premium-gate .pg-list{list-style:none;padding:0;margin:12px auto 16px;max-width:430px;text-align:left}.premium-gate .pg-list li{padding:7px 0 7px 26px;position:relative;color:var(--muted)}.premium-gate .pg-list li::before{content:'🔒';position:absolute;left:0;font-size:.82rem}.premium-gate .price-line{color:var(--gold);font-weight:800;margin:10px 0 14px}";
    document.head.appendChild(st);
    const rest = document.createElement("div"); rest.className = "premium-rest";
    for (let k = cut; k < nodes.length; k++) rest.appendChild(nodes[k]);
    const gate = document.createElement("div"); gate.className = "premium-gate";
    gate.innerHTML = '<div class="pg-fade"></div><div class="pg-card"><span class="cf-premium-badge">Premium</span><h2>Restul lecției e în Premium</h2>' +
      (heads.length ? '<p style="color:var(--muted)">Ce mai afli în această lecție:</p><ul class="pg-list">' + heads.slice(0, 6).map(h => '<li>' + esc(h) + '</li>').join("") + '</ul>' : '<p style="color:var(--muted)">Deblochează lecția completă + toate cele 500 + teste.</p>') +
      '<p class="price-line">Toate cele 1000 de lecții + teste + instrumente — 49 lei/lună</p><a class="btn btn-primary" href="/premium.html">Deblochează cu Premium</a><p style="margin-top:10px;font-size:.85rem"><a href="/login.html" style="color:var(--emerald-link)">Ai cont Premium? Conectează-te</a></p></div>';
    disc.parentNode.insertBefore(gate, disc);
    disc.parentNode.insertBefore(rest, disc);
    art.classList.add("cf-locked");
    window.addEventListener("cf-auth", function () {
      if (window.cfPremium) { art.classList.remove("cf-locked"); while (rest.firstChild) disc.parentNode.insertBefore(rest.firstChild, rest); gate.remove(); rest.remove(); }
    });
  })();

  // ---------- bară de progres ----------
  const bar = document.createElement("div");
  bar.className = "read-progress";
  document.body.appendChild(bar);
  function onScroll() {
    const total = document.documentElement.scrollHeight - window.innerHeight;
    const p = total > 0 ? (window.scrollY / total) * 100 : 0;
    bar.style.width = Math.min(100, Math.max(0, p)) + "%";
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // ---------- slugify pentru id-uri ----------
  function slugify(s) {
    return s.toLowerCase()
      .replace(/[ăâ]/g, "a").replace(/î/g, "i").replace(/ș|ş/g, "s").replace(/ț|ţ/g, "t")
      .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 50);
  }

  // ---------- cuprins (din h2/h3, fără titlul duplicat) ----------
  const heads = [...art.querySelectorAll("h2, h3")].filter(h => {
    const t = h.textContent.trim();
    return t && t.toLowerCase() !== titleText.toLowerCase() && t.toLowerCase() !== "pe scurt";
  });
  if (heads.length >= 3) {
    const used = {};
    const items = heads.map(h => {
      let id = slugify(h.textContent);
      if (!id) id = "sectiune";
      if (used[id]) { used[id]++; id += "-" + used[id]; } else { used[id] = 1; }
      h.id = id;
      const lvl = h.tagName === "H3" ? " toc-sub" : "";
      return `<li class="${lvl}"><a href="#${id}">${h.textContent.trim()}</a></li>`;
    }).join("");
    const toc = document.createElement("nav");
    toc.className = "toc";
    toc.innerHTML = `<p class="toc-h">Cuprins</p><ul>${items}</ul>`;
    if (h1 && h1.nextSibling) art.insertBefore(toc, h1.nextSibling);
    else art.insertBefore(toc, art.firstChild);
  }

  // ---------- bară acțiuni: marchează citit + share ----------
  const url = location.href.split("#")[0];
  const enc = encodeURIComponent;
  const READ_KEY = "cf-read";
  function getRead() { try { return JSON.parse(localStorage.getItem(READ_KEY) || "[]"); } catch (e) { return []; } }
  function isRead() { return getRead().includes(slug); }
  function setRead(v) {
    let a = getRead();
    if (v && !a.includes(slug)) a.push(slug);
    if (!v) a = a.filter(s => s !== slug);
    localStorage.setItem(READ_KEY, JSON.stringify(a));
  }
  const actions = document.createElement("div");
  actions.className = "art-actions";
  actions.innerHTML = `
    <button class="read-btn" id="readBtn">${isRead() ? "✓ Citit" : "Marchează ca citit"}</button>
    <div class="share-row">
      <span>Distribuie:</span>
      <a href="https://www.facebook.com/sharer/sharer.php?u=${enc(url)}" target="_blank" rel="noopener" title="Facebook" aria-label="Distribuie pe Facebook">f</a>
      <a href="https://x.com/intent/tweet?url=${enc(url)}&text=${enc(titleText)}" target="_blank" rel="noopener" title="X" aria-label="Distribuie pe X">𝕏</a>
      <a href="https://api.whatsapp.com/send?text=${enc(titleText + " " + url)}" target="_blank" rel="noopener" title="WhatsApp" aria-label="Distribuie pe WhatsApp">W</a>
      <a href="https://t.me/share/url?url=${enc(url)}&text=${enc(titleText)}" target="_blank" rel="noopener" title="Telegram" aria-label="Distribuie pe Telegram">✈</a>
      <button id="copyBtn" title="Copiază linkul" aria-label="Copiază linkul">🔗</button>
    </div>`;
  const disc = art.querySelector(".disc");
  if (disc) art.insertBefore(actions, disc); else art.appendChild(actions);
  const readBtn = actions.querySelector("#readBtn");
  if (isRead()) readBtn.classList.add("done");
  readBtn.onclick = () => {
    const now = !isRead();
    setRead(now);
    readBtn.textContent = now ? "✓ Citit" : "Marchează ca citit";
    readBtn.classList.toggle("done", now);
  };
  const copyBtn = actions.querySelector("#copyBtn");
  copyBtn.onclick = () => {
    navigator.clipboard && navigator.clipboard.writeText(url).then(() => {
      copyBtn.textContent = "✓"; setTimeout(() => copyBtn.textContent = "🔗", 1500);
    });
  };

  // ---------- articole conexe (aceeași categorie) ----------
  fetch("/search-index.json").then(r => r.json()).then(idx => {
    const me = idx.find(a => a.s === slug);
    if (!me) return;
    let pool = idx.filter(a => a.c === me.c && a.s !== slug);
    // amestec determinist-ish pe baza slug-ului
    for (let i = pool.length - 1; i > 0; i--) {
      const j = (slug.charCodeAt(i % slug.length) + i) % (i + 1);
      [pool[i], pool[j]] = [pool[j], pool[i]];
    }
    const pick = pool.slice(0, 3);
    if (!pick.length) return;
    const rel = document.createElement("section");
    rel.className = "related";
    const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    rel.innerHTML = `<h2 class="title" style="font-size:1.4rem">Articole conexe</h2><div class="related-grid">${
      pick.map(a => `<a class="card" href="/articole/${encodeURIComponent(a.s)}.html"><h3>${esc(a.t)}</h3><p>${esc(a.d || "")}</p><span class="more">Citește</span></a>`).join("")
    }</div>`;
    art.appendChild(rel);
  }).catch(() => {});

  // ---------- navigare capitol (prev/next cu nume) + test după lecție ----------
  (function () {
    var esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    var st = document.createElement("style");
    st.textContent = ".lesson-nav{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:30px 0}.lnav{display:block;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 16px;transition:.15s}.lnav:hover{border-color:var(--emerald);transform:translateY(-2px)}.lnav span{display:block;color:var(--muted);font-size:.78rem;font-weight:700}.lnav b{display:block;font-size:.95rem;margin-top:3px;color:var(--text)}.lnav.next{text-align:right}@media(max-width:560px){.lesson-nav{grid-template-columns:1fr}.lnav.next{text-align:left}}.lesson-quiz{background:linear-gradient(135deg,color-mix(in srgb,var(--emerald) 10%,var(--card)),var(--card));border:1px solid color-mix(in srgb,var(--emerald) 30%,var(--border));border-radius:16px;padding:22px;margin:34px 0 10px;text-align:center}.lq-q{font-size:1.15rem;font-weight:800;font-family:var(--font-display);margin:10px 0 16px;text-align:left}.lq-opt{display:block;width:100%;text-align:left;background:var(--card);border:2px solid var(--border);border-radius:12px;padding:13px 16px;margin-bottom:10px;font:inherit;font-size:1rem;cursor:pointer;transition:.15s}.lq-opt:hover:not(:disabled){border-color:var(--emerald)}.lq-opt.ok{border-color:var(--emerald);background:color-mix(in srgb,var(--emerald) 14%,var(--card))}.lq-opt.no{border-color:#e25555;background:color-mix(in srgb,#e25555 12%,var(--card))}.lq-ex{display:none;background:var(--bg-soft);border-left:4px solid var(--emerald);border-radius:10px;padding:12px 14px;margin:4px 0 14px;text-align:left;font-size:.92rem}.lq-ex.show{display:block}.lq-prog{color:var(--muted);font-weight:700;font-size:.85rem;text-align:left;margin-bottom:6px}.lq-big{font-size:2.4rem;font-weight:900;background:var(--grad);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}.article .gloss-link{color:var(--emerald-link);font-weight:600;text-decoration:underline;text-decoration-color:color-mix(in srgb,var(--emerald) 40%,transparent);text-underline-offset:2px}.article .gloss-link:hover{text-decoration-color:var(--emerald)}.lesson-intro{background:linear-gradient(135deg,color-mix(in srgb,var(--emerald) 8%,var(--card)),var(--card));border:1px solid color-mix(in srgb,var(--emerald) 28%,var(--border));border-radius:14px;padding:14px 18px;margin:14px 0 22px}.li-step{font-size:.82rem;font-weight:800;color:var(--emerald-link,var(--emerald));letter-spacing:.01em}.li-bar{height:6px;border-radius:999px;background:var(--bg-soft2,rgba(0,0,0,.06));overflow:hidden;margin:8px 0}.li-bar i{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,var(--emerald),var(--blue,#2563eb))}.li-hook{margin:6px 0 0;font-size:1.02rem;line-height:1.5;color:var(--text)}";
    document.head.appendChild(st);

    fetch("/assets/manual-order.json").then(r => r.json()).then(ord => {
      var e = ord[slug]; if (!e) return;
      // ---- FIR: pasul X din Y în domeniu + bară progres + intro captivantă (hook) ----
      var DOMN={buget:"Buget",economii:"Economisire",datorii:"Scăpat de datorii",venituri:"Venituri",psihologie:"Psihologia banilor",credite:"Credite",asigurari:"Asigurări",planificare:"Planificare financiară",investitii:"Investiții",pensii:"Pensii",fire:"Libertate financiară (FIRE)",imobiliare:"Imobiliare",crypto:"Crypto",taxe:"Taxe & fiscalitate",antreprenoriat:"Antreprenoriat",economie:"Economie",siguranta:"Siguranță financiară"};
      var _dom=DOMN[e.d]||e.d, _pct=e.tot?Math.round(e.i/e.tot*100):0;
      var _intro=document.createElement("div"); _intro.className="lesson-intro";
      _intro.innerHTML='<div class="li-step">📍 <b>'+esc(_dom)+'</b> · Pasul '+e.i+' din '+e.tot+'</div>'+
        '<div class="li-bar"><i style="width:'+_pct+'%"></i></div>'+
        '<p class="li-hook" id="liHook" style="display:none"></p>';
      if(h1 && h1.nextSibling) art.insertBefore(_intro,h1.nextSibling); else art.insertBefore(_intro,art.firstChild);
      fetch("/assets/lesson-intros.json").then(function(r){return r.json();}).then(function(hk){
        var t=hk[slug]; var lh=document.getElementById("liHook");
        if(t && lh){ lh.innerHTML="✨ "+esc(t); lh.style.display="block"; }
      }).catch(function(){});
      // test după lecție
      var box = document.createElement("section"); box.className = "lesson-quiz";
      box.innerHTML = '<div id="lqStart"><p class="eyebrow">Testează-te</p><h2 style="font-size:1.3rem;margin:4px 0 10px">Ai înțeles lecția? Verifică în 10 întrebări.</h2><button class="btn btn-primary" id="lqBtn">Începe testul</button></div><div id="lqRun"></div>';
      // testul + navigarea trebuie să apară DEASUPRA disclaimerului „⚠️ Conținut educativ"
      var _disc = art.querySelector(".disc");
      if (_disc) art.insertBefore(box, _disc); else art.appendChild(box);
      // prev / next (cu nume)
      var nav = document.createElement("nav"); nav.className = "lesson-nav";
      nav.innerHTML =
        (e.p ? '<a class="lnav prev" href="/articole/' + encodeURIComponent(e.p[0]) + '.html"><span>← Lecția anterioară</span><b>' + esc(e.p[1]) + '</b></a>'
             : '<a class="lnav prev" href="/manual/' + e.d + '.html"><span>← Înapoi la</span><b>Capitol</b></a>') +
        (e.n ? '<a class="lnav next" href="/articole/' + encodeURIComponent(e.n[0]) + '.html"><span>Lecția următoare →</span><b>' + esc(e.n[1]) + '</b></a>'
             : '<a class="lnav next" href="/teste.html?d=' + e.d + '"><span>Testul capitolului →</span><b>Recapitulare</b></a>');
      if (_disc) art.insertBefore(nav, _disc); else art.appendChild(nav);

      fetch("/assets/quiz/d/" + e.d + ".json").then(r => r.json()).then(qd => {
        var qs = (qd[slug] && qd[slug].q) || [];
        if (!qs.length) { box.style.display = "none"; return; }
        document.getElementById("lqBtn").onclick = () => runQuiz(qs);
      }).catch(() => { box.style.display = "none"; });

      function runQuiz(qs) {
        var i = 0, correct = 0, prem = !!window.cfPremium;
        var run = document.getElementById("lqRun"); document.getElementById("lqStart").style.display = "none";
        function q() {
          if (i >= qs.length) return done();
          var it = qs[i];
          run.innerHTML = '<div class="lq-prog">' + (i + 1) + ' / ' + qs.length + '</div><div class="lq-q">' + esc(it.q) + '</div>' +
            it.options.map((o, k) => '<button class="lq-opt" data-k="' + k + '">' + esc(o) + '</button>').join("") +
            '<div class="lq-ex" id="lqEx"></div><button class="btn btn-primary" id="lqNext" style="display:none;width:100%;justify-content:center">Continuă</button>';
          run.querySelectorAll(".lq-opt").forEach(b => b.onclick = () => ans(b, it));
        }
        function ans(b, it) {
          var opts = run.querySelectorAll(".lq-opt"); opts.forEach(o => o.disabled = true);
          var ok = +b.dataset.k === it.correct; opts[it.correct].classList.add("ok"); if (!ok) b.classList.add("no");
          if (ok) { correct++; if (prem) { try { localStorage.setItem("cf-qz-xp", parseInt(localStorage.getItem("cf-qz-xp") || "0", 10) + 10); } catch (e) {} } }
          var ex = document.getElementById("lqEx"); ex.innerHTML = (ok ? "✓ Corect! " : "✗ ") + esc(it.explain || ""); ex.classList.add("show");
          var nx = document.getElementById("lqNext"); nx.style.display = "inline-flex"; nx.textContent = (i + 1 >= qs.length) ? "Vezi rezultatul" : "Continuă"; nx.onclick = () => { i++; q(); };
        }
        function done() {
          var pct = Math.round(correct / qs.length * 100);
          run.innerHTML = '<div class="lq-big">' + pct + '%</div><p style="color:var(--muted)">' + correct + ' din ' + qs.length + ' corecte.' + (prem ? ' +' + (correct * 10) + ' XP' : '') + '</p>' +
            (prem ? '' : '<p style="font-size:.9rem;margin-top:8px">Cu <a href="/premium.html" style="color:var(--emerald-link);font-weight:700">Premium</a> îți ții seria zilnică, aduni XP și primești certificate.</p>') +
            '<button class="btn btn-ghost" id="lqAgain" style="margin-top:12px">Încă o dată</button>';
          document.getElementById("lqAgain").onclick = () => runQuiz(qs);
        }
        q();
      }
    }).catch(() => {});
  })();
})();
