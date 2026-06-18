# Clubul Financiar — Auto-poster (gratis, în cloud)

Postează singur, zilnic la 19:30 (ora României), pe **Telegram, Facebook, Instagram, YouTube**
(Shorts) **și X/Twitter**. **TikTok = semi-manual** (API-ul lor cere aprobare de app).
Rulează gratis prin **GitHub Actions** — nu-ți trebuie calculatorul pornit.

## Cum funcționează
- `schedule.json` = ce postare se publică în ce zi
- `media/ziuaN/` = reel.mp4 + feed.png
- `captions/ziuaN.txt` = textul + hashtagurile per rețea
- `.github/workflows/autopost.yml` = cron-ul care rulează `autopost.py` zilnic
- Token-urile stau în **GitHub → Settings → Secrets**, NU în cod

## Setup (o singură dată)

### 1. Creează repo-ul (PUBLIC) și urcă fișierele
Public = necesar pentru ca Instagram/Facebook să vadă video-urile (URL public). Token-urile rămân sigure (sunt în Secrets, criptate).

### 2. Telegram (cel mai ușor — 5 min)
1. În Telegram, scrie lui **@BotFather** → `/newbot` → nume + username (ex. `clubulfinanciar_bot`) → copiază **TOKEN-ul**
2. Creează un **Canal** public (ex. `@clubulfinanciar`), adaugă botul ca **admin**
3. GitHub → repo → **Settings → Secrets and variables → Actions → New repository secret**:
   - `TELEGRAM_TOKEN` = token-ul de la BotFather
   - `TELEGRAM_CHANNEL` = `@clubulfinanciar`

### 3. Facebook (Pagină)
1. **developers.facebook.com** → create app (type: Business)
2. **Graph API Explorer** → permisiuni `pages_manage_posts`, `pages_read_engagement` → generează token de Pagină → schimbă-l în **token de lungă durată**
3. Secrets: `FB_PAGE_ID` (id-ul Paginii) + `FB_PAGE_TOKEN`

### 4. Instagram (Business, legat de Pagină)
Folosește aceeași app Meta. Permisiuni: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`.
- Secrets: `IG_USER_ID` (id-ul contului IG business) + `IG_TOKEN` (token de lungă durată)

### 5. Testează ACUM (fără să aștepți cron-ul)
GitHub → **Actions → Auto-post Clubul Financiar → Run workflow**.
Verifică log-ul. Dacă o zi e programată azi, postează; altfel scrie „nimic programat azi".

### 6. YouTube (Shorts) — autorizare o singură dată
Upload-ul pe YouTube cere OAuth (refresh token), nu doar o cheie. Se face o singură dată:
1. **console.cloud.google.com** → proiect nou → **APIs & Services → Library** → activează **YouTube Data API v3**
2. **OAuth consent screen** → External → adaugă-te ca *Test user* → scope `.../auth/youtube.upload`
3. **Credentials → Create OAuth client ID → Desktop app** → copiază Client ID + Client Secret
4. Local: `pip install requests && python3 get_youtube_token.py` → autorizează cu contul canalului → îți dă 3 valori
5. Secrets: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`
   - opțional `YT_PRIVACY` = `public` (implicit) / `unlisted` / `private`

Reel-urile verticale se urcă automat ca **Shorts**. Titlul + descrierea vin din secțiunea
`=== YOUTUBE SHORT ===` (TITLU / DESCRIERE) din `captions/ziuaN.txt`.

### 7. X / Twitter — 100% automat (OAuth 1.0a, fără flow)
Postează video + text singur. Nu are nevoie de script de autorizare ca YouTube — generezi direct 4 chei:
1. **developer.x.com** → Developer Portal → creează un **Project + App**
2. La App → **User authentication settings** → setează **App permissions = Read and write** (obligatoriu ca să poată posta) + tip OAuth 1.0a
3. La App → tab **Keys and tokens**:
   - **API Key** și **API Key Secret** (Consumer Keys)
   - **Access Token** și **Access Token Secret** → apasă **Generate** (asigură-te că arată „Read and Write"; dacă nu, regenerează după ce ai pus permisiunile la pasul 2)
4. Secrets în GitHub:
   - `X_API_KEY` = API Key
   - `X_API_SECRET` = API Key Secret
   - `X_ACCESS_TOKEN` = Access Token
   - `X_ACCESS_SECRET` = Access Token Secret

Textul vine din secțiunea `=== X ===` din `captions/ziuaN.txt` (limitat la 280 caractere).
Notă: pe planul **Free** al X API ai ~500 postări/lună — mai mult decât suficient pentru o postare/zi.

## Conținut nou
Cere-i lui Claude un lot nou de postări → se adaugă în `media/` + `captions/` + `schedule.json` → push → cron-ul le postează singur.
