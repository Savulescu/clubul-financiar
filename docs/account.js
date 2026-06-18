// Badge de cont fix în colțul dreapta-sus (Supabase). Inclus pe paginile site-ului.
(function () {
  const SUPABASE_URL = "https://maumjqciuxdbwjtvcpsy.supabase.co";
  const SUPABASE_ANON_KEY = "sb_publishable_N6X3B_Sn7oWkxJF-iHCfbg__w4J7ONR";
  const sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  window._sb = sb;

  // stiluri badge
  const css = document.createElement("style");
  css.textContent = `
    #accountBadge{position:fixed;top:14px;right:16px;z-index:9999;display:flex;align-items:center;gap:8px;
      font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
    #accountBadge a.acc-login{color:#E8C268;border:1px solid #E8C268;border-radius:999px;padding:7px 16px;
      text-decoration:none;font-size:.85rem;font-weight:700;background:rgba(8,20,40,.55);backdrop-filter:blur(4px)}
    #accountBadge a.acc-login:hover{background:#E8C268;color:#1a1208}
    #accountBadge .acc-email{color:#e8eefb;font-size:.82rem;background:rgba(8,20,40,.55);backdrop-filter:blur(4px);
      padding:7px 12px;border-radius:999px;max-width:170px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
      border:1px solid rgba(232,194,104,.3)}
    #accountBadge button.acc-logout{background:rgba(8,20,40,.55);backdrop-filter:blur(4px);
      border:1px solid rgba(255,255,255,.22);color:#fff;border-radius:999px;padding:7px 13px;font-size:.82rem;cursor:pointer}
    #accountBadge button.acc-logout:hover{border-color:#ff9a9a;color:#ff9a9a}
  `;
  document.head.appendChild(css);

  function render(session) {
    let el = document.getElementById("accountBadge");
    if (!el) { el = document.createElement("div"); el.id = "accountBadge"; document.body.appendChild(el); }
    if (session && session.user) {
      const name = session.user.email || session.user.user_metadata?.name || "cont";
      el.innerHTML = `<span class="acc-email" title="${name}">${name}</span><button class="acc-logout">Ieși</button>`;
      el.querySelector(".acc-logout").onclick = () => sb.auth.signOut();
    } else {
      el.innerHTML = `<a class="acc-login" href="./login.html">Cont</a>`;
    }
  }

  sb.auth.getSession().then(({ data }) => render(data.session));
  sb.auth.onAuthStateChange((_e, s) => render(s));
})();
