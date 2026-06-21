# Deploy Hub Fiscal — runbook (o singură dată)

Uneltele Pro funcționează ca site static. Ca să meargă **backend-ul** (tier real, logare cross-device, AI ANAF, remindere), rulează pașii de mai jos. Frontend-ul degradează grațios dacă un pas lipsește.

## 1. Tabele Supabase (logare + abonamente + remindere)
Supabase → proiectul `maumjqciuxdbwjtvcpsy` → **SQL Editor** → New query → lipește conținutul din
`supabase/schema_hub_fiscal.sql` → **Run**. (idempotent, poate fi rulat de mai multe ori)

## 2. Asistentul ANAF (AI) — Edge Function cu cheile StockCap
Cheile sunt deja în GitHub Secrets ale StockCap. Le setezi o dată ca secrete Supabase (aceleași valori):

```bash
# instalează CLI dacă nu există: brew install supabase/tap/supabase
supabase login
supabase link --project-ref maumjqciuxdbwjtvcpsy

# setează cheile (aceleași ca în StockCap — pune valorile reale):
supabase secrets set \
  CEREBRAS_API_KEY=... GROQ_API_KEY=... GEMINI_API_KEY=... MISTRAL_API_KEY=... \
  TOGETHER_API_KEY=... DEEPSEEK_API_KEY=... SAMBANOVA_API_KEY=... OPENROUTER_API_KEY=... \
  NVIDIA_API_KEY=... FIREWORKS_API_KEY=... SILICONFLOW_API_KEY=...

# deploy funcția
supabase functions deploy ai-anaf --no-verify-jwt
```
Endpoint rezultat: `https://maumjqciuxdbwjtvcpsy.functions.supabase.co/ai-anaf`
(este deja cablat în `docs/assets/cf-tool.js` → `CF.AI_ENDPOINT`).

Test rapid:
```bash
curl -s -X POST https://maumjqciuxdbwjtvcpsy.functions.supabase.co/ai-anaf \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Cat platesc ca PFA la 100000 lei venit net?"}]}'
```

## 3. Remindere lunare (Telegram/email) — GitHub Actions
Workflow-ul `.github/workflows/reminders.yml` rulează zilnic 09:00 RO. Adaugă în GitHub Secrets:
- `SUPABASE_SERVICE_KEY` — service_role key (Supabase → Settings → API). **Doar pe server, niciodată în frontend.**
- `TELEGRAM_TOKEN` — deja există (auto-poster).
- (opțional) `RESEND_API_KEY` + `REMINDER_FROM` pentru email.

## 4. Stripe (facturare reală) — ultimul pas, separat
Tier-ul real se citește din tabelul `subscriptions`. Ca să-l populeze automat:
1. Creează produsele/prețurile în Stripe (Premium 49/490, Pro 99/990, Ultra 199/1990 lei).
2. Edge Function `stripe-webhook` (de construit) care la `checkout.session.completed` /
   `customer.subscription.updated` face `upsert` în `subscriptions` (tier, status, current_period_end)
   folosind `SUPABASE_SERVICE_KEY`.
3. Buton „Abonează-te" pe `/premium.html` → Stripe Checkout.
Până atunci: adminul (`clubulfinanciar@gmail.com`) are tier `ultra` automat, deci poți testa tot.

## Verificare end-to-end
- Logat ca admin → toate uneltele deblocate (gating pe tier funcționează).
- AI ANAF răspunde (după pasul 2).
- Loghezi o lună în „Radar plafon TVA" → reapare după re-login pe alt device (după pasul 1).
- La 1 ale lunii primești reminder pe Telegram (după pasul 3, dacă ai `telegram_chat_id` setat).
