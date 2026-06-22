// Supabase Edge Function: newsletter-welcome
// Trimite un email de bun-venit când cineva se abonează la newsletter (apelat din site.js).
//
// Deploy:
//   supabase functions deploy newsletter-welcome --no-verify-jwt
//   supabase secrets set RESEND_API_KEY=re_xxx "NEWSLETTER_FROM=Clubul Financiar <newsletter@clubulfinanciar.ro>"
//
// (RESEND_API_KEY = aceeași cheie Resend; domeniul clubulfinanciar.ro trebuie verificat în Resend.)

const NAVY = "#0e2750", NAVY2 = "#081627", PANEL = "#0f2238", GOLD = "#E8C268", GOLD2 = "#caa44a";
const INK = "#eaf1fb", MUT = "#93a7c4", LINE = "rgba(232,194,104,.24)";
const SERIF = "Georgia,'Times New Roman',serif";
const SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif";
const SITE = "https://clubulfinanciar.ro";

function welcomeHtml(): string {
  return `<!DOCTYPE html><html lang="ro"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"></head>
<body style="margin:0;padding:0;background:${NAVY2}">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:${NAVY2}"><tr><td align="center" style="padding:24px 12px">
  <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:${NAVY};border:1px solid ${LINE};border-radius:18px;overflow:hidden">
    <tr><td style="height:3px;background:linear-gradient(90deg,transparent,${GOLD2},transparent)"></td></tr>
    <tr><td style="padding:30px 28px 8px">
      <div style="font-family:${SERIF};letter-spacing:.18em;text-transform:uppercase;font-size:11px;color:${GOLD};font-weight:bold">Clubul Financiar</div>
      <div style="font-family:${SERIF};font-size:26px;color:${INK};font-weight:bold;margin-top:14px">Bun venit! 👋</div>
    </td></tr>
    <tr><td style="padding:6px 28px 4px"><div style="font-family:${SANS};font-size:15px;color:${MUT};line-height:1.65">
      Te-ai abonat la <b style="color:${INK}">Dimineața pe scurt</b> — newsletterul gratuit care-ți pune banii în context, în fiecare dimineață. Primul ajunge mâine.
    </div></td></tr>
    <tr><td style="padding:16px 28px 4px">
      <div style="background:${PANEL};border:1px solid ${LINE};border-radius:12px;padding:16px 18px">
        <div style="font-family:${SERIF};font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:${GOLD};font-weight:bold;margin-bottom:10px">Ce primești în fiecare dimineață</div>
        <div style="font-family:${SANS};font-size:14px;color:${INK};line-height:1.9">
          📰 Cele 5 lucruri care-ți mișcă banii azi<br>
          💱 Cursul oficial BNR (euro, dolar, aur)<br>
          💰 Dividendele de urmărit la bursa românească<br>
          📚 Un concept financiar explicat simplu<br>
          💡 Sfatul zilei
        </div>
      </div>
    </td></tr>
    <tr><td style="padding:22px 28px 10px">
      <table role="presentation" cellpadding="0" cellspacing="0"><tr><td style="border-radius:12px;background:linear-gradient(135deg,${GOLD},${GOLD2})">
        <a href="${SITE}" style="display:inline-block;padding:13px 26px;font-family:${SANS};font-weight:800;font-size:14px;color:#1a1304;text-decoration:none">Descoperă instrumentele →</a>
      </td></tr></table>
    </td></tr>
    <tr><td style="padding:14px 28px 26px;border-top:1px solid ${LINE}">
      <div style="font-family:${SANS};font-size:11px;color:${MUT};line-height:1.6">
        Te-ai abonat pe ${SITE}. Conținut educativ, nu sfat de investiții.<br>
        <a href="${SITE}" style="color:${GOLD};text-decoration:none">clubulfinanciar.ro</a> ·
        <a href="${SITE}/account.html" style="color:${MUT}">Preferințe</a>
      </div>
    </td></tr>
  </table>
</td></tr></table></body></html>`;
}

Deno.serve(async (req: Request) => {
  const cors = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
    "Content-Type": "application/json",
  };
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  try {
    const { email } = await req.json();
    if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      return new Response(JSON.stringify({ error: "email invalid" }), { status: 400, headers: cors });
    }
    const RESEND = Deno.env.get("RESEND_API_KEY");
    const FROM = Deno.env.get("NEWSLETTER_FROM") || "Clubul Financiar <newsletter@clubulfinanciar.ro>";
    if (!RESEND) return new Response(JSON.stringify({ error: "RESEND lipsește" }), { status: 500, headers: cors });
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { "Authorization": "Bearer " + RESEND, "Content-Type": "application/json" },
      body: JSON.stringify({ from: FROM, to: [email], subject: "Bun venit la Clubul Financiar 👋", html: welcomeHtml() }),
    });
    return new Response(JSON.stringify({ ok: r.ok }), { headers: cors });
  } catch (e) {
    return new Response(JSON.stringify({ error: String(e) }), { status: 500, headers: cors });
  }
});
