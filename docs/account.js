// Avatar de cont (omuleț) fix sus-dreapta + meniu dropdown (Supabase).
(function () {
  const SUPABASE_URL = "https://maumjqciuxdbwjtvcpsy.supabase.co";
  const SUPABASE_ANON_KEY = "sb_publishable_N6X3B_Sn7oWkxJF-iHCfbg__w4J7ONR";
  const sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  window._sb = sb;

  const css = document.createElement("style");
  css.textContent = `
    #accountBadge{position:fixed;top:14px;right:16px;z-index:9999;
      font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
    #accountBadge a.acc-login{color:#E8C268;border:1px solid #E8C268;border-radius:999px;padding:8px 18px;
      text-decoration:none;font-size:.85rem;font-weight:700;background:rgba(8,20,40,.55);backdrop-filter:blur(4px)}
    #accountBadge a.acc-login:hover{background:#E8C268;color:#1a1208}
    #accountBadge .acc-avatar{width:42px;height:42px;border-radius:50%;border:2px solid rgba(232,194,104,.6);
      background:linear-gradient(135deg,#E8C268,#C68F2C);cursor:pointer;display:flex;align-items:center;
      justify-content:center;box-shadow:0 3px 10px rgba(0,0,0,.35);padding:0}
    #accountBadge .acc-avatar:hover{filter:brightness(1.06)}
    #accountBadge .acc-menu{position:absolute;top:50px;right:0;width:240px;background:#0e2750;
      border:1px solid rgba(232,194,104,.25);border-radius:14px;padding:8px;box-shadow:0 12px 34px rgba(0,0,0,.45)}
    #accountBadge .acc-menu[hidden]{display:none}
    #accountBadge .acc-head{padding:10px 12px 12px;border-bottom:1px solid rgba(255,255,255,.08);margin-bottom:6px}
    #accountBadge .acc-head .nm{color:#E8C268;font-weight:700;font-size:.84rem;word-break:break-all}
    #accountBadge .acc-head .sub{color:#7d93b8;font-size:.72rem;margin-top:2px}
    #accountBadge .acc-item{display:block;width:100%;text-align:left;background:transparent;border:none;
      color:#e8eefb;font-size:.9rem;padding:11px 12px;border-radius:8px;cursor:pointer;text-decoration:none;font-family:inherit}
    #accountBadge .acc-item:hover{background:rgba(255,255,255,.06)}
    #accountBadge .acc-out{color:#ff9a9a;border-top:1px solid rgba(255,255,255,.08);margin-top:6px}
  `;
  document.head.appendChild(css);

  const PERSON = '<svg width="22" height="22" viewBox="0 0 24 24"><circle cx="12" cy="8.2" r="3.8" fill="#0e2750"/><path d="M5 19.5c0-3.6 3.2-5.5 7-5.5s7 1.9 7 5.5z" fill="#0e2750"/></svg>';

  function render(session) {
    let el = document.getElementById("accountBadge");
    if (!el) { el = document.createElement("div"); el.id = "accountBadge"; document.body.appendChild(el); }
    if (session && session.user) {
      const name = session.user.email || session.user.user_metadata?.name || "cont";
      el.innerHTML = `
        <button class="acc-avatar" id="accAvatar" aria-label="Cont" title="Contul meu">${PERSON}</button>
        <div class="acc-menu" id="accMenu" hidden>
          <div class="acc-head"><div class="nm">${name}</div><div class="sub">Cont Clubul Financiar</div></div>
          <a class="acc-item" href="./account.html">👤 Contul meu</a>
          <a class="acc-item" href="./account.html">🔑 Schimbă parola</a>
          <a class="acc-item" href="./index.html">🏠 Acasă</a>
          <button class="acc-item acc-out" id="accLogout">↩︎ Deconectează-te</button>
        </div>`;
      const menu = el.querySelector("#accMenu");
      el.querySelector("#accAvatar").onclick = (e) => { e.stopPropagation(); menu.hidden = !menu.hidden; };
      menu.onclick = (e) => e.stopPropagation();
      el.querySelector("#accLogout").onclick = () => sb.auth.signOut();
      document.addEventListener("click", () => { menu.hidden = true; });
    } else {
      el.innerHTML = `<a class="acc-login" href="./login.html">Cont</a>`;
    }
  }

  sb.auth.getSession().then(({ data }) => render(data.session));
  sb.auth.onAuthStateChange((_e, s) => render(s));
})();
