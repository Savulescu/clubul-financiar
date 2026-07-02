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
    st.textContent = "article.cf-locked .premium-rest{display:none}.premium-gate{position:relative;margin:0 0 10px;text-align:center}.premium-gate .pg-fade{height:90px;margin-top:-110px;margin-bottom:20px;background:linear-gradient(transparent,var(--u-bg1,var(--bg)));pointer-events:none;position:relative}.premium-gate .pg-card{border:1px solid color-mix(in srgb,var(--gold) 42%,var(--border));background:linear-gradient(180deg,color-mix(in srgb,var(--gold) 9%,var(--card)),var(--card));border-radius:18px;padding:28px 24px;box-shadow:var(--shadow-lg)}.premium-gate h2{font-size:1.4rem;margin:8px 0 6px}.premium-gate .pg-list{list-style:none;padding:0;margin:12px auto 16px;max-width:430px;text-align:left}.premium-gate .pg-list li{padding:7px 0 7px 26px;position:relative;color:var(--muted)}.premium-gate .pg-list li::before{content:url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='13' height='13'><path fill='%23b08a2e' d='M12 2a5 5 0 0 0-5 5v3H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8a2 2 0 0 0-2-2h-1V7a5 5 0 0 0-5-5zm-3 8V7a3 3 0 1 1 6 0v3H9z'/></svg>\");position:absolute;left:0;top:9px}.premium-gate .price-line{color:var(--gold-ink,var(--gold));font-weight:800;margin:10px 0 14px}";
    document.head.appendChild(st);
    const rest = document.createElement("div"); rest.className = "premium-rest";
    for (let k = cut; k < nodes.length; k++) rest.appendChild(nodes[k]);
    const gate = document.createElement("div"); gate.className = "premium-gate"; gate.id = "premium-gate";
    gate.innerHTML = '<div class="pg-fade"></div><div class="pg-card"><span class="cf-premium-badge">Premium</span><h2>Restul lecției e în Premium</h2>' +
      (heads.length ? '<p style="color:var(--muted)">Ce mai afli în această lecție:</p><ul class="pg-list">' + heads.slice(0, 6).map(h => '<li>' + esc(h) + '</li>').join("") + '</ul>' : '<p style="color:var(--muted)">Deblochează lecția completă + toate cele 1000 + teste.</p>') +
      '<p class="price-line">Toate cele 1000 de lecții + teste + instrumente — 49 lei/lună</p><a class="btn btn-primary" href="/premium">Deblochează cu Premium</a><p style="margin-top:10px;font-size:.85rem"><a href="/login" style="color:var(--emerald-link)">Ai cont Premium? Conectează-te</a></p></div>';
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
  let ticking = false, sh = document.documentElement.scrollHeight;
  function onScroll() {
    ticking = false;
    const total = sh - window.innerHeight;
    const p = total > 0 ? (window.scrollY / total) * 100 : 0;
    bar.style.width = Math.min(100, Math.max(0, p)) + "%";
  }
  window.addEventListener("scroll", () => { if (!ticking) { requestAnimationFrame(onScroll); ticking = true; } }, { passive: true });
  window.addEventListener("resize", () => { sh = document.documentElement.scrollHeight; onScroll(); }, { passive: true });
  onScroll();

  // ---------- slugify pentru id-uri ----------
  function slugify(s) {
    return s.toLowerCase()
      .replace(/[ăâ]/g, "a").replace(/î/g, "i").replace(/ș|ş/g, "s").replace(/ț|ţ/g, "t")
      .replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 50);
  }

  // ---------- cuprins (din h2/h3, fără titlul duplicat și fără cardul de gating) ----------
  const LOCK_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a5 5 0 0 0-5 5v3H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8a2 2 0 0 0-2-2h-1V7a5 5 0 0 0-5-5zm-3 8V7a3 3 0 1 1 6 0v3H9z"/></svg>';
  const heads = [...art.querySelectorAll("h2, h3")].filter(h => {
    if (h.closest("[data-cf-related]") || h.closest(".premium-gate")) return false; // nu include conexe/cardul Premium
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
      const locked = !!h.closest(".premium-rest");
      const lvl = (h.tagName === "H3" ? " toc-sub" : "") + (locked ? " toc-lock" : "");
      return `<li class="${lvl.trim()}"><a href="#${id}">${h.textContent.trim()}${locked ? LOCK_SVG : ""}</a></li>`;
    }).join("");
    const toc = document.createElement("nav");
    toc.className = "toc";
    toc.innerHTML = `<p class="toc-h">Cuprins</p><ul>${items}</ul>`;
    // secțiunile blocate: cât timp articolul e blocat, cuprinsul duce la cardul Premium
    // (după deblocare, id-urile redevin ancore normale — aceleași elemente revin în flux)
    toc.addEventListener("click", function (ev) {
      const a = ev.target.closest("a"); if (!a) return;
      const target = document.getElementById(decodeURIComponent((a.getAttribute("href") || "").slice(1)));
      if (target && target.closest(".premium-rest") && art.classList.contains("cf-locked")) {
        ev.preventDefault();
        const gate = document.getElementById("premium-gate");
        if (gate) gate.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    });
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
  // iconuri brand SVG (aceleași path-uri ca în footer) + WhatsApp + link
  const IC = {
    fb: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z"/></svg>',
    x: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z"/></svg>',
    wa: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413Z"/></svg>',
    tg: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>',
    ln: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
    ok: '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>',
  };
  actions.innerHTML = `
    <button class="read-btn" id="readBtn">${isRead() ? "✓ Citit" : "Marchează ca citit"}</button>
    <div class="share-row">
      <span>Distribuie:</span>
      <a href="https://www.facebook.com/sharer/sharer.php?u=${enc(url)}" target="_blank" rel="noopener" title="Facebook" aria-label="Distribuie pe Facebook">${IC.fb}</a>
      <a href="https://x.com/intent/tweet?url=${enc(url)}&text=${enc(titleText)}" target="_blank" rel="noopener" title="X" aria-label="Distribuie pe X">${IC.x}</a>
      <a href="https://api.whatsapp.com/send?text=${enc(titleText + " " + url)}" target="_blank" rel="noopener" title="WhatsApp" aria-label="Distribuie pe WhatsApp">${IC.wa}</a>
      <a href="https://t.me/share/url?url=${enc(url)}&text=${enc(titleText)}" target="_blank" rel="noopener" title="Telegram" aria-label="Distribuie pe Telegram">${IC.tg}</a>
      <button id="copyBtn" title="Copiază linkul" aria-label="Copiază linkul">${IC.ln}</button>
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
      copyBtn.innerHTML = IC.ok; setTimeout(() => copyBtn.innerHTML = IC.ln, 1500);
    });
  };

  // ---------- articole conexe — server-side (semantic) dacă există, altfel fallback client-side ----------
  if (!art.querySelector("[data-cf-related]")) fetch("/search-index.json").then(r => r.json()).then(idx => {
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
      pick.map(a => `<a class="card" href="/articole/${encodeURIComponent(a.s)}"><h3>${esc(a.t)}</h3><p>${esc(a.d || "")}</p><span class="more">Citește</span></a>`).join("")
    }</div>`;
    art.appendChild(rel);
  }).catch(() => {});

  // ---------- navigare capitol (prev/next cu nume) + test după lecție ----------
  (function () {
    var esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    var st = document.createElement("style");
    st.textContent = ".lesson-nav{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:30px 0}.lnav{display:block;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 16px;transition:.15s}.lnav:hover{border-color:var(--emerald);transform:translateY(-2px)}.lnav span{display:block;color:var(--muted);font-size:.78rem;font-weight:700}.lnav b{display:block;font-size:.95rem;margin-top:3px;color:var(--text)}.lnav.next{text-align:right}@media(max-width:560px){.lesson-nav{grid-template-columns:1fr}.lnav.next{text-align:left}}.lesson-quiz{background:linear-gradient(135deg,color-mix(in srgb,var(--emerald) 10%,var(--card)),var(--card));border:1px solid color-mix(in srgb,var(--emerald) 30%,var(--border));border-radius:16px;padding:22px;margin:34px 0 10px;text-align:center}.lq-q{font-size:1.15rem;font-weight:800;font-family:var(--font-display);margin:10px 0 16px;text-align:left}.lq-opt{display:block;width:100%;text-align:left;background:var(--card);border:2px solid var(--border);border-radius:12px;padding:13px 16px;margin-bottom:10px;font:inherit;font-size:1rem;cursor:pointer;transition:.15s}.lq-opt:hover:not(:disabled){border-color:var(--emerald)}.lq-opt.ok{border-color:var(--emerald);background:color-mix(in srgb,var(--emerald) 14%,var(--card))}.lq-opt.no{border-color:#e25555;background:color-mix(in srgb,#e25555 12%,var(--card))}.lq-ex{display:none;background:var(--bg-soft);border-left:4px solid var(--emerald);border-radius:10px;padding:12px 14px;margin:4px 0 14px;text-align:left;font-size:.92rem}.lq-ex.show{display:block}.lq-prog{color:var(--muted);font-weight:700;font-size:.85rem;text-align:left;margin-bottom:6px}.lq-big{font-size:2.4rem;font-weight:900;background:var(--grad);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}.article .gloss-link{color:var(--emerald-link);font-weight:600;text-decoration:underline;text-decoration-color:color-mix(in srgb,var(--emerald) 40%,transparent);text-underline-offset:2px}.article .gloss-link:hover{text-decoration-color:var(--emerald)}.lesson-intro{background:linear-gradient(135deg,color-mix(in srgb,var(--emerald) 8%,var(--card)),var(--card));border:1px solid color-mix(in srgb,var(--emerald) 28%,var(--border));border-radius:14px;padding:14px 18px;margin:14px 0 22px}.li-step{font-size:.82rem;font-weight:800;color:var(--emerald-link,var(--emerald));letter-spacing:.01em}.li-bar{height:6px;border-radius:999px;background:var(--bg-soft2,rgba(0,0,0,.06));overflow:hidden;margin:8px 0}.li-bar i{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,var(--emerald),var(--blue,#2563eb))}.li-hook{margin:6px 0 0;font-size:1.02rem;line-height:1.5;color:var(--text)}";
    document.head.appendChild(st);

    // ---- INTRO LECȚIE: hook captivant (TOATE lecțiile cu intro) + pas X/Y (doar cele din manual) ----
    // Datele sunt injectate in-place per-articol în window.__cfLesson (script de injecție),
    // ca să nu mai descărcăm lesson-intros.json + manual-order.json (~312KB) pe fiecare pagină.
    var __cf = window.__cfLesson || {};
    var hook = __cf.hook, e = __cf.e;
    (function () {
      if (!hook && !e) return;
      var DOMN = { buget:"Buget",economii:"Economisire",datorii:"Scăpat de datorii",venituri:"Venituri",psihologie:"Psihologia banilor",credite:"Credite",asigurari:"Asigurări",planificare:"Planificare financiară",investitii:"Investiții",pensii:"Pensii",fire:"Libertate financiară (FIRE)",imobiliare:"Imobiliare",crypto:"Crypto",taxe:"Taxe & fiscalitate",antreprenoriat:"Antreprenoriat",economie:"Economie",siguranta:"Siguranță financiară" };
      var html = "";
      if (e) { var dom = DOMN[e.d] || e.d, pct = e.tot ? Math.round(e.i / e.tot * 100) : 0;
        html += '<div class="li-step"><b>' + esc(dom) + '</b> · Pasul ' + e.i + ' din ' + e.tot + '</div>' +
                '<div class="li-bar"><i style="width:' + pct + '%"></i></div>'; }
      if (hook) { html += '<p class="li-hook">' + esc(hook) + '</p>'; }
      var box = document.createElement("div"); box.className = "lesson-intro"; box.innerHTML = html;
      if (h1 && h1.nextSibling) art.insertBefore(box, h1.nextSibling); else art.insertBefore(box, art.firstChild);
    })();

    (function () {
      if (!e) return;
      // test după lecție
      var box = document.createElement("section"); box.className = "lesson-quiz";
      box.innerHTML = '<div id="lqStart"><p class="eyebrow">Testează-te</p><h2 style="font-size:1.3rem;margin:4px 0 10px">Ai înțeles lecția? Verifică în 10 întrebări.</h2><button class="btn btn-primary" id="lqBtn">Începe testul</button></div><div id="lqRun"></div>';
      // testul + navigarea trebuie să apară DEASUPRA disclaimerului „⚠️ Conținut educativ"
      var _disc = art.querySelector(".disc");
      if (_disc) art.insertBefore(box, _disc); else art.appendChild(box);
      // prev / next (cu nume)
      var nav = document.createElement("nav"); nav.className = "lesson-nav";
      nav.innerHTML =
        (e.p ? '<a class="lnav prev" href="/articole/' + encodeURIComponent(e.p[0]) + '"><span>← Lecția anterioară</span><b>' + esc(e.p[1]) + '</b></a>'
             : '<a class="lnav prev" href="/manual/' + e.d + '"><span>← Înapoi la</span><b>Capitol</b></a>') +
        (e.n ? '<a class="lnav next" href="/articole/' + encodeURIComponent(e.n[0]) + '"><span>Lecția următoare →</span><b>' + esc(e.n[1]) + '</b></a>'
             : '<a class="lnav next" href="/teste?d=' + e.d + '"><span>Testul capitolului →</span><b>Recapitulare</b></a>');
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
            (prem ? '' : '<p style="font-size:.9rem;margin-top:8px">Cu <a href="/premium" style="color:var(--emerald-link);font-weight:700">Premium</a> îți ții seria zilnică, aduni XP și primești certificate.</p>') +
            '<button class="btn btn-ghost" id="lqAgain" style="margin-top:12px">Încă o dată</button>';
          document.getElementById("lqAgain").onclick = () => runQuiz(qs);
        }
        q();
      }
    })();
  })();
})();
