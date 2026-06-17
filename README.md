# Clubul Financiar — Auto-poster (gratis, în cloud)

Postează singur, zilnic la 19:30 (ora României), pe **Telegram, Facebook, Instagram**
(YouTube se adaugă ulterior). **TikTok = manual** (API-ul lor cere aprobare de app).
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

## Conținut nou
Cere-i lui Claude un lot nou de postări → se adaugă în `media/` + `captions/` + `schedule.json` → push → cron-ul le postează singur.
