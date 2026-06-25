# Fix definitiv: declanșare externă fiabilă (newsletter + știri externe)

**De ce:** cron-ul GitHub Actions sare/întârzie rulările programate (1-3h sau deloc).
Soluția care chiar merge: un scheduler extern (cron-job.org, gratuit) apelează API-ul
GitHub la ora fixă și pornește workflow-ul. Workflow-ul tot rulează pe GitHub (deci
secretele Resend/Supabase funcționează), dar **declanșarea** e fiabilă.

---

## PASUL 1 — Token GitHub (PAT fine-grained)

1. github.com → click pe poza ta (dreapta sus) → **Settings**
2. Jos în stânga → **Developer settings**
3. **Personal access tokens** → **Fine-grained tokens** → **Generate new token**
4. Completează:
   - **Token name:** `cron-job trigger`
   - **Expiration:** 1 an (sau „No expiration" dacă vrei să nu-l reînnoiești)
   - **Resource owner:** Savulescu (contul tău)
   - **Repository access:** „Only select repositories" → bifează **clubul-financiar**
   - **Permissions** → **Repository permissions** → găsește **Actions** → pune **Read and write**
     (Metadata: Read se adaugă automat — lasă așa)
5. **Generate token** → **COPIAZĂ token-ul ACUM** (se arată o singură dată!). Ține-l undeva safe.

---

## PASUL 2 — cron-job.org pentru NEWSLETTER (zilnic 07:30 RO)

1. Intră pe **cron-job.org** → creează cont gratuit (sau loghează-te)
2. **Create cronjob**
3. **Title:** `Newsletter CF 07:30`
4. **URL:**
   ```
   https://api.github.com/repos/Savulescu/clubul-financiar/actions/workflows/newsletter.yml/dispatches
   ```
5. **Schedule:** alege „Every day", ora **07:30**, iar la **Timezone** pune **Europe/Bucharest**
   (așa se ocupă singur de ora de vară/iarnă)
6. Deschide **Advanced settings** (sau „Request settings"):
   - **Request method:** `POST`
   - **Headers** (adaugă fiecare ca pereche cheie/valoare):
     | Key | Value |
     |---|---|
     | `Authorization` | `Bearer TOKENUL_TĂU` |
     | `Accept` | `application/vnd.github+json` |
     | `X-GitHub-Api-Version` | `2022-11-28` |
     | `Content-Type` | `application/json` |
   - **Request body:**
     ```json
     {"ref":"main"}
     ```
7. **Save**
8. Test: apasă **Run now** (sau „Test run"). Apoi verifică pe GitHub → **Actions** → „Newsletter"
   să apară o rulare nouă cu event **workflow_dispatch**. Dacă apare → merge ✅
   (răspuns API așteptat: HTTP **204 No Content** = succes.)

---

## PASUL 3 — cron-job.org pentru ȘTIRI EXTERNE (din 30 în 30 min)

La fel ca mai sus, dar:
- **Title:** `Stiri externe CF 30min`
- **URL:**
  ```
  https://api.github.com/repos/Savulescu/clubul-financiar/actions/workflows/externe.yml/dispatches
  ```
- **Schedule:** „Every 30 minutes" (sau custom: la minutul 0 și 30 al fiecărei ore)
- Restul (POST, headers cu același token, body `{"ref":"main"}`) — identic.

⚠️ Notă onestă: scriptul de știri are un **throttle intern** (~1,5-4h) ca să nu ardă cota
de LLM gratuit. Deci chiar dacă-l declanșezi din 30 în 30, va *aduce* știri noi la ~1,5-4h.
Dacă vrei cu adevărat mai des, spune-mi și reduc throttle-ul (cu riscul de cotă LLM).

---

## Verificare că funcționează
- Mâine dimineață la 07:30 RO → primești newsletterul.
- În GitHub → Actions → vezi rulări cu event **workflow_dispatch** (de la cron-job.org),
  nu doar „schedule".
- Dacă o rulare e roșie, deschide-o → pasul „Newsletter" → citește eroarea și trimite-mi-o.

## Dacă PAT-ul expiră
Refaci doar Pasul 1 și înlocuiești valoarea `Authorization` în cele 2 cronjob-uri.
