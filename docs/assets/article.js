/* Clubul Financiar — UX articol: progres citire, cuprins, articole conexe, share, marcare citit */
(function () {
  const art = document.querySelector("article.article");
  if (!art) return;

  const h1 = art.querySelector("h1");
  const titleText = h1 ? h1.textContent.trim() : document.title;
  const slug = decodeURIComponent(location.pathname.split("/").pop().replace(/\.html$/, ""));

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
})();
