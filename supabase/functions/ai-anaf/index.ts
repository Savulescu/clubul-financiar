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

// Promptul AUTORITATIV trăiește în docs/assets/ai-anaf-prompt.txt (editezi acolo + push, FĂRĂ re-deploy).
// Cel de mai jos e doar FALLBACK dacă fetch-ul fișierului eșuează.
const PROMPT_URL = "https://clubulfinanciar.ro/assets/ai-anaf-prompt.txt";
let _promptCache: { text: string; ts: number } = { text: "", ts: 0 };
async function getSystem(): Promise<string> {
  const now = Date.now();
  if (_promptCache.text && now - _promptCache.ts < 300000) return _promptCache.text; // cache 5 min
  try {
    const r = await fetch(PROMPT_URL, { signal: AbortSignal.timeout(5000) });
    if (r.ok) {
      const t = (await r.text()).trim();
      if (t.length > 300) { _promptCache = { text: t, ts: now }; return t; }
    }
  } catch (_e) { /* fallback */ }
  return _promptCache.text || FALLBACK_SYSTEM;
}

// ---- RAG: bază de cunoștințe verificată (glosar + concepte lecții + constante) ----
// Editezi docs/assets/ai-knowledge.json + push → se actualizează în ≤5 min, FĂRĂ re-deploy.
const KB_URL = "https://clubulfinanciar.ro/assets/ai-knowledge.json";
let _kbCache: { data: any[]; ts: number } = { data: [], ts: 0 };
async function getKnowledge(): Promise<any[]> {
  const now = Date.now();
  if (_kbCache.data.length && now - _kbCache.ts < 300000) return _kbCache.data;
  try {
    const r = await fetch(KB_URL, { signal: AbortSignal.timeout(6000) });
    if (r.ok) { const d = await r.json(); if (Array.isArray(d) && d.length) { _kbCache = { data: d, ts: now }; return d; } }
  } catch (_e) { /* fallback */ }
  return _kbCache.data;
}
// normalizare diacritic-insensitivă (trebuie să fie IDENTICĂ cu _norm din _build_ai_knowledge.py)
function norm(s: string): string {
  return String(s).toLowerCase()
    .replace(/[ăâ]/g, "a").replace(/î/g, "i").replace(/[șş]/g, "s").replace(/[țţ]/g, "t");
}
// rădăcini de 6 caractere → potrivire diacritic-insensitiv + forme de cuvânt (taxare/taxarea)
function tokenize(s: string): string[] {
  return (norm(s).match(/[a-z0-9]{4,}/g) || []).map((w) => w.slice(0, 6));
}
// scor simplu prin suprapunere de rădăcini; întoarce top-k intrări relevante
function retrieve(question: string, kb: any[], k = 6): any[] {
  const qt = new Set(tokenize(question));
  if (!qt.size || !kb.length) return [];
  const scored = kb.map((e) => {
    let sc = 0;
    for (const w of (e.k || [])) if (qt.has(w)) sc += 2;
    const xl = norm(e.x || "");
    for (const w of qt) if (xl.includes(w)) sc += 1;
    return { e, sc };
  }).filter((x) => x.sc >= 3).sort((a, b) => b.sc - a.sc).slice(0, k);
  return scored.map((x) => x.e);
}

