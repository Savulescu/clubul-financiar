/* Clubul Financiar — Masterclass Bursă: gating premium + cuprins + progres + share/citit
   + test de 25 întrebări (inline) + navigare prev/next. Layout: share → test → nav → disclaimer. */
(function () {
  const art = document.querySelector("article.article");
  if (!art) return;
  const h1 = art.querySelector("h1");
  const titleText = h1 ? h1.textContent.trim() : document.title;
  const slug = decodeURIComponent(location.pathname.split("/").pop().replace(/\.html$/, ""));
  const disc = art.querySelector(".disc");
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  // ---------- gating Pro (preview ~25% + lock, SEO-safe) ----------
  var hasPro = function () { return !!window.cfAdmin || window.cfTier === "pro" || window.cfTier === "ultra"; };
  (function () {
    if (art.getAttribute("data-premium") !== "1" || hasPro()) return;
    if (!h1 || !disc) return;
    const nodes = []; let nn = h1.nextElementSibling;
    while (nn && nn !== disc) { nodes.push(nn); nn = nn.nextElementSibling; }
    if (nodes.length < 4) return;
    let total = 0; nodes.forEach(x => total += (x.textContent || "").length);
    let acc = 0, cut = nodes.length;
    for (let i = 0; i < nodes.length; i++) { acc += (nodes[i].textContent || "").length; if (i >= 1 && acc >= total * 0.25) { cut = i + 1; break; } }
    const heads = [];
    for (let j = cut; j < nodes.length; j++) { if (/^H[23]$/.test(nodes[j].tagName)) { const h = nodes[j].textContent.trim(); if (h) heads.push(h); } }
    const st = document.createElement("style");
    st.textContent = "article.cf-locked .premium-rest{display:none}.premium-gate{position:relative;margin:0 0 10px;text-align:center}.premium-gate .pg-fade{height:90px;margin-top:-110px;margin-bottom:20px;background:linear-gradient(transparent,var(--bg));pointer-events:none;position:relative}.premium-gate .pg-card{border:1px solid color-mix(in srgb,var(--gold) 42%,var(--border));background:linear-gradient(180deg,color-mix(in srgb,var(--gold) 9%,var(--card)),var(--card));border-radius:18px;padding:28px 24px;box-shadow:var(--shadow-lg)}.premium-gate h2{font-size:1.4rem;margin:8px 0 6px}.premium-gate .pg-list{list-style:none;padding:0;margin:12px auto 16px;max-width:430px;text-align:left}.premium-gate .pg-list li{padding:7px 0 7px 26px;position:relative;color:var(--muted)}.premium-gate .pg-list li::before{content:'🔒';position:absolute;left:0;font-size:.82rem}.premium-gate .price-line{color:var(--gold);font-weight:800;margin:10px 0 14px}";
    document.head.appendChild(st);
    const rest = document.createElement("div"); rest.className = "premium-rest";
    for (let k = cut; k < nodes.length; k++) rest.appendChild(nodes[k]);
    const gate = document.createElement("div"); gate.className = "premium-gate";
    gate.innerHTML = '<div class="pg-fade"></div><div class="pg-card"><span class="cf-premium-badge">Pro</span><h2>Restul lecției e în Pro</h2>' +
      (heads.length ? '<p style="color:var(--muted)">Ce mai afli în această lecție:</p><ul class="pg-list">' + heads.slice(0, 6).map(h => '<li>' + esc(h) + '</li>').join("") + '</ul>' : '<p style="color:var(--muted)">Deblochează lecția completă + testul + tot Masterclass-ul.</p>') +
      '<p class="price-line">Tot Masterclass Bursă + cele 1000 de lecții + Hub Fiscal — 99 lei/lună</p><a class="btn btn-primary" href="/premium#plan-pro">Deblochează cu Pro</a><p style="margin-top:10px;font-size:.85rem"><a href="/login" style="color:var(--emerald-link)">Ai cont Pro? Conectează-te</a></p></div>';
    disc.parentNode.insertBefore(gate, disc);
    disc.parentNode.insertBefore(rest, disc);
    art.classList.add("cf-locked");
    window.addEventListener("cf-auth", function () {
      if (hasPro()) { art.classList.remove("cf-locked"); while (rest.firstChild) disc.parentNode.insertBefore(rest.firstChild, rest); gate.remove(); rest.remove(); }
    });
  })();

  // ---------- bară progres citire ----------
  const bar = document.createElement("div"); bar.className = "read-progress"; document.body.appendChild(bar);
  let ticking = false, sh = document.documentElement.scrollHeight;
  function onScroll() { ticking = false; const t = sh - window.innerHeight; bar.style.width = Math.min(100, Math.max(0, t > 0 ? (window.scrollY / t) * 100 : 0)) + "%"; }
  window.addEventListener("scroll", () => { if (!ticking) { requestAnimationFrame(onScroll); ticking = true; } }, { passive: true });
  window.addEventListener("resize", () => { sh = document.documentElement.scrollHeight; onScroll(); }, { passive: true });
  onScroll();

  function slugify(s) { return s.toLowerCase().replace(/[ăâ]/g, "a").replace(/î/g, "i").replace(/ș|ş/g, "s").replace(/ț|ţ/g, "t").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 50); }

  // ---------- cuprins ----------
  const heads = [...art.querySelectorAll("h2, h3")].filter(h => { const t = h.textContent.trim(); return t && t.toLowerCase() !== titleText.toLowerCase(); });
  if (heads.length >= 3) {
    const used = {};
    const items = heads.map(h => { let id = slugify(h.textContent) || "sectiune"; if (used[id]) { used[id]++; id += "-" + used[id]; } else { used[id] = 1; } h.id = id; return `<li class="${h.tagName === "H3" ? "toc-sub" : ""}"><a href="#${id}">${esc(h.textContent.trim())}</a></li>`; }).join("");
    const toc = document.createElement("nav"); toc.className = "toc"; toc.innerHTML = `<p class="toc-h">Cuprins</p><ul>${items}</ul>`;
    if (h1 && h1.nextSibling) art.insertBefore(toc, h1.nextSibling); else art.insertBefore(toc, art.firstChild);
  }

  // ---------- stiluri test + navigare (din article.js) ----------
  const st2 = document.createElement("style");
  st2.textContent = ".art-actions{display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;margin:28px 0 6px;padding:14px 0;border-top:1px solid var(--border)}.read-btn{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:9px 14px;font:inherit;font-weight:700;cursor:pointer;color:var(--text)}.read-btn.done{border-color:var(--emerald);color:var(--emerald-link)}.share-row{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:.9rem}.share-row a,.share-row button{display:grid;place-items:center;width:34px;height:34px;border-radius:9px;background:var(--card);border:1px solid var(--border);color:var(--text);text-decoration:none;font-weight:700;cursor:pointer}.share-row a:hover,.share-row button:hover{border-color:var(--emerald)}.lesson-nav{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:24px 0}.lnav{display:block;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 16px;transition:.15s}.lnav:hover{border-color:var(--emerald);transform:translateY(-2px)}.lnav span{display:block;color:var(--muted);font-size:.78rem;font-weight:700}.lnav b{display:block;font-size:.95rem;margin-top:3px;color:var(--text)}.lnav.next{text-align:right}@media(max-width:560px){.lesson-nav{grid-template-columns:1fr}.lnav.next{text-align:left}}.lesson-quiz{background:linear-gradient(135deg,color-mix(in srgb,var(--emerald) 10%,var(--card)),var(--card));border:1px solid color-mix(in srgb,var(--emerald) 30%,var(--border));border-radius:16px;padding:22px;margin:30px 0 10px;text-align:center}.lq-q{font-size:1.15rem;font-weight:800;font-family:var(--font-display);margin:10px 0 16px;text-align:left}.lq-opt{display:block;width:100%;text-align:left;background:var(--card);border:2px solid var(--border);border-radius:12px;padding:13px 16px;margin-bottom:10px;font:inherit;font-size:1rem;cursor:pointer;transition:.15s}.lq-opt:hover:not(:disabled){border-color:var(--emerald)}.lq-opt.ok{border-color:var(--emerald);background:color-mix(in srgb,var(--emerald) 14%,var(--card))}.lq-opt.no{border-color:#e25555;background:color-mix(in srgb,#e25555 12%,var(--card))}.lq-ex{display:none;background:var(--bg-soft);border-left:4px solid var(--emerald);border-radius:10px;padding:12px 14px;margin:4px 0 14px;text-align:left;font-size:.92rem}.lq-ex.show{display:block}.lq-prog{color:var(--muted);font-weight:700;font-size:.85rem;text-align:left;margin-bottom:6px}.lq-big{font-size:2.4rem;font-weight:900;background:var(--grad);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}";
  document.head.appendChild(st2);

  // ---------- bară acțiuni: marchează citit + share (înainte de disclaimer) ----------
  const url = location.href.split("#")[0], enc = encodeURIComponent, READ_KEY = "cf-read";
  function getRead() { try { return JSON.parse(localStorage.getItem(READ_KEY) || "[]"); } catch (e) { return []; } }
  function isRead() { return getRead().includes(slug); }
  function setRead(v) { let a = getRead(); if (v && !a.includes(slug)) a.push(slug); if (!v) a = a.filter(s => s !== slug); localStorage.setItem(READ_KEY, JSON.stringify(a)); }
  const actions = document.createElement("div"); actions.className = "art-actions";
  actions.innerHTML = `<button class="read-btn" id="readBtn">${isRead() ? "✓ Citit" : "Marchează ca citit"}</button>
    <div class="share-row"><span>Distribuie:</span>
      <a href="https://www.facebook.com/sharer/sharer.php?u=${enc(url)}" target="_blank" rel="noopener" title="Facebook">f</a>
      <a href="https://x.com/intent/tweet?url=${enc(url)}&text=${enc(titleText)}" target="_blank" rel="noopener" title="X">𝕏</a>
      <a href="https://api.whatsapp.com/send?text=${enc(titleText + " " + url)}" target="_blank" rel="noopener" title="WhatsApp">W</a>
      <a href="https://t.me/share/url?url=${enc(url)}&text=${enc(titleText)}" target="_blank" rel="noopener" title="Telegram">✈</a>
      <button id="copyBtn" title="Copiază linkul">🔗</button></div>`;
  if (disc) disc.parentNode.insertBefore(actions, disc); else art.appendChild(actions);
  const readBtn = actions.querySelector("#readBtn"); if (isRead()) readBtn.classList.add("done");
  readBtn.onclick = () => { const now = !isRead(); setRead(now); readBtn.textContent = now ? "✓ Citit" : "Marchează ca citit"; readBtn.classList.toggle("done", now); };
  actions.querySelector("#copyBtn").onclick = function () { const b = this; navigator.clipboard && navigator.clipboard.writeText(url).then(() => { b.textContent = "✓"; setTimeout(() => b.textContent = "🔗", 1500); }); };

  // ---------- TEST 25 întrebări (din JSON inline) — între share și disclaimer ----------
  let quiz = [];
  try { quiz = JSON.parse((document.getElementById("cf-mc-quiz") || {}).textContent || "[]"); } catch (e) {}
  if (quiz.length) {
    const box = document.createElement("section"); box.className = "lesson-quiz";
    box.innerHTML = '<div id="lqStart"><p class="eyebrow">Testează-te</p><h2 style="font-size:1.3rem;margin:4px 0 10px">Ai înțeles lecția? Verifică în ' + quiz.length + ' întrebări.</h2><button class="btn btn-primary" id="lqBtn">Începe testul</button></div><div id="lqRun"></div>';
    if (disc) disc.parentNode.insertBefore(box, disc); else art.appendChild(box);
    document.getElementById("lqBtn").onclick = () => runQuiz(quiz);
    function runQuiz(qs) {
      let i = 0, correct = 0; const prem = !!window.cfPremium;
      const run = document.getElementById("lqRun"); document.getElementById("lqStart").style.display = "none";
      function q() {
        if (i >= qs.length) return fin();
        const it = qs[i];
        run.innerHTML = '<div class="lq-prog">' + (i + 1) + ' / ' + qs.length + '</div><div class="lq-q">' + esc(it.q) + '</div>' +
          it.options.map((o, k) => '<button class="lq-opt" data-k="' + k + '">' + esc(o) + '</button>').join("") +
          '<div class="lq-ex" id="lqEx"></div><button class="btn btn-primary" id="lqNext" style="display:none;width:100%;justify-content:center">Continuă</button>';
        run.querySelectorAll(".lq-opt").forEach(b => b.onclick = () => ans(b, it));
      }
      function ans(b, it) {
        const opts = run.querySelectorAll(".lq-opt"); opts.forEach(o => o.disabled = true);
        const ok = +b.dataset.k === it.correct; opts[it.correct].classList.add("ok"); if (!ok) b.classList.add("no");
        if (ok) { correct++; if (prem) { try { localStorage.setItem("cf-qz-xp", parseInt(localStorage.getItem("cf-qz-xp") || "0", 10) + 10); } catch (e) {} } }
        const ex = document.getElementById("lqEx"); ex.innerHTML = (ok ? "✓ Corect! " : "✗ ") + esc(it.explain || ""); ex.classList.add("show");
        const nx = document.getElementById("lqNext"); nx.style.display = "inline-flex"; nx.textContent = (i + 1 >= qs.length) ? "Vezi rezultatul" : "Continuă"; nx.onclick = () => { i++; q(); };
      }
      function fin() {
        const pct = Math.round(correct / qs.length * 100);
        run.innerHTML = '<div class="lq-big">' + pct + '%</div><p style="color:var(--muted)">' + correct + ' din ' + qs.length + ' corecte.' + (prem ? ' +' + (correct * 10) + ' XP' : '') + '</p>' +
          (prem ? '' : '<p style="font-size:.9rem;margin-top:8px">Cu <a href="/premium" style="color:var(--emerald-link);font-weight:700">Premium</a> aduni XP și primești certificate.</p>') +
          '<button class="btn btn-ghost" id="lqAgain" style="margin-top:12px">Încă o dată</button>';
        document.getElementById("lqAgain").onclick = () => runQuiz(qs);
      }
      q();
    }
  }

  // ---------- navigare prev/next (din data-attrs) — după test, înainte de disclaimer ----------
  const dp = art.getAttribute("data-prev"), dpt = art.getAttribute("data-prev-title");
  const dn = art.getAttribute("data-next"), dnt = art.getAttribute("data-next-title");
  const hub = art.getAttribute("data-hub") || "/masterclass";
  const nav = document.createElement("nav"); nav.className = "lesson-nav";
  nav.innerHTML =
    (dp ? '<a class="lnav prev" href="/masterclass/' + enc(dp) + '"><span>← Lecția anterioară</span><b>' + esc(dpt || "") + '</b></a>'
        : '<a class="lnav prev" href="' + hub + '"><span>← Înapoi la</span><b>Masterclass Bursă</b></a>') +
    (dn ? '<a class="lnav next" href="/masterclass/' + enc(dn) + '"><span>Lecția următoare →</span><b>' + esc(dnt || "") + '</b></a>'
        : '<a class="lnav next" href="' + hub + '"><span>Toate lecțiile →</span><b>Masterclass Bursă</b></a>');
  if (disc) disc.parentNode.insertBefore(nav, disc); else art.appendChild(nav);

  // ---------- intro captivantă (hook) ----------
  fetch("/assets/masterclass-intros.json").then(function (r) { return r.json(); }).then(function (hk) {
    var t = hk[slug]; if (!t || !h1) return;
    var box = document.createElement("div"); box.className = "lesson-intro";
    box.innerHTML = '<p class="li-hook" style="margin:0">✨ ' + esc(t) + '</p>';
    art.insertBefore(box, h1.nextSibling);
  }).catch(function () { });
})();
