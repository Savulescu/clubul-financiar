/* Clubul Financiar — navbar + footer + theme + auth (injectate pe toate paginile) */
(function () {
  const SB_URL = "https://maumjqciuxdbwjtvcpsy.supabase.co";
  const SB_KEY = "sb_publishable_N6X3B_Sn7oWkxJF-iHCfbg__w4J7ONR";
  const sb = window.supabase ? window.supabase.createClient(SB_URL, SB_KEY) : null;
  window._sb = sb;

  const NAV = [
    ["Începe aici", "/incepe-aici.html"],
    ["Educație", "/educatie.html"],
    ["Glosar", "/glosar.html"],
    ["Știri", "/stiri.html"],
    ["Investiții", "/investitii.html"],
    ["Credite", "/credite.html"],
    ["Calculatoare", "/calculatoare.html"],
    ["Cursuri", "/cursuri.html"],
    ["Premium", "/premium.html"],
  ];
  const SOC = [
    ["Instagram","https://www.instagram.com/clubulfinanciar"],["TikTok","https://www.tiktok.com/@clubulfinanciar"],
    ["YouTube","https://www.youtube.com/@clubulfinanciar"],["Facebook","https://www.facebook.com/clubulfinanciar"],
    ["Threads","https://www.threads.net/@clubulfinanciar"],["X","https://x.com/clubulfinanciar"],
    ["Telegram","https://t.me/clubul_financiar"],
  ];

  // ---- theme ----
  const saved = localStorage.getItem("cf-theme");
  if (saved) document.documentElement.setAttribute("data-theme", saved);
  function toggleTheme(){
    const cur = document.documentElement.getAttribute("data-theme")==="dark"?"":"dark";
    if(cur) document.documentElement.setAttribute("data-theme",cur); else document.documentElement.removeAttribute("data-theme");
    localStorage.setItem("cf-theme",cur);
    document.querySelectorAll(".theme-ic").forEach(e=>e.textContent=cur==="dark"?"☀️":"🌙");
  }

  // ---- navbar ----
  const nav = document.createElement("header");
  nav.className = "nav";
  nav.innerHTML = `<div class="container nav-in">
    <a class="brand-logo" href="/index.html"><span class="dot">CF</span> Clubul Financiar</a>
    <nav class="nav-links" id="navLinks">${NAV.map(([t,h])=>`<a href="${h}">${t}</a>`).join("")}</nav>
    <div class="nav-right">
      <button class="icon-btn" id="searchBtn" aria-label="Caută">🔍</button>
      <button class="icon-btn" id="themeBtn" aria-label="Temă"><span class="theme-ic">${document.documentElement.getAttribute("data-theme")==="dark"?"☀️":"🌙"}</span></button>
      <span id="acctSlot"></span>
      <button class="icon-btn burger" id="burger" aria-label="Meniu">☰</button>
    </div>
  </div>`;
  document.body.prepend(nav);
  document.getElementById("themeBtn").onclick = toggleTheme;
  document.getElementById("burger").onclick = () => document.getElementById("navLinks").classList.toggle("open");

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
  function openSearch() {
    overlay.hidden = false; document.body.style.overflow = "hidden"; setTimeout(() => sInput.focus(), 40);
    if (!searchLoaded) {
      searchLoaded = true;
      fetch("/search-index.json").then(r => r.json()).then(d => { searchIdx = d; runSearch(); }).catch(() => { sRes.innerHTML = `<p class="search-hint">Căutarea nu e disponibilă momentan.</p>`; });
    }
  }
  function closeSearch() { overlay.hidden = true; document.body.style.overflow = ""; }
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
    if (!top.length) { sRes.innerHTML = `<p class="search-hint">Niciun rezultat pentru „${sInput.value}".</p>`; return; }
    sRes.innerHTML = top.map(([, a]) => {
      const badge = a.k === "g" ? "Glosar" : (a.k === "calc" ? "Calculator" : (a.cn || "Articol"));
      return `<a class="search-item" href="${a.u}"><div><strong>${a.t}</strong><span class="search-badge">${badge}</span></div><p>${a.d || ""}</p></a>`;
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
    ["Educație", [["Începe aici","/incepe-aici.html"],["Buget personal","/educatie.html"],["Economisire","/educatie.html"],["Psihologia banilor","/educatie.html"]]],
    ["Investiții", [["Bursă & acțiuni","/investitii.html"],["ETF-uri","/investitii.html"],["Titluri de stat","/investitii.html"],["Calculatoare","/calculatoare.html"]]],
    ["Platformă", [["Cursuri","/cursuri.html"],["Premium","/premium.html"],["Cont","/login.html"],["Contact","/contact.html"]]],
  ];
  const foot = document.createElement("footer");
  foot.className = "foot";
  foot.innerHTML = `<div class="container">
    <div class="foot-grid">
      <div>
        <a class="brand-logo" href="/index.html"><span class="dot">CF</span> Clubul Financiar</a>
        <p style="color:var(--muted);font-size:.92rem;margin-top:12px;max-width:300px">Învață banii de la zero — educație financiară pe înțelesul tuturor.</p>
        <div class="soc">${SOC.map(([t,h])=>`<a href="${h}" title="${t}" rel="noopener" target="_blank">${t[0]}</a>`).join("")}</div>
      </div>
      ${cols.map(([h,links])=>`<div><h4>${h}</h4>${links.map(([t,u])=>`<a href="${u}">${t}</a>`).join("")}</div>`).join("")}
    </div>
    <div class="foot-bottom">
      <span>© Clubul Financiar · clubulfinanciar.ro</span>
      <span><a href="/privacy.html">Confidențialitate</a> · <a href="/terms.html">Termeni</a> · Conținut educativ, nu sfat de investiții</span>
    </div>
  </div>`;
  document.body.appendChild(foot);

  // ---- roluri (admin / premium) ----
  const ADMIN_EMAILS = ["clubulfinanciar@gmail.com"];
  function applyRole(session){
    const email = session && session.user && (session.user.email || "").toLowerCase();
    const isAdmin = !!email && ADMIN_EMAILS.includes(email);
    const isPremium = isAdmin; // momentan: admin = acces premium complet
    if(isPremium){ document.body.setAttribute("data-cf-premium",""); } else { document.body.removeAttribute("data-cf-premium"); }
    if(isAdmin){ document.body.setAttribute("data-cf-role-admin",""); } else { document.body.removeAttribute("data-cf-role-admin"); }
    window.cfPremium = isPremium; window.cfAdmin = isAdmin; window.cfEmail = email || null;
    try { window.dispatchEvent(new CustomEvent("cf-auth", { detail: { email: email || null, isPremium, isAdmin } })); } catch(e){}
    return { isAdmin, isPremium };
  }

  // ---- auth account area ----
  function renderAcct(session){
    const { isAdmin, isPremium } = applyRole(session);
    const slot = document.getElementById("acctSlot");
    if(!slot) return;
    if(session && session.user){
      const name = session.user.email || "cont";
      const roleLine = isAdmin
        ? `<div style="font-size:.72rem;font-weight:800;color:var(--gold,#E8C268);margin-top:3px">👑 Administrator · acces complet</div>`
        : (isPremium ? `<div style="font-size:.72rem;font-weight:800;color:var(--gold,#E8C268);margin-top:3px">⭐ Premium activ</div>` : ``);
      const avBg = isAdmin ? "linear-gradient(135deg,#E8C268,#caa23f)" : "var(--grad)";
      slot.innerHTML = `<span style="position:relative">
        <button class="icon-btn" id="avatarBtn" title="Contul meu" style="background:${avBg};border:none;color:#fff;font-weight:800">${(name[0]||"U").toUpperCase()}</button>
        <div id="acctMenu" hidden style="position:absolute;top:46px;right:0;width:240px;background:var(--card);border:1px solid var(--border);border-radius:14px;padding:8px;box-shadow:var(--shadow-lg)">
          <div style="padding:8px 10px 10px;border-bottom:1px solid var(--border);margin-bottom:6px"><div style="font-weight:700;font-size:.84rem;color:var(--emerald);word-break:break-all">${name}</div>${roleLine}</div>
          <a href="/account.html" style="display:block;padding:10px;border-radius:8px;color:var(--text);font-size:.9rem">👤 Contul meu</a>
          <a href="/cursuri.html" style="display:block;padding:10px;border-radius:8px;color:var(--text);font-size:.9rem">🎓 Cursurile mele</a>
          ${isPremium ? `<a href="/cursuri.html" style="display:block;padding:10px;border-radius:8px;color:var(--text);font-size:.9rem">🔓 Cursuri premium (deblocate)</a>` : ``}
          <button id="logoutBtn" style="width:100%;text-align:left;background:transparent;border:none;border-top:1px solid var(--border);margin-top:6px;padding:10px;color:#e25555;font-size:.9rem;cursor:pointer">↩︎ Deconectează-te</button>
        </div></span>`;
      const menu = document.getElementById("acctMenu");
      document.getElementById("avatarBtn").onclick=(e)=>{e.stopPropagation();menu.hidden=!menu.hidden;};
      menu.onclick=(e)=>e.stopPropagation();
      document.getElementById("logoutBtn").onclick=()=>sb.auth.signOut();
      document.addEventListener("click",()=>{menu.hidden=true;});
    } else {
      slot.innerHTML = `<a class="btn btn-primary" href="/login.html" style="padding:9px 18px">Cont</a>`;
    }
  }
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
})();
