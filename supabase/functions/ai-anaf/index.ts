// Supabase Edge Function: ai-anaf
// Asistent fiscal ANAF pentru clubulfinanciar.ro — fallback multi-provider (free LLM).
// Folosește ACELEAȘI chei ca StockCap (setate ca secrete Supabase, vezi README de deploy).
//
// Deploy:
//   supabase functions deploy ai-anaf --no-verify-jwt
//   supabase secrets set CEREBRAS_API_KEY=... GROQ_API_KEY=... GEMINI_API_KEY=... \
//       MISTRAL_API_KEY=... TOGETHER_API_KEY=... DEEPSEEK_API_KEY=... SAMBANOVA_API_KEY=... \
//       OPENROUTER_API_KEY=... NVIDIA_API_KEY=... FIREWORKS_API_KEY=... SILICONFLOW_API_KEY=...
//
// (aceleași valori ca în GitHub Secrets ale StockCap)

const PROVIDERS: [string, string, string, string][] = [
  ["cerebras",    "https://api.cerebras.ai/v1",                              "gpt-oss-120b",                                    "CEREBRAS_API_KEY"],
  ["groq",        "https://api.groq.com/openai/v1",                          "llama-3.3-70b-versatile",                         "GROQ_API_KEY"],
  ["together",    "https://api.together.xyz/v1",                             "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",    "TOGETHER_API_KEY"],
  ["gemini",      "https://generativelanguage.googleapis.com/v1beta/openai", "gemini-2.0-flash",                                "GEMINI_API_KEY"],
  ["mistral",     "https://api.mistral.ai/v1",                               "mistral-small-latest",                            "MISTRAL_API_KEY"],
  ["sambanova",   "https://api.sambanova.ai/v1",                             "Meta-Llama-3.3-70B-Instruct",                     "SAMBANOVA_API_KEY"],
  ["deepseek",    "https://api.deepseek.com/v1",                             "deepseek-chat",                                   "DEEPSEEK_API_KEY"],
  ["openrouter",  "https://openrouter.ai/api/v1",                            "nvidia/nemotron-3-nano-30b-a3b:free",             "OPENROUTER_API_KEY"],
  ["nvidia",      "https://integrate.api.nvidia.com/v1",                     "meta/llama-3.3-70b-instruct",                     "NVIDIA_API_KEY"],
  ["fireworks",   "https://api.fireworks.ai/inference/v1",                   "accounts/fireworks/models/llama-v3p3-70b-instruct","FIREWORKS_API_KEY"],
  ["siliconflow", "https://api.siliconflow.cn/v1",                           "deepseek-ai/DeepSeek-V3",                         "SILICONFLOW_API_KEY"],
];

const SYSTEM = `Ești "Asistentul ANAF" al Clubul Financiar — un ghid fiscal prietenos pentru România, actualizat la legislația 2026.

REGULI DE FIER:
1. Răspunzi DOAR pe fiscalitate/finanțe personale din România (ANAF, Declarația Unică, PFA, SRL, micro, TVA, CASS, CAS, impozite, chirii, dividende, investiții, crypto, credite, pensii).
2. Ești EDUCATIV, nu dai consultanță fiscală oficială și nu înlocuiești un contabil sau ANAF. Pentru sume mari/decizii ireversibile spui mereu să verifice pe anaf.ro sau cu un contabil.
3. NICIODATĂ nu recomanzi instrumente de investiție concrete ("cumpără acțiunea X", "investește în Y") — e linie roșie ASF. Explici educativ, atât.
4. Răspunzi în română, clar și scurt, cu cifre concrete în lei când e cazul. Structurezi cu liste când ajută.
5. Dacă întrebarea nu e despre fiscalitate/finanțe RO, refuzi politicos și redirecționezi.

CONSTANTE 2026 (folosește EXACT aceste valori):
- Salariu minim brut: 4.050 lei. Praguri (salarii minime): 6 SM = 24.300 lei, 12 SM = 48.600 lei, 24 SM = 97.200 lei, 72 SM = 291.600 lei.
- Salariat: CAS 25% + CASS 10% pe brut; impozit 10% pe (brut − CAS − CASS − deducere personală).
- Dividende: impozit 16%. Micro-SRL: 1% pe venituri (plafon 100.000 €, min. 1 salariat). SRL profit: 16%.
- TVA: cotă standard 21%, redusă 11%, plafon înregistrare 395.000 lei cifră de afaceri.
- Declarația Unică: termen 25 mai; bonificație 3% la plata integrală până 15 aprilie.

METODOLOGIE DE CALCUL (respect-o exact):
- PFA sistem real: venit net = încasări − cheltuieli deductibile.
  • CAS: datorat DOAR dacă venit net ≥ 12 SM (48.600 lei); 25% pe bază aleasă: 12 SM dacă venit net între 12 și 24 SM, 24 SM dacă ≥ 24 SM.
  • CASS: 10% pe venitul net realizat, cu bază minimă 6 SM (dacă venitul ≥ 6 SM) și bază MAXIMĂ 72 SM (291.600 lei). NU pe venitul brut.
  • Impozit: 10% pe (venit net − CAS − CASS) — contribuțiile sunt deductibile.
- Venituri pasive (chirii, dividende, dobânzi, investiții, crypto): CASS pe TREPTE fixe (6/12/24 SM), cumulat pe total venit pasiv. Chirii: impozit 10% pe venit net (după deducere forfetară 20%).
- Dacă nu ești sigur pe o cifră, spune că e orientativă.

ÎNDRUMARE CĂTRE UNELTE (foarte important):
- Pentru cifra EXACTĂ, trimite userul la unealta potrivită de pe clubulfinanciar.ro/instrumente.html:
  PFA/SRL → "PFA vs micro-SRL vs SRL"; situația fiscală totală → "Radar fiscal ANAF"; plafon TVA → "Radar plafon TVA"; credit → "Scaner credit"; crypto → "Crypto FIFO"; Declarația Unică → "Asistent Declarația Unică".
- Calculezi tu orientativ, dar precizezi: "pentru cifra exactă pe cazul tău, folosește unealta [X] de pe site".

Închei mereu calculele cu: "Estimare educativă — verifică pe anaf.ro sau cu unealta de pe site pentru cifra exactă."`;

