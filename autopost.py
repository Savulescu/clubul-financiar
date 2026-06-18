#!/usr/bin/env python3
"""Auto-poster Clubul Financiar — rulează în GitHub Actions (cron), gratis, în cloud.
Găsește postarea programată pentru AZI în schedule.json și o publică pe platformele
pentru care există SECRETS în GitHub. Tu nu uploadezi nimic — programul o face.

Acoperire:
  Telegram  ✅   (TELEGRAM_TOKEN, TELEGRAM_CHANNEL)
  Facebook  ✅   (FB_PAGE_ID, FB_PAGE_TOKEN)        -> postează prin URL public (raw GitHub)
  Instagram ⚙️   (IG_USER_ID, IG_TOKEN)             -> Graph API, video la URL public
  YouTube   ✅   (YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN) -> Data API v3, resumable upload (Short)
  TikTok    ⚙️   (TT_CLIENT_KEY, TT_CLIENT_SECRET, TT_REFRESH_TOKEN) -> semi-auto: urcă în inbox, publici din app
  X/Twitter ✅   (X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET) -> v2 media upload + tweet, 100% auto
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

def _parse_youtube(block):
    """Extrage TITLU + DESCRIERE din secțiunea YOUTUBE SHORT a caption-ului."""
    title = "Clubul Financiar — educație financiară"
    desc = ""
    mt = re.search(r"TITLU:\s*(.+)", block)
    if mt:
        title = mt.group(1).strip()
    md = re.search(r"DESCRIERE:\s*\n?(.+)", block, re.S)
    if md:
        desc = md.group(1).strip()
    else:
        desc = block.strip()
    return title, desc

def post_youtube(folder):
    cid = os.environ.get("YT_CLIENT_ID")
    csec = os.environ.get("YT_CLIENT_SECRET")
    rtok = os.environ.get("YT_REFRESH_TOKEN")
    if not (cid and csec and rtok):
        return log("  youtube: fără secrets, sar")
    # 1) refresh token -> access token
    tr = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": cid, "client_secret": csec,
        "refresh_token": rtok, "grant_type": "refresh_token"}, timeout=60)
    if not tr.ok:
        return log(f"  youtube: FAIL token {tr.text[:200]}")
    access = tr.json().get("access_token")
    if not access:
        return log("  youtube: FAIL token (fără access_token)")
    # 2) titlu + descriere din caption
    title, desc = _parse_youtube(caption(folder, "youtube"))
    video = os.path.join(ROOT, "media", folder, "reel.mp4")
    size = os.path.getsize(video)
    meta = {
        "snippet": {"title": title[:100], "description": desc[:4900], "categoryId": "27"},  # 27 = Education
        "status": {"privacyStatus": os.environ.get("YT_PRIVACY", "public"),
                   "selfDeclaredMadeForKids": False},
    }
    # 3) inițiază upload resumable
    init = requests.post(
        "https://www.googleapis.com/upload/youtube/v3/videos",
        params={"uploadType": "resumable", "part": "snippet,status"},
        headers={"Authorization": f"Bearer {access}",
                 "Content-Type": "application/json; charset=UTF-8",
                 "X-Upload-Content-Type": "video/*",
                 "X-Upload-Content-Length": str(size)},
        data=json.dumps(meta), timeout=60)
    location = init.headers.get("Location")
    if init.status_code not in (200, 201) or not location:
        return log(f"  youtube: FAIL init {init.status_code} {init.text[:200]}")
    # 4) urcă octeții video
    with open(video, "rb") as f:
        up = requests.put(location, headers={"Content-Type": "video/*",
                          "Content-Length": str(size)}, data=f, timeout=900)
    if up.ok:
        vid = up.json().get("id", "")
        log(f"  youtube: OK https://youtu.be/{vid}")
    else:
        log(f"  youtube: FAIL upload {up.status_code} {up.text[:200]}")

def post_tiktok(folder):
    """Semi-automat: urcă reel-ul în INBOX-ul TikTok (draft). Tu dai 'Publică' din app.
    Mod 'upload to inbox' (scope video.upload) — merge și înainte de auditul TikTok.
    Caption-ul îl pui tu în app la publicare (vezi secțiunea TIKTOK din captions/ziuaN.txt)."""
    ck = os.environ.get("TT_CLIENT_KEY")
    cs = os.environ.get("TT_CLIENT_SECRET")
    rt = os.environ.get("TT_REFRESH_TOKEN")
    if not (ck and cs and rt):
        return log("  tiktok: fără secrets, sar (semi-automat: ajunge în inbox-ul TikTok)")
    # 1) refresh -> access token
    tr = requests.post("https://open.tiktokapis.com/v2/oauth/token/",
                       headers={"Content-Type": "application/x-www-form-urlencoded"},
                       data={"client_key": ck, "client_secret": cs,
                             "grant_type": "refresh_token", "refresh_token": rt}, timeout=60)
    if not tr.ok or "access_token" not in tr.text:
        return log(f"  tiktok: FAIL token {tr.text[:200]}")
    access = tr.json()["access_token"]
    # 2) init upload (FILE_UPLOAD, un singur chunk)
    video = os.path.join(ROOT, "media", folder, "reel.mp4")
    size = os.path.getsize(video)
    init = requests.post("https://open.tiktokapis.com/v2/post/publish/inbox/video/init/",
                         headers={"Authorization": f"Bearer {access}",
                                  "Content-Type": "application/json; charset=UTF-8"},
                         data=json.dumps({"source_info": {
                             "source": "FILE_UPLOAD", "video_size": size,
                             "chunk_size": size, "total_chunk_count": 1}}), timeout=60)
    if not init.ok or "upload_url" not in init.text:
        return log(f"  tiktok: FAIL init {init.status_code} {init.text[:200]}")
    upload_url = init.json()["data"]["upload_url"]
    # 3) urcă octeții
    with open(video, "rb") as f:
        up = requests.put(upload_url, headers={
            "Content-Type": "video/mp4",
            "Content-Range": f"bytes 0-{size - 1}/{size}",
            "Content-Length": str(size)}, data=f, timeout=900)
    if up.ok:
        log("  tiktok: OK — video în inbox-ul TikTok; deschide app-ul și apasă Publică")
    else:
        log(f"  tiktok: FAIL upload {up.status_code} {up.text[:200]}")

def post_x(folder):
    """X / Twitter — postează video + text 100% automat.
    OAuth 1.0a User Context (4 chei generate din developer.x.com, fără flow).
    Upload video prin v2 chunked media upload (api.x.com/2/media/upload), apoi tweet v2.
    """
    ck = os.environ.get("X_API_KEY")
    cs = os.environ.get("X_API_SECRET")
    at = os.environ.get("X_ACCESS_TOKEN")
    ats = os.environ.get("X_ACCESS_SECRET")
    if not (ck and cs and at and ats):
        return log("  x: fără secrets, sar")
    try:
        from requests_oauthlib import OAuth1
    except ImportError:
        return log("  x: lipsește requests_oauthlib (adaugă-l în workflow)")
    auth = OAuth1(ck, cs, at, ats)
    video = os.path.join(ROOT, "media", folder, "reel.mp4")
    size = os.path.getsize(video)
    UPLOAD = "https://api.x.com/2/media/upload"
    # endpoint-ul v2 cere multipart/form-data (NU urlencoded) -> câmpurile ca (None, val)
    def mp(fields):
        return {k: (None, str(v)) for k, v in fields.items()}
    # 1) INIT
    init = requests.post(UPLOAD, auth=auth, files=mp({
        "command": "INIT", "total_bytes": size,
        "media_type": "video/mp4", "media_category": "tweet_video"}), timeout=60)
    if not init.ok:
        return log(f"  x: FAIL init {init.status_code} {init.text[:200]}")
    media_id = (init.json().get("data") or init.json()).get("id")
    if not media_id:
        return log(f"  x: FAIL init (fără media_id) {init.text[:200]}")
    # 2) APPEND (chunk-uri de 4MB, multipart cu binarul)
    CHUNK = 4 * 1024 * 1024
    with open(video, "rb") as f:
        idx = 0
        while True:
            buf = f.read(CHUNK)
            if not buf:
                break
            ap = requests.post(UPLOAD, auth=auth, files={
                "command": (None, "APPEND"), "media_id": (None, str(media_id)),
                "segment_index": (None, str(idx)),
                "media": ("chunk", buf, "application/octet-stream")}, timeout=300)
            if not ap.ok:
                return log(f"  x: FAIL append {idx} {ap.status_code} {ap.text[:200]}")
            idx += 1
    # 3) FINALIZE
    fin = requests.post(UPLOAD, auth=auth, files=mp({
        "command": "FINALIZE", "media_id": media_id}), timeout=60)
    if not fin.ok:
        return log(f"  x: FAIL finalize {fin.status_code} {fin.text[:200]}")
    # 4) așteaptă procesarea video (dacă e cazul)
    info = (fin.json().get("data") or fin.json()).get("processing_info")
    for _ in range(20):
        if not info or info.get("state") == "succeeded":
            break
        if info.get("state") == "failed":
            return log(f"  x: FAIL procesare {info}")
        time.sleep(max(info.get("check_after_secs", 5), 3))
        st = requests.get(UPLOAD, auth=auth,
                          params={"command": "STATUS", "media_id": media_id}, timeout=60)
        info = (st.json().get("data") or st.json()).get("processing_info")
    # 5) tweet cu media
    cap = caption(folder, "x")[:280]
    tw = requests.post("https://api.x.com/2/tweets", auth=auth,
                       json={"text": cap, "media": {"media_ids": [str(media_id)]}}, timeout=120)
    if tw.ok and (tw.json().get("data") or {}).get("id"):
        log(f"  x: OK https://x.com/i/status/{tw.json()['data']['id']}")
    else:
        log(f"  x: FAIL tweet {tw.status_code} {tw.text[:200]}")

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
    _t = os.environ.get("TELEGRAM_TOKEN", "")
    log(f"  [debug] TG_TOKEN prezent={bool(_t)} lungime={len(_t)} (corect=46) | "
        f"TG_CHANNEL={os.environ.get('TELEGRAM_CHANNEL')!r}")
    funcs = {"telegram": post_telegram, "facebook": post_facebook,
             "instagram": post_instagram, "youtube": post_youtube,
             "tiktok": post_tiktok, "x": post_x}
    for plat in entry["platforms"]:
        if plat in funcs:
            try:
                funcs[plat](folder)
            except Exception as e:
                log(f"  {plat}: EROARE {e}")

if __name__ == "__main__":
    main()
