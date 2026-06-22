/* Clubul Financiar — navbar + footer + theme + auth (injectate pe toate paginile) */
(function () {
  const SB_URL = "https://maumjqciuxdbwjtvcpsy.supabase.co";
  const SB_KEY = "sb_publishable_N6X3B_Sn7oWkxJF-iHCfbg__w4J7ONR";
  const sb = window.supabase ? window.supabase.createClient(SB_URL, SB_KEY) : null;
  window._sb = sb;

  // escape HTML — folosit oriunde băgăm text în innerHTML (anti-XSS)
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g,
    c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  const NAV = [
    ["Prezentare", "/incepe-aici.html"],
    ["Învață", "/educatie.html"],
    ["Masterclass", "/masterclass.html"],
    ["Calculatoare", "/calculatoare.html"],
    ["Instrumente", "/instrumente.html"],
    ["Feedback", "/feedback.html"],
    ["Știri", "/stiri.html"],
    ["Premium", "/premium.html"],
  ];
  const SOC = [
    ["Instagram","https://www.instagram.com/clubulfinanciar"],["TikTok","https://www.tiktok.com/@clubulfinanciar"],
    ["YouTube","https://www.youtube.com/@clubulfinanciar"],["Facebook","https://www.facebook.com/clubulfinanciar"],
    ["Threads","https://www.threads.net/@clubulfinanciar"],["X","https://x.com/clubulfinanciar"],
    ["Telegram","https://t.me/clubul_financiar"],
  ];
  const SOC_ICONS = {
    "instagram": "<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077\"/></svg>",
    "tiktok": "<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z\"/></svg>",
    "youtube": "<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z\"/></svg>",
    "facebook": "<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z\"/></svg>",
    "threads": "<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M12.186 24h-.007c-3.581-.024-6.334-1.205-8.184-3.509C2.35 18.44 1.5 15.586 1.472 12.01v-.017c.03-3.579.879-6.43 2.525-8.482C5.845 1.205 8.6.024 12.18 0h.014c2.746.02 5.043.725 6.826 2.098 1.677 1.29 2.858 3.13 3.509 5.467l-2.04.569c-1.104-3.96-3.898-5.984-8.304-6.015-2.91.022-5.11.936-6.54 2.717C4.307 6.504 3.616 8.914 3.589 12c.027 3.086.718 5.496 2.057 7.164 1.43 1.783 3.631 2.698 6.54 2.717 2.623-.02 4.358-.631 5.8-2.045 1.647-1.613 1.618-3.593 1.09-4.798-.31-.71-.873-1.3-1.634-1.75-.192 1.352-.622 2.446-1.284 3.272-.886 1.102-2.14 1.704-3.73 1.79-1.202.065-2.361-.218-3.259-.801-1.063-.689-1.685-1.74-1.752-2.964-.065-1.19.408-2.285 1.33-3.082.88-.76 2.119-1.207 3.583-1.291a13.853 13.853 0 0 1 3.02.142c-.126-.742-.375-1.332-.75-1.757-.513-.586-1.308-.883-2.359-.89h-.029c-.844 0-1.992.232-2.721 1.32L7.734 7.847c.98-1.454 2.568-2.256 4.478-2.256h.044c3.194.02 5.097 1.975 5.287 5.388.108.046.216.094.321.142 1.49.7 2.58 1.761 3.154 3.07.797 1.82.871 4.79-1.548 7.158-1.85 1.81-4.094 2.628-7.277 2.65Zm1.003-11.69c-.242 0-.487.007-.739.021-1.836.103-2.98.946-2.916 2.143.067 1.256 1.452 1.839 2.784 1.767 1.224-.065 2.818-.543 3.086-3.71a10.5 10.5 0 0 0-2.215-.221z\"/></svg>",
    "x": "<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M14.234 10.162 22.977 0h-2.072l-7.591 8.824L7.251 0H.258l9.168 13.343L.258 24H2.33l8.016-9.318L16.749 24h6.993zm-2.837 3.299-.929-1.329L3.076 1.56h3.182l5.965 8.532.929 1.329 7.754 11.09h-3.182z\"/></svg>",
    "telegram": "<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z\"/></svg>"
  };

  // ---- theme ----
  const saved = localStorage.getItem("cf-theme");
  if (saved) document.documentElement.setAttribute("data-theme", saved);
  function toggleTheme(){
    const cur = document.documentElement.getAttribute("data-theme")==="dark"?"":"dark";
    if(cur) document.documentElement.setAttribute("data-theme",cur); else document.documentElement.removeAttribute("data-theme");
    localStorage.setItem("cf-theme",cur);
    document.querySelectorAll(".theme-ic").forEach(e=>e.textContent=cur==="dark"?"☀️":"🌙");
  }

  // ---- navbar (hidratează dacă e pre-randat static în HTML, altfel îl creează) ----
  if (!document.querySelector("header.nav")) {
  const nav = document.createElement("header");
  nav.className = "nav";
  nav.innerHTML = `<div class="container nav-in">
    <a class="brand-logo" href="/index.html"><img class="brand-img" src="/icon-64.png" alt="Clubul Financiar" width="34" height="34"> <span class="brand-txt">Clubul Financiar</span></a>
    <nav class="nav-links" id="navLinks">${NAV.map(([t,h])=>`<a href="${h}"${t==="Ultra"?' style="color:#E8C268;font-weight:700"':""}>${t}</a>`).join("")}</nav>
    <div class="nav-right">
      <button class="icon-btn" id="searchBtn" aria-label="Caută">🔍</button>
      <button class="icon-btn" id="themeBtn" aria-label="Temă"><span class="theme-ic">${document.documentElement.getAttribute("data-theme")==="dark"?"☀️":"🌙"}</span></button>
      <span id="acctSlot"></span>
      <button class="icon-btn burger" id="burger" aria-label="Meniu">☰</button>
    </div>
  </div>`;
  document.body.prepend(nav);
  }
  document.getElementById("themeBtn").onclick = toggleTheme;
  const burgerBtn = document.getElementById("burger");
  const navLinksEl = document.getElementById("navLinks");
  burgerBtn.setAttribute("aria-controls", "navLinks");
  burgerBtn.setAttribute("aria-expanded", "false");
  burgerBtn.onclick = () => {
    const open = navLinksEl.classList.toggle("open");
    burgerBtn.setAttribute("aria-expanded", open ? "true" : "false");
  };
  // închide meniul după ce alegi un link (nu mai rămâne deschis peste conținut)
  navLinksEl.addEventListener("click", e => {
    if (e.target.closest("a")) { navLinksEl.classList.remove("open"); burgerBtn.setAttribute("aria-expanded", "false"); }
  });

  // ---- căutare globală (articole + glosar) ----
  let searchIdx = null, searchLoaded = false;
  const overlay = document.createElement("div");
  overlay.className = "search-ov";
  overlay.hidden = true;
  overlay.innerHTML = `<div class="search-box">
    <div class="search-in"><span>🔍</span><input id="searchInput" type="search" placeholder="Caută articole, termeni, calculatoare…" autocomplete="off"><button id="searchClose" aria-label="Închide">✕</button></div>
    <div id="searchRes" class="search-res"><p class="search-hint">Scrie un cuvânt — ex: „inflație", „ETF", „credit ipotecar".</p></div>
  </div>`;
  document.body.appendChild(overlay);
  const sInput = overlay.querySelector("#searchInput");
  const sRes = overlay.querySelector("#searchRes");
  const norm = s => (s || "").toLowerCase().replace(/[ăâ]/g,"a").replace(/î/g,"i").replace(/ș|ş/g,"s").replace(/ț|ţ/g,"t");
  let lastFocus = null;
  function openSearch() {
    lastFocus = document.activeElement;
    overlay.hidden = false; document.body.style.overflow = "hidden"; setTimeout(() => sInput.focus(), 40);
    if (!searchLoaded) {
      searchLoaded = true;
      fetch("/search-index.json").then(r => r.json()).then(d => { searchIdx = d; runSearch(); }).catch(() => { sRes.innerHTML = `<p class="search-hint">Căutarea nu e disponibilă momentan.</p>`; });
    }
  }
  function closeSearch() { overlay.hidden = true; document.body.style.overflow = ""; if (lastFocus && lastFocus.focus) lastFocus.focus(); }
  function runSearch() {
    const q = norm(sInput.value.trim());
    if (!searchIdx) return;
    if (q.length < 2) { sRes.innerHTML = `<p class="search-hint">Scrie cel puțin 2 litere.</p>`; return; }
    const terms = q.split(/\s+/);
    const scored = [];
    for (const a of searchIdx) {
      const hay = norm((a.t || "") + " " + (a.d || "") + " " + (a.c || ""));
      let ok = true, score = 0;
      for (const t of terms) { if (!hay.includes(t)) { ok = false; break; } }
      if (!ok) continue;
      if (norm(a.t).startsWith(terms[0])) score += 10;
      if (norm(a.t).includes(q)) score += 5;
      score += (a.k === "g" ? 0 : 1);
      scored.push([score, a]);
    }
    scored.sort((x, y) => y[0] - x[0]);
    const top = scored.slice(0, 24);
    if (!top.length) { sRes.innerHTML = `<p class="search-hint">Niciun rezultat pentru „${esc(sInput.value)}".</p>`; return; }
    sRes.innerHTML = top.map(([, a]) => {
      const badge = a.k === "g" ? "Glosar" : (a.k === "calc" ? "Calculator" : (a.cn || "Articol"));
      return `<a class="search-item" href="${esc(a.u)}"><div><strong>${esc(a.t)}</strong><span class="search-badge">${esc(badge)}</span></div><p>${esc(a.d || "")}</p></a>`;
    }).join("");
  }
  document.getElementById("searchBtn").onclick = openSearch;
  window.cfOpenSearch = function (q) { openSearch(); if (q) { sInput.value = q; runSearch(); } };
  overlay.querySelector("#searchClose").onclick = closeSearch;
  overlay.addEventListener("click", e => { if (e.target === overlay) closeSearch(); });
  sInput.addEventListener("input", runSearch);
  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && !overlay.hidden) closeSearch();
    if ((e.key === "/" || (e.key === "k" && (e.metaKey || e.ctrlKey))) && overlay.hidden) {
      const tag = (document.activeElement && document.activeElement.tagName) || "";
      if (tag !== "INPUT" && tag !== "TEXTAREA" && tag !== "SELECT") { e.preventDefault(); openSearch(); }
    }
  });

  // ---- footer ----
  const cols = [
    ["Educație", [["Prezentare","/incepe-aici.html"],["Buget personal","/educatie.html"],["Economisire","/educatie.html"],["Psihologia banilor","/educatie.html"]]],
    ["Investiții", [["Bursă & acțiuni","/investitii.html"],["ETF-uri","/investitii.html"],["Titluri de stat","/investitii.html"],["Calculatoare","/calculatoare.html"]]],
    ["Platformă", [["Despre noi","/despre.html"],["Cursuri","/cursuri.html"],["Premium","/premium.html"],["Cont","/login.html"],["Contact","/contact.html"]]],
  ];
  if (!document.querySelector("footer.foot")) {
  const foot = document.createElement("footer");
  foot.className = "foot";
  foot.innerHTML = `<div class="container">
    <div class="foot-grid">
      <div>
        <a class="brand-logo" href="/index.html"><img class="brand-img" src="/icon-64.png" alt="Clubul Financiar" width="34" height="34"> <span class="brand-txt">Clubul Financiar</span></a>
        <p style="color:var(--muted);font-size:.92rem;margin-top:12px;max-width:300px">Învață banii de la zero — educație financiară pe înțelesul tuturor.</p>
        <p class="soc-h">Urmărește-ne</p><div class="soc">${SOC.map(([t,h])=>`<a href="${h}" title="${t}" aria-label="${t}" rel="noopener" target="_blank">${SOC_ICONS[t.toLowerCase()]||t[0]}</a>`).join("")}</div>
      </div>
      ${cols.map(([h,links])=>`<div><h4>${h}</h4>${links.map(([t,u])=>`<a href="${u}">${t}</a>`).join("")}</div>`).join("")}
    </div>
    <div class="foot-bottom">
      <span>© Clubul Financiar · clubulfinanciar.ro</span>
      <span><a href="/privacy.html">Confidențialitate</a> · <a href="/terms.html">Termeni</a> · Conținut educativ, nu sfat de investiții</span>
    </div>
  </div>`;
  document.body.appendChild(foot);
  }

  // ---- pe paginile premium (.u-page), nav + footer capătă accente aurii ----
  if (document.querySelector("main.u-page")) {
    document.querySelectorAll("header.nav, footer.foot").forEach(function(el){ el.classList.add("ultra"); });
  }

  // ---- redenumire „Începe aici" → „Prezentare" pe paginile statice (nav + footer) ----
  document.querySelectorAll('a[href="/incepe-aici.html"]').forEach(function(a){
    if (a.textContent.trim() === "Începe aici") a.textContent = "Prezentare";
  });

  // ---- abonare newsletter: wire ORICE formular .nl-form (banda injectată + cele din pagini) ----
  function nlGet(){ try { return JSON.parse(localStorage.getItem("cf-nl") || "null"); } catch(e){ return null; } }
  function attachNl(form){
    if (form.getAttribute("data-nl-wired")) return;
    form.setAttribute("data-nl-wired", "1");
    const inputHTML = form.innerHTML;   // starea cu input (pentru revenire la dezabonare)

    function showInput(){ form.innerHTML = inputHTML; }
    function showSubscribed(email){
      form.innerHTML =
        '<span class="nl-ok">✓ Abonat</span>' +
        (email ? '<span class="nl-sub-em">' + esc(email) + '</span>' : '') +
        '<button type="button" class="nl-unsub">Dezabonează-te</button>' +
        '<div class="nl-msg" role="status"></div>';
      form.querySelector(".nl-unsub").addEventListener("click", function(){
        const sub = nlGet(); const msg = form.querySelector(".nl-msg");
        const done = (ok, t) => { if (msg) { msg.textContent = t; msg.className = "nl-msg " + (ok ? "ok" : "err"); } };
        const clear = () => { localStorage.removeItem("cf-nl"); showInput(); };
        if (!sb || !sub || !sub.token) { clear(); return; }   // fără token (alt device) → doar curăță local
        done(true, "Se procesează…");
        sb.rpc("newsletter_unsubscribe", { token: sub.token }).then(clear, function(){ done(false, "N-a mers, încearcă din nou."); });
      });
    }

    form.addEventListener("submit", function(e){
      e.preventDefault();
      const input = form.querySelector('input[type="email"]');
      const msg = form.querySelector(".nl-msg");
      const em = ((input && input.value) || "").trim();
      const done = (ok, t) => { if (msg) { msg.textContent = t; msg.className = "nl-msg " + (ok ? "ok" : "err"); } };
      if (!em || em.indexOf("@") < 1) { done(false, "Scrie o adresă de email validă."); return; }
      done(true, "Se abonează…"); if (msg) msg.className = "nl-msg";
      if (!sb) { done(false, "Momentan indisponibil. Încearcă mai târziu."); return; }
      const token = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : (Date.now() + "" + Math.random().toString(36).slice(2));
      const ins = (uid) => sb.from("newsletter_subscribers").insert({ email: em, user_id: uid || null, source: "site", unsub_token: token }).then(function(res){
        if (res.error) {
          const m = (res.error.message || "").toLowerCase();
          if (res.error.code === "23505" || m.indexOf("duplicate") >= 0) {
            localStorage.setItem("cf-nl", JSON.stringify({ email: em, token: null })); showSubscribed(em);
          } else done(false, "N-a mers, încearcă din nou.");
        } else {
          localStorage.setItem("cf-nl", JSON.stringify({ email: em, token: token })); showSubscribed(em);
          try { sb.functions.invoke("newsletter-welcome", { body: { email: em } }); } catch(e){}  // email de bun-venit (best-effort)
        }
      }, function(){ done(false, "N-a mers, încearcă din nou."); });
      sb.auth.getSession().then(function(r){ ins(r && r.data && r.data.session && r.data.session.user && r.data.session.user.id); }, function(){ ins(null); });
    });

    // stare inițială: dacă ești deja abonat (salvat local), arată „Abonat · Dezabonează-te"
    const sub = nlGet();
    if (sub && sub.email) showSubscribed(sub.email);
  }
  // banda site-wide deasupra footer-ului (mai puțin pe login/reset/account/dezabonare)
  if (!document.querySelector(".nl-band") && !/\/(login|reset|account|dezabonare)\.html/.test(location.pathname)) {
    const band = document.createElement("section");
    band.className = "nl-band";
    band.innerHTML = `<div class="container nl-in">
      <div class="nl-tx"><div class="nl-h">📬 Dimineața pe scurt</div>
        <div class="nl-p">Știrile care-ți mișcă banii + un concept explicat simplu, în 5 minute. Gratuit, în fiecare dimineață.</div></div>
      <form class="nl-form" novalidate>
        <input type="email" placeholder="adresa ta de email" autocomplete="email" required aria-label="Email">
        <button type="submit">Abonează-mă</button>
        <div class="nl-msg" role="status"></div>
      </form></div>`;
    const ft = document.querySelector("footer.foot");
    if (ft && ft.parentNode) ft.parentNode.insertBefore(band, ft); else document.body.appendChild(band);
  }
  document.querySelectorAll("form.nl-form").forEach(attachNl);

  // ---- roluri (admin / premium / pro / ultra) ----
  const ADMIN_EMAILS = ["clubulfinanciar@gmail.com"];
  const RANK = { free:0, premium:1, pro:2, ultra:3 };
  // expune clientul + userul pentru cf-tool.js (logare Supabase cross-device)
  window.cfSupabase = sb; window.__cfSB = sb;
  function setTier(tier, email, isAdmin){
    const isPremium = RANK[tier] >= RANK.premium;
    document.body.toggleAttribute("data-cf-premium", isPremium);
    document.body.setAttribute("data-cf-tier", tier);
    document.body.toggleAttribute("data-cf-role-admin", !!isAdmin);
    window.cfTier = tier; window.cfPremium = isPremium; window.cfAdmin = !!isAdmin; window.cfEmail = email || null;
    try { window.dispatchEvent(new CustomEvent("cf-auth", { detail:{ email:email||null, tier, isPremium, isAdmin:!!isAdmin } })); } catch(e){}
  }
  function applyRole(session){
    const email = session && session.user && (session.user.email || "").toLowerCase();
    const isAdmin = !!email && ADMIN_EMAILS.includes(email);
    window.cfUserId = session && session.user ? session.user.id : null;
    // baseline sincron: admin = ultra (acces complet), altfel free până vine DB-ul
    setTier(isAdmin ? "ultra" : "free", email, isAdmin);
    // tier real din tabelul subscriptions (abonament activ, neexpirat)
    if(sb && !isAdmin && session && session.user){
      try {
        sb.from("subscriptions").select("tier,status,current_period_end")
          .eq("user_id", session.user.id).maybeSingle().then(({data})=>{
            if(data && data.status==="active" && (!data.current_period_end || new Date(data.current_period_end) > new Date())
               && RANK[data.tier] != null){
              setTier(data.tier, email, false);
            }
          }, ()=>{});
      } catch(e){}
    }
    const isPremium = isAdmin;
    return { isAdmin, isPremium };
  }

  // ---- auth account area ----
  function tierMeta(tier, isAdmin){
    if(isAdmin) return { ic:"👑", nm:"Administrator", cls:"" };
    return ({
      ultra:  { ic:"◆",  nm:"Ultra · birou privat", cls:"" },
      pro:    { ic:"🛰️", nm:"Pro · Hub Fiscal",      cls:"" },
      premium:{ ic:"⭐", nm:"Premium",               cls:"" },
      free:   { ic:"",   nm:"Cont gratuit",          cls:"free" }
    })[tier] || { ic:"", nm:"Cont gratuit", cls:"free" };
  }
  // rândurile cu planuri (dreapta în dropdown): evidențiază planul curent, marchează upgrade-urile
  function plansHTML(rank){
    const P = [["premium","⭐ Premium","49 lei"],["pro","🛰️ Pro","99 lei"],["ultra","◆ Ultra","199 lei"]];
    return P.map(function(row){
      const k=row[0], nm=row[1], pr=row[2], r=RANK[k];
      let cls,tag,href;
      if(rank > r){ cls="owned"; tag="Inclus"; href="/instrumente.html#"+k; }
      else if(rank === r){ cls="cur"; tag="Activ ✓"; href="/instrumente.html#"+k; }
      else { cls="up"; tag="Treci →"; href="/premium.html#alege"; }
      return `<a class="acct-plan ${cls}" href="${href}"><span class="pn">${nm} <span style="color:var(--muted);font-weight:600">· ${pr}</span></span><span class="pp">${tag}</span></a>`;
    }).join("");
  }
  function plansColHTML(rank){
    return `<h5>Planul tău</h5>${plansHTML(rank)}<a class="acct-manage" href="/premium.html">Gestionează abonamentul →</a>`;
  }

  function renderAcct(session){
    const { isAdmin, isPremium } = applyRole(session);
    const slot = document.getElementById("acctSlot");
    if(!slot) return;
    if(session && session.user){
      const name = session.user.email || "cont";
      const tier = isAdmin ? "ultra" : (window.cfTier || "free");
      const rank = isAdmin ? 3 : (RANK[tier] != null ? RANK[tier] : 0);
      const tm = tierMeta(isAdmin ? null : tier, isAdmin);
      const avBg = (isAdmin || tier==="ultra") ? "linear-gradient(135deg,#E8C268,#caa23f)" : "var(--grad)";
      const isDark = document.documentElement.getAttribute("data-theme")==="dark";
      const initial = (name[0]||"U").toUpperCase();
      slot.innerHTML = `<span style="position:relative">
        <button class="icon-btn" id="avatarBtn" title="Contul meu" style="background:${avBg};border:none;color:#fff;font-weight:800">${initial}</button>
        <div id="acctMenu" class="acct-pop" hidden>
          <div class="acct-head">
            <span class="acct-av" style="background:${avBg}">${initial}</span>
            <div class="acct-id"><div class="em">${esc(name)}</div><div class="tier ${tm.cls}">${tm.ic} ${esc(tm.nm)}</div></div>
          </div>
          <div class="acct-body">
            <div class="acct-col">
              <h5>Cont &amp; setări</h5>
              <a class="acct-link" href="/account.html"><span class="ico">👤</span>Contul meu</a>
              <a class="acct-link" href="/ultra/profil.html"><span class="ico">🧭</span>Profilul financiar</a>
              <a class="acct-link" href="/cursuri.html"><span class="ico">🎓</span>Cursurile mele${isPremium?` <span class="meta">deblocate</span>`:``}</a>
              <a class="acct-link" href="/instrumente.html"><span class="ico">🧰</span>Instrumentele mele</a>
              <a class="acct-link" href="/feedback.html"><span class="ico">💬</span>Trimite feedback</a>
              ${isAdmin ? `<a class="acct-link" href="/statistici.html"><span class="ico">📊</span>Statistici</a>` : ``}
            </div>
            <div class="acct-col" id="acctPlans">${plansColHTML(rank)}</div>
          </div>
          <div class="acct-foot">
            <button class="acct-theme" id="acctTheme"><span class="theme-ic">${isDark?"☀️":"🌙"}</span> <span id="acctThemeT">${isDark?"Mod luminos":"Mod întunecat"}</span></button>
            <button class="acct-logout" id="logoutBtn">↩︎ Deconectează-te</button>
          </div>
        </div></span>`;
      const menu = document.getElementById("acctMenu");
      document.getElementById("avatarBtn").onclick=(e)=>{e.stopPropagation();menu.hidden=!menu.hidden;};
      menu.onclick=(e)=>e.stopPropagation();
      document.getElementById("logoutBtn").onclick=()=>sb.auth.signOut();
      const tBtn=document.getElementById("acctTheme");
      if(tBtn) tBtn.onclick=()=>{ toggleTheme(); const d=document.documentElement.getAttribute("data-theme")==="dark";
        const t=document.getElementById("acctThemeT"); if(t) t.textContent=d?"Mod luminos":"Mod întunecat"; };
      document.addEventListener("click",()=>{menu.hidden=true;});
    } else {
      slot.innerHTML = `<a class="btn btn-primary" href="/login.html" style="padding:9px 18px">Cont</a>`;
    }
  }
  // când vine tierul real din DB, reîmprospătează coloana de planuri + badge-ul (fără re-render complet)
  window.addEventListener("cf-auth", function(e){
    const d = e.detail || {};
    const isAdmin = !!d.isAdmin;
    const tier = isAdmin ? "ultra" : (d.tier || "free");
    const rank = isAdmin ? 3 : (RANK[tier] != null ? RANK[tier] : 0);
    const plansEl = document.getElementById("acctPlans");
    if(plansEl) plansEl.innerHTML = plansColHTML(rank);
    const tierEl = document.querySelector("#acctMenu .acct-id .tier");
    if(tierEl){ const tm = tierMeta(isAdmin ? null : tier, isAdmin); tierEl.className = "tier "+tm.cls; tierEl.textContent = tm.ic+" "+tm.nm; }
  });
  if(sb){
    sb.auth.getSession().then(({data})=>renderAcct(data.session));
    sb.auth.onAuthStateChange((_e,s)=>renderAcct(s));
  } else { renderAcct(null); }

  // ---- reveal on scroll ----
  const io = new IntersectionObserver((es)=>es.forEach(x=>{if(x.isIntersecting)x.target.classList.add("in")}),{threshold:.12});
  window.addEventListener("DOMContentLoaded",()=>document.querySelectorAll(".reveal").forEach(e=>io.observe(e)));

  // ---- bifează articolele deja citite (orice card spre /articole/...) ----
  function markRead(){
    let read; try{ read=JSON.parse(localStorage.getItem("cf-read")||"[]"); }catch(e){ return; }
    if(!read.length) return;
    document.querySelectorAll('a[href*="/articole/"]').forEach(a=>{
      const m=(a.getAttribute("href")||"").match(/\/articole\/([^\/]+)\.html/);
      if(m && read.includes(decodeURIComponent(m[1])) && !a.querySelector(".read-tick")){
        const h=a.querySelector("h3");
        if(h && !h.querySelector(".read-tick")){ const s=document.createElement("span"); s.className="read-tick"; s.title="Citit"; s.textContent="✓"; h.appendChild(s); }
      }
    });
  }
  window.addEventListener("DOMContentLoaded",markRead);

  // ---- parallax hero la scroll (jos/sus) ----
  (function(){
    if(matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const hero=document.querySelector(".hero"); if(!hero) return;
    const txt=hero.querySelector(".hero-grid > div:first-child");
    const cap=hero.querySelector(".hero-caption");
    const c3d=document.getElementById("hero3d");
    let ticking=false;
    function onScroll(){
      ticking=false; const y=window.scrollY; if(y>1200) return;
      const f=Math.max(0,1-y/600);
      if(txt){ txt.style.transform="translateY("+(y*0.34)+"px)"; txt.style.opacity=f; }
      if(cap){ cap.style.transform="translateY("+(y*0.16)+"px)"; cap.style.opacity=f; }
      if(c3d){ c3d.style.transform="translateY("+(y*0.14)+"px) scale("+(1+y*0.00014)+")"; }
    }
    window.addEventListener("scroll",()=>{ if(!ticking){ requestAnimationFrame(onScroll); ticking=true; } }, {passive:true});
    onScroll();
  })();

  // ---- analytics minimal: numără pageview-ul în Supabase (cookieless, fără date personale) ----
  (function(){
    try{
      if (navigator.webdriver) return;                 // sari peste boți/headless
      if (location.pathname.indexOf("/statistici") === 0) return; // nu număra panoul de admin
      let vid = localStorage.getItem("cf-vid");
      if (!vid) { vid = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : (String(Date.now())+"-"+Math.random().toString(36).slice(2)); localStorage.setItem("cf-vid", vid); }
      if (!sb) return;
      sb.from("page_views").insert({ path: location.pathname, visitor: vid, referrer: document.referrer || null }).then(function(){}, function(){});
    }catch(e){}
  })();
})();