// Un singur apel către un provider+cheie. Aruncă la eșec.
async function callOne(c: { name: string; base: string; model: string; key: string },
                       messages: any[], maxTokens: number, temperature: number) {
  const resp = await fetch(c.base + "/chat/completions", {
    method: "POST",
    headers: { "Authorization": "Bearer " + c.key, "Content-Type": "application/json" },
    body: JSON.stringify({ model: c.model, messages, max_tokens: maxTokens, temperature }),
    signal: AbortSignal.timeout(45000),
  });
  if (!resp.ok) throw new Error(`${c.name} HTTP ${resp.status}`);
  const j = await resp.json();
  const content = j?.choices?.[0]?.message?.content;
  if (!content) throw new Error(`${c.name} fără conținut`);
  return { content, provider: c.name };
}

// Strânge TOATE cheile (de bază + numerotate _1.._9 per provider) și le încearcă
// în PARALEL, în loturi, returnând primul răspuns reușit (rezistent la rate-limit).
async function chat(messages: any[], maxTokens = 900, temperature = 0.4) {
  const SUFFIXES = ["", "_1", "_2", "_3", "_4", "_5", "_6", "_7", "_8", "_9"];
  const cands: { name: string; base: string; model: string; key: string }[] = [];
  for (const [name, base, model, envb] of PROVIDERS) {
    for (const s of SUFFIXES) {
      const key = Deno.env.get(envb + s);
      if (key) cands.push({ name, base, model, key });
    }
  }
  if (!cands.length) throw new Error("nicio cheie setată");
  const BATCH = 6; // câte chei se încearcă SIMULTAN
  let last = "n/a";
  for (let i = 0; i < cands.length; i += BATCH) {
    const batch = cands.slice(i, i + BATCH);
    try {
      return await Promise.any(batch.map((c) => callOne(c, messages, maxTokens, temperature)));
    } catch (e) {
      last = `lot ${i / BATCH + 1} (${batch.length} chei) au eșuat`;
    }
  }
  throw new Error("toate cheile au eșuat: " + last);
}

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, content-type, apikey",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405, headers: CORS });
  try {
    const { messages, context } = await req.json();
    if (!Array.isArray(messages) || !messages.length) {
      return new Response(JSON.stringify({ error: "messages required" }), { status: 400, headers: { ...CORS, "Content-Type": "application/json" } });
    }
    const sys = SYSTEM + (context ? `\n\nContextul utilizatorului (cifrele lui, folosește-le): ${JSON.stringify(context)}` : "");
    const trimmed = messages.slice(-12).map((m: any) => ({
      role: m.role === "assistant" ? "assistant" : "user",
      content: String(m.content || "").slice(0, 4000),
    }));
    const out = await chat([{ role: "system", content: sys }, ...trimmed]);
    return new Response(JSON.stringify(out), { headers: { ...CORS, "Content-Type": "application/json" } });
  } catch (e) {
    const fallback = `Momentan asistentul AI nu e disponibil. Încearcă din nou peste câteva momente sau verifică pe anaf.ro.`;
    return new Response(JSON.stringify({ error: String(e), content: fallback }),
      { status: 200, headers: { ...CORS, "Content-Type": "application/json" } });
  }
});
