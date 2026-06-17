#!/usr/bin/env python3
"""Auto-poster Clubul Financiar — rulează în GitHub Actions (cron), gratis, în cloud.
Găsește postarea programată pentru AZI în schedule.json și o publică pe platformele
pentru care există SECRETS în GitHub. Tu nu uploadezi nimic — programul o face.

Acoperire:
  Telegram  ✅   (TELEGRAM_TOKEN, TELEGRAM_CHANNEL)
  Facebook  ✅   (FB_PAGE_ID, FB_PAGE_TOKEN)        -> postează prin URL public (raw GitHub)
  Instagram ⚙️   (IG_USER_ID, IG_TOKEN)             -> Graph API, video la URL public
  YouTube   ⚙️   (se adaugă ulterior, OAuth)
  TikTok    ❌   manual (API cere aprobare de app)
"""
import json, os, sys, datetime, re, time
import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("GITHUB_REPOSITORY", "")
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")
RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}" if REPO else ""

def log(m): print(m, flush=True)

def caption(folder, section):
    p = os.path.join(ROOT, "captions", f"{folder}.txt")
    if not os.path.exists(p):
        return ""
    parts = re.split(r"=== (.+?) ===\n", open(p, encoding="utf-8").read())
    for i in range(1, len(parts) - 1, 2):
        if section.lower() in parts[i].lower():
            return parts[i + 1].strip()
    return ""

def post_telegram(folder):
    tok, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHANNEL")
    if not (tok and chat):
        return log("  telegram: fără secrets, sar")
    video = os.path.join(ROOT, "media", folder, "reel.mp4")
    cap = caption(folder, "instagram")[:1000]
    with open(video, "rb") as f:
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendVideo",
                          data={"chat_id": chat, "caption": cap, "supports_streaming": True},
                          files={"video": f}, timeout=300)
    ok = r.ok and r.json().get("ok")
    log(f"  telegram: {'OK' if ok else 'FAIL ' + r.text[:200]}")

def post_facebook(folder):
    pid, tok = os.environ.get("FB_PAGE_ID"), os.environ.get("FB_PAGE_TOKEN")
    if not (pid and tok):
        return log("  facebook: fără secrets, sar")
    url = f"{RAW}/media/{folder}/reel.mp4"
    cap = caption(folder, "facebook")
    r = requests.post(f"https://graph.facebook.com/v21.0/{pid}/videos",
                      data={"file_url": url, "description": cap, "access_token": tok}, timeout=180)
    log(f"  facebook: {'OK' if r.ok and 'id' in r.text else 'FAIL ' + r.text[:200]}")

def post_instagram(folder):
    uid, tok = os.environ.get("IG_USER_ID"), os.environ.get("IG_TOKEN")
    if not (uid and tok):
        return log("  instagram: fără secrets, sar")
    url = f"{RAW}/media/{folder}/reel.mp4"
    cap = caption(folder, "instagram")
    # 1) container
    c = requests.post(f"https://graph.facebook.com/v21.0/{uid}/media",
                      data={"media_type": "REELS", "video_url": url, "caption": cap,
                            "access_token": tok}, timeout=120)
    if not c.ok or "id" not in c.text:
        return log(f"  instagram: FAIL container {c.text[:200]}")
    cid = c.json()["id"]
    # 2) așteaptă procesarea
    for _ in range(20):
        time.sleep(15)
        st = requests.get(f"https://graph.facebook.com/v21.0/{cid}",
                          params={"fields": "status_code", "access_token": tok}, timeout=60).json()
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") == "ERROR":
            return log("  instagram: FAIL procesare video")
    # 3) publish
    p = requests.post(f"https://graph.facebook.com/v21.0/{uid}/media_publish",
                      data={"creation_id": cid, "access_token": tok}, timeout=120)
    log(f"  instagram: {'OK' if p.ok and 'id' in p.text else 'FAIL ' + p.text[:200]}")

def main():
    sched = json.load(open(os.path.join(ROOT, "schedule.json")))
    today = datetime.date.today().isoformat()
    entry = next((e for e in sched if e["date"] == today), None)
    if not entry:
        # mod test: la rulare manuală (Run workflow) postează prima zi, ca să verifici că merge
        if os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch":
            entry = sched[0]
            log(f"TEST (rulare manuală): nimic azi, postez '{entry['folder']}' ca probă")
        else:
            return log(f"nimic programat azi ({today})")
    folder = entry["folder"]
    log(f"postez '{folder}' pentru {today}")
    funcs = {"telegram": post_telegram, "facebook": post_facebook, "instagram": post_instagram}
    for plat in entry["platforms"]:
        if plat in funcs:
            try:
                funcs[plat](folder)
            except Exception as e:
                log(f"  {plat}: EROARE {e}")
    log("  tiktok: manual (API cere aprobare)")

if __name__ == "__main__":
    main()