const FALLBACK_SYSTEM = `Ești "Asistentul ANAF" al Clubul Financiar — un ghid fiscal prietenos pentru România, actualizat la legislația 2026.

REGULI DE FIER:
1. Răspunzi pe fiscalitate, finanțe personale ȘI contabilitate din România (ANAF, Declarația Unică, PFA, SRL, micro, TVA, CASS, CAS, impozite, chirii, dividende, investiții, crypto, credite, pensii, plus contabilitate: plan de conturi, balanță, bilanț, înregistrări de partidă dublă, debit/credit, amortizare). Ești expert și pe contabilitate românească.
2. Ești EDUCATIV, nu dai consultanță fiscală oficială și nu înlocuiești un contabil sau ANAF. Pentru sume mari/decizii ireversibile spui mereu să verifice pe anaf.ro sau cu un contabil.
3. NICIODATĂ nu recomanzi instrumente de investiție concrete ("cumpără acțiunea X", "investește în Y") — e linie roșie ASF. Explici educativ, atât.
4. Răspunzi în română, clar și bine structurat, cu cifre concrete în lei. Poți da răspunsuri detaliate (pași, liste, tabele) când subiectul cere. Folosește DOAR Markdown simplu (tabele cu „|" și rând separator „|---|", liste cu „-" sau „1."). NU folosi HTML în răspuns — fără <br>, <div>, <b> etc.; pentru mai multe linii într-o celulă de tabel, scrie text scurt sau folosește o listă în afara tabelului. Ține celulele de tabel scurte (o singură linie). FOARTE IMPORTANT: termină ÎNTOTDEAUNA răspunsul complet — nu-l lăsa la jumătate. Dacă subiectul e foarte vast, fă-l mai compact ca să încapă întreg, sau încheie secțiunea curentă curat și oferă să continui la cerere („Vrei să continui cu partea despre X?").
5. Dacă întrebarea nu e despre fiscalitate/finanțe RO, refuzi politicos și redirecționezi.
6. FORMATARE TABELE: lasă un rând gol înainte de fiecare tabel și pune titlul (###) pe rândul lui — NU lipi titlul de tabel pe același rând.
7. CONTABILITATE: dă numere de cont CORECTE din Planul de conturi românesc (OMFP 1802/2014) — folosește referința de mai jos, NU inventa coduri. Dacă un cont nu e în referință și nu ești sigur, spune clar „verifică în planul oficial de conturi" în loc să ghicești. La cazuri complexe recomandă și un contabil, dar oferă informația corectă. Atenție la confuziile frecvente: Mărfuri = 371 (NU 301); Materii prime = 301; Clienți = 411; Furnizori = 401; Casa = 5311; Bancă în lei = 5121; TVA de plată = 4423; TVA colectată = 4427; TVA deductibilă = 4426.

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

PLAN DE CONTURI RO (OMFP 1802/2014) — principalele conturi (folosește EXACT aceste coduri, nu inventa altele):
- Clasa 1 Capitaluri: 101 Capital · 105 Rezerve din reevaluare · 106 Rezerve · 117 Rezultatul reportat · 121 Profit sau pierdere · 129 Repartizarea profitului · 151 Provizioane · 162 Credite bancare pe termen lung · 167 Alte împrumuturi și datorii asimilate · 168 Dobânzi aferente împrumuturilor.
- Clasa 2 Imobilizări: 201 Cheltuieli de constituire · 203 Cheltuieli de dezvoltare · 205 Concesiuni/brevete/licențe · 208 Alte imob. necorporale · 211 Terenuri și amenajări · 212 Construcții · 213 Instalații tehnice și mijloace de transport · 214 Mobilier/birotică · 231 Imobilizări corporale în curs · 261 Acțiuni la entități afiliate · 267 Creanțe imobilizate · 280 Amortizări imob. necorporale · 281 Amortizări imob. corporale.
- Clasa 3 Stocuri: 301 Materii prime · 302 Materiale consumabile · 303 Obiecte de inventar · 331 Producție în curs · 345 Produse finite · 371 Mărfuri · 378 Diferențe de preț la mărfuri · 381 Ambalaje · 397/398 Ajustări.
- Clasa 4 Terți: 401 Furnizori · 404 Furnizori de imobilizări · 408 Furnizori - facturi nesosite · 411 Clienți · 418 Clienți - facturi de întocmit · 419 Clienți-creditori · 421 Personal - salarii datorate · 425 Avansuri personal · 4315 CAS (asigurări sociale) · 4316 CASS (sănătate) · 436 CAM (contribuția asiguratorie pentru muncă) · 441 Impozit pe profit/venit · 444 Impozit pe venituri din salarii · 4423 TVA de plată · 4424 TVA de recuperat · 4426 TVA deductibilă · 4427 TVA colectată · 4428 TVA neexigibilă · 446 Alte impozite și taxe · 461 Debitori diverși · 462 Creditori diverși.
- Clasa 5 Trezorerie: 5121 Conturi la bănci în lei · 5124 Conturi la bănci în valută · 5311 Casa în lei · 5314 Casa în valută · 542 Avansuri de trezorerie · 581 Viramente interne.
- Clasa 6 Cheltuieli: 601 Materii prime · 607 Mărfuri · 611-628 Servicii executate de terți · 635 Alte impozite și taxe · 641 Salarii · 646 CAM · 665 Diferențe de curs valutar · 666 Dobânzi · 681 Amortizări și ajustări · 691 Impozit pe profit · 698 Impozit pe venit (microîntreprinderi).
- Clasa 7 Venituri: 701 Produse finite · 704 Servicii prestate · 707 Mărfuri · 758 Alte venituri din exploatare · 766 Venituri din dobânzi.
Reguli contabile cheie: balanța/bilanțul respectă Activ = Datorii + Capitaluri proprii; partidă dublă = orice operație are debit = credit. Pentru planul complet, trimite la OMFP 1802/2014.

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
async function chat(messages: any[], maxTokens = 4000, temperature = 0.4) {
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
    const { messages, context, maxTokens } = await req.json();
    if (!Array.isArray(messages) || !messages.length) {
      return new Response(JSON.stringify({ error: "messages required" }), { status: 400, headers: { ...CORS, "Content-Type": "application/json" } });
    }
    // Limită de output reglabilă din frontend (default 4000, max 6000) — fără re-deploy la viitoare ajustări.
    const mt = Math.min(Math.max(parseInt(maxTokens, 10) || 4000, 256), 6000);
    const baseSystem = await getSystem();
    // RAG: caută surse verificate pentru ultima întrebare a utilizatorului și injectează-le
    const lastQ = [...messages].reverse().find((m: any) => m.role !== "assistant")?.content
                  || messages[messages.length - 1]?.content || "";
    let kbBlock = "";
    try {
      const kb = await getKnowledge();
      const hits = retrieve(String(lastQ), kb, 6);
      if (hits.length) {
        kbBlock = "\n\n=== SURSE VERIFICATE (din conținutul fact-checkat Clubul Financiar — TRATEAZĂ-LE CA ADEVĂR, citează cifrele de aici; dacă răspunsul NU se află în aceste surse și nu ești 100% sigur, spune clar să verifice pe anaf.ro sau cu un contabil — NU inventa cifre/articole) ===\n"
          + hits.map((h: any, i: number) => `[${i + 1}] ${h.x}`).join("\n");
      }
    } catch (_e) { /* fără RAG dacă pică */ }
    const sys = baseSystem + kbBlock + (context ? `\n\nContextul utilizatorului (cifrele lui, folosește-le): ${JSON.stringify(context)}` : "");
    const trimmed = messages.slice(-12).map((m: any) => ({
      role: m.role === "assistant" ? "assistant" : "user",
      content: String(m.content || "").slice(0, 4000),
    }));
    const out = await chat([{ role: "system", content: sys }, ...trimmed], mt);
    return new Response(JSON.stringify(out), { headers: { ...CORS, "Content-Type": "application/json" } });
  } catch (e) {
    const fallback = `Momentan asistentul AI nu e disponibil. Încearcă din nou peste câteva momente sau verifică pe anaf.ro.`;
    return new Response(JSON.stringify({ error: String(e), content: fallback }),
      { status: 200, headers: { ...CORS, "Content-Type": "application/json" } });
  }
});
