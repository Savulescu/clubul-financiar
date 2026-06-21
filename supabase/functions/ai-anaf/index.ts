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
4. Folosești cifrele 2026: salariu minim 4.050 lei; CAS 25%, CASS 10%, impozit venit 10%; dividende 16%; micro 1% (plafon 100.000 €, min. 1 salariat); plafon TVA 395.000 lei; cotă TVA standard 21%/redusă 11%; praguri CASS 6/12/24 salarii minime (24.300 / 48.600 / 97.200 lei); Declarația Unică termen 25 mai, bonificație 3% la plată până 15 aprilie.
5. Răspunzi în română, clar și scurt, cu cifre concrete în lei când e cazul. Structurezi cu liste când ajută. Eviți jargonul inutil.
6. Dacă întrebarea nu e despre fiscalitate/finanțe RO, refuzi politicos și redirecționezi.
7. Închei mereu calculele cu o linie: "Estimare educativă — verifică pe anaf.ro pentru cazul tău exact."`;

async function chat(messages: any[], maxTokens = 900, temperature = 0.4) {
  let last = "n/a";
  for (const [name, base, model, envb] of PROVIDERS) {
    const key = Deno.env.get(envb);
    if (!key) continue;
    try {
      const resp = await fetch(base + "/chat/completions", {
        method: "POST",
        headers: { "Authorization": "Bearer " + key, "Content-Type": "application/json" },
        body: JSON.stringify({ model, messages, max_tokens: maxTokens, temperature }),
        signal: AbortSignal.timeout(45000),
      });
      if (!resp.ok) { last = `${name} HTTP ${resp.status}`; continue; }
      const j = await resp.json();
      const content = j?.choices?.[0]?.message?.content;
      if (content) return { content, provider: name };
      last = `${name} fără conținut`;
    } catch (e) { last = `${name} ${e}`; }
  }
  throw new Error("toți providerii au eșuat: " + last);
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
    return new Response(JSON.stringify({ error: String(e), content: "Momentan asistentul AI nu e disponibil. Încearcă din nou peste câteva momente sau verifică pe anaf.ro." }),
      { status: 200, headers: { ...CORS, "Content-Type": "application/json" } });
  }
});
