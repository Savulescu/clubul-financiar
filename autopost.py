#!/usr/bin/env python3
"""Auto-poster Clubul Financiar — rulează în GitHub Actions (cron), gratis, în cloud.
Găsește postarea programată pentru AZI în schedule.json și o publică pe platformele
pentru care există SECRETS în GitHub. Tu nu uploadezi nimic — programul o face.

Acoperire:
  Telegram  ✅   (TELEGRAM_TOKEN, TELEGRAM_CHANNEL)
  Facebook  ✅   (FB_PAGE_ID, FB_PAGE_TOKEN)        -> REEL (fallback video) + Facebook Story video
  IG Story  ✅   (IG_USER_ID, IG_TOKEN)             -> Instagram Story video (media_type=STORIES)
  FB Story  ✅   (FB_PAGE_ID, FB_PAGE_TOKEN)        -> /video_stories (3 faze)
  Instagram ⚙️   (IG_USER_ID, IG_TOKEN)             -> Graph API, video la URL public
  YouTube   ✅   (YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN) -> Data API v3, resumable upload (Short)
  TikTok    ⚙️   (TT_CLIENT_KEY, TT_CLIENT_SECRET, TT_REFRESH_TOKEN) -> semi-auto: urcă în inbox, publici din app
  X/Twitter ✅   (X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET) -> v2 media upload + tweet, 100% auto
  Threads   ✅   (THREADS_USER_ID, THREADS_TOKEN)   -> graph.threads.net, container video + publish, 100% auto
  Reddit    ✅   (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD, REDDIT_SUBREDDIT) -> video în subreddit propriu, 100% auto
  LinkedIn  ✅   (LINKEDIN_TOKEN, LINKEDIN_PERSON_URN)  -> Videos API + Posts API pe profil personal, 100% auto
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
    cap = (caption(folder, "telegram") or caption(folder, "instagram"))[:1000]
    with open(video, "rb") as f:
        r = requests.post(f"https://api.telegram.org/bot{tok}/sendVideo",
                          data={"chat_id": chat, "caption": cap, "supports_streaming": True},
                          files={"video": f}, timeout=300)
    ok = r.ok and r.json().get("ok")
    log(f"  telegram: {'OK' if ok else 'FAIL ' + r.text[:200]}")

def post_facebook(folder):
    """Facebook — postează ca REEL (reach mai mare), cu fallback la video normal dacă reel-ul pică."""
    pid, tok = os.environ.get("FB_PAGE_ID"), os.environ.get("FB_PAGE_TOKEN")
    if not (pid and tok):
        return log("  facebook: fără secrets, sar")
    url = f"{RAW}/media/{folder}/reel.mp4"
    desc = caption(folder, "facebook")
    G = "https://graph.facebook.com/v21.0"
    # întâi REEL (3 faze: start -> upload prin file_url -> finish)
    try:
        s = requests.post(f"{G}/{pid}/video_reels",
                          data={"upload_phase": "start", "access_token": tok}, timeout=60).json()
        vid, up = s.get("video_id"), s.get("upload_url")
        if vid and up:
            ru = requests.post(up, headers={"Authorization": f"OAuth {tok}", "file_url": url}, timeout=300)
            if ru.ok:
                fin = requests.post(f"{G}/{pid}/video_reels",
                                    data={"upload_phase": "finish", "video_id": vid,
                                          "video_state": "PUBLISHED", "description": desc,
                                          "access_token": tok}, timeout=120)
                if fin.ok and fin.json().get("success", True):
                    return log("  facebook: OK (reel)")
            log(f"  facebook: reel eșuat ({ru.status_code}), fallback video")
        else:
            log(f"  facebook: reel start eșuat ({s}), fallback video")
    except Exception as e:
        log(f"  facebook: reel eroare ({e}), fallback video")
    # fallback: video normal
    r = requests.post(f"{G}/{pid}/videos",
                      data={"file_url": url, "description": desc, "access_token": tok}, timeout=180)
    log(f"  facebook: {'OK (video)' if r.ok and 'id' in r.text else 'FAIL ' + r.text[:200]}")

def post_facebook_story(folder):
    """Facebook Story video (3 faze ca la reels, fără descriere — story-urile sunt vizuale)."""
    pid, tok = os.environ.get("FB_PAGE_ID"), os.environ.get("FB_PAGE_TOKEN")
    if not (pid and tok):
        return log("  fb_story: fără secrets, sar")
    url = f"{RAW}/media/{folder}/reel.mp4"
    G = "https://graph.facebook.com/v21.0"
    s = requests.post(f"{G}/{pid}/video_stories",
                      data={"upload_phase": "start", "access_token": tok}, timeout=60).json()
    vid, up = s.get("video_id"), s.get("upload_url")
    if not (vid and up):
        return log(f"  fb_story: FAIL start {s}")
    ru = requests.post(up, headers={"Authorization": f"OAuth {tok}", "file_url": url}, timeout=300)
    if not ru.ok:
        return log(f"  fb_story: FAIL upload {ru.status_code} {ru.text[:150]}")
    fin = requests.post(f"{G}/{pid}/video_stories",
                        data={"upload_phase": "finish", "video_id": vid, "access_token": tok}, timeout=120)
    log(f"  fb_story: {'OK' if fin.ok else 'FAIL ' + fin.text[:200]}")

def post_instagram_story(folder):
    """Instagram Story video (container media_type=STORIES -> procesare -> publish)."""
    uid, tok = os.environ.get("IG_USER_ID"), os.environ.get("IG_TOKEN")
    if not (uid and tok):
        return log("  ig_story: fără secrets, sar")
    url = f"{RAW}/media/{folder}/reel.mp4"
    G = "https://graph.facebook.com/v21.0"
    c = requests.post(f"{G}/{uid}/media",
                      data={"media_type": "STORIES", "video_url": url, "access_token": tok}, timeout=120)
    if not c.ok or "id" not in c.text:
        return log(f"  ig_story: FAIL container {c.text[:200]}")
    cid = c.json()["id"]
    for _ in range(20):
        time.sleep(15)
        st = requests.get(f"{G}/{cid}", params={"fields": "status_code", "access_token": tok}, timeout=60).json()
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") == "ERROR":
            return log("  ig_story: FAIL procesare")
    p = requests.post(f"{G}/{uid}/media_publish",
                      data={"creation_id": cid, "access_token": tok}, timeout=120)
    log(f"  ig_story: {'OK' if p.ok and 'id' in p.text else 'FAIL ' + p.text[:200]}")

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
    # 2) titlu + descriere + tag-uri din caption (tag-urile ajută la căutare/recomandări)
    title, desc = _parse_youtube(caption(folder, "youtube"))
    tags = [t for t in re.findall(r"#(\w+)", caption(folder, "youtube"))
            if not t.isdigit() and len(t) > 1]
    tags = list(dict.fromkeys(tags + ["educatie financiara", "finante personale",
                                       "bani", "Romania", "Clubul Financiar"]))[:15]
    video = os.path.join(ROOT, "media", folder, "reel.mp4")
    size = os.path.getsize(video)
    meta = {
        "snippet": {"title": title[:100], "description": desc[:4900], "categoryId": "27",  # 27 = Education
                    "tags": tags},
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

def post_threads(folder):
    """Threads (Meta) — 100% automat. Flux ca la Instagram: container video -> procesare -> publish.
    graph.threads.net, scope threads_basic + threads_content_publish, text max 500."""
    uid, tok = os.environ.get("THREADS_USER_ID"), os.environ.get("THREADS_TOKEN")
    if not (uid and tok):
        return log("  threads: fără secrets, sar")
    url = f"{RAW}/media/{folder}/reel.mp4"
    text = (caption(folder, "threads") or caption(folder, "instagram"))[:500]
    G = "https://graph.threads.net/v1.0"
    # 1) container video
    c = requests.post(f"{G}/{uid}/threads",
                      data={"media_type": "VIDEO", "video_url": url, "text": text,
                            "access_token": tok}, timeout=120)
    if not c.ok or "id" not in c.text:
        return log(f"  threads: FAIL container {c.text[:200]}")
    cid = c.json()["id"]
    # 2) așteaptă procesarea (video = asincron; min ~30s recomandat)
    for _ in range(20):
        time.sleep(15)
        st = requests.get(f"{G}/{cid}",
                          params={"fields": "status", "access_token": tok}, timeout=60).json()
        if st.get("status") == "FINISHED":
            break
        if st.get("status") == "ERROR":
            return log(f"  threads: FAIL procesare {st}")
    # 3) publish
    p = requests.post(f"{G}/{uid}/threads_publish",
                      data={"creation_id": cid, "access_token": tok}, timeout=120)
    log(f"  threads: {'OK' if p.ok and 'id' in p.text else 'FAIL ' + p.text[:200]}")

def post_linkedin(folder):
    """LinkedIn — postează video pe profil personal. 100% automat.
    Videos API (initialize/upload/finalize) + Posts API. Token expiră în 60 zile."""
    tok = os.environ.get("LINKEDIN_TOKEN")
    urn = os.environ.get("LINKEDIN_PERSON_URN")  # urn:li:person:XXXX
    if not (tok and urn):
        return log("  linkedin: fără secrets, sar")
    VER = os.environ.get("LINKEDIN_VERSION", "202409")
    H = {"Authorization": f"Bearer {tok}", "LinkedIn-Version": VER,
         "X-Restli-Protocol-Version": "2.0.0"}
    JH = {**H, "Content-Type": "application/json"}
    video = os.path.join(ROOT, "media", folder, "reel.mp4")
    with open(video, "rb") as f:
        data = f.read()
    size = len(data)
    # 1) initialize upload
    init = requests.post("https://api.linkedin.com/rest/videos?action=initializeUpload", headers=JH,
                         data=json.dumps({"initializeUploadRequest": {
                             "owner": urn, "fileSizeBytes": size,
                             "uploadCaptions": False, "uploadThumbnail": False}}), timeout=60)
    if not init.ok:
        return log(f"  linkedin: FAIL init {init.status_code} {init.text[:200]}")
    val = init.json()["value"]
    video_urn = val["video"]
    upload_token = val.get("uploadToken", "")
    # 2) upload părți (după byte-range), strânge ETag-urile
    etags = []
    for ins in val["uploadInstructions"]:
        fb, lb = ins["firstByte"], ins["lastByte"]
        up = requests.put(ins["uploadUrl"], data=data[fb:lb + 1],
                          headers={"Content-Type": "application/octet-stream"}, timeout=600)
        if up.status_code not in (200, 201):
            return log(f"  linkedin: FAIL upload {up.status_code} {up.text[:120]}")
        etags.append(up.headers.get("etag", "").strip('"'))
    # 3) finalize
    fin = requests.post("https://api.linkedin.com/rest/videos?action=finalizeUpload", headers=JH,
                        data=json.dumps({"finalizeUploadRequest": {
                            "video": video_urn, "uploadToken": upload_token,
                            "uploadedPartIds": etags}}), timeout=60)
    if not fin.ok:
        return log(f"  linkedin: FAIL finalize {fin.status_code} {fin.text[:200]}")
    # 4) așteaptă procesarea video (AVAILABLE)
    enc = requests.utils.quote(video_urn, safe="")
    for _ in range(20):
        time.sleep(15)
        s = requests.get(f"https://api.linkedin.com/rest/videos/{enc}", headers=H, timeout=60)
        stt = s.json().get("status") if s.ok else None
        if stt in ("AVAILABLE", "PROCESSING_FAILED"):
            break
    # 5) creează postarea
    text = caption(folder, "linkedin")[:2900]
    post = requests.post("https://api.linkedin.com/rest/posts", headers=JH, data=json.dumps({
        "author": urn, "commentary": text, "visibility": "PUBLIC",
        "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [],
                         "thirdPartyDistributionChannels": []},
        "content": {"media": {"title": "Clubul Financiar", "id": video_urn}},
        "lifecycleState": "PUBLISHED", "isReshareDisabledByAuthor": False}), timeout=120)
    log(f"  linkedin: {'OK' if post.status_code in (200, 201) else 'FAIL ' + str(post.status_code) + ' ' + post.text[:200]}")

def post_reddit(folder):
    """Reddit — postează video în subreddit-ul propriu (r/REDDIT_SUBREDDIT). 100% automat.
    OAuth2 password grant (app tip 'script'). Upload video + poster în media Reddit, apoi submit kind=video.
    Titlul = TITLU din secțiunea YOUTUBE SHORT a caption-ului."""
    cid = os.environ.get("REDDIT_CLIENT_ID")
    csec = os.environ.get("REDDIT_CLIENT_SECRET")
    user = os.environ.get("REDDIT_USERNAME")
    pw = os.environ.get("REDDIT_PASSWORD")
    sub = os.environ.get("REDDIT_SUBREDDIT", "ClubulFinanciar")
    if not (cid and csec and user and pw):
        return log("  reddit: fără secrets, sar")
    UA = f"clubulfinanciar-autoposter/1.0 by u/{user}"
    # 1) access token (password grant)
    tr = requests.post("https://www.reddit.com/api/v1/access_token", auth=(cid, csec),
                       data={"grant_type": "password", "username": user, "password": pw},
                       headers={"User-Agent": UA}, timeout=60)
    if not tr.ok or "access_token" not in tr.text:
        return log(f"  reddit: FAIL token {tr.status_code} {tr.text[:200]}")
    H = {"Authorization": f"Bearer {tr.json()['access_token']}", "User-Agent": UA}
    # helper: urcă un fișier în media Reddit (S3) -> întoarce URL-ul public
    def upload(path, mimetype):
        fn = os.path.basename(path)
        lease = requests.post("https://oauth.reddit.com/api/media/asset.json", headers=H,
                              data={"filepath": fn, "mimetype": mimetype}, timeout=60)
        if not lease.ok:
            return None
        a = lease.json()["args"]
        action = a["action"]
        action = ("https:" + action) if action.startswith("//") else action
        fields = {f["name"]: f["value"] for f in a["fields"]}
        with open(path, "rb") as fh:
            up = requests.post(action, data=fields, files={"file": (fn, fh, mimetype)}, timeout=600)
        if up.status_code not in (200, 201, 204):
            return None
        return f"{action}/{fields['key']}"
    video_url = upload(os.path.join(ROOT, "media", folder, "reel.mp4"), "video/mp4")
    poster_url = upload(os.path.join(ROOT, "media", folder, "feed.png"), "image/png")
    if not (video_url and poster_url):
        return log("  reddit: FAIL upload media")
    title = _parse_youtube(caption(folder, "youtube"))[0]
    sb = requests.post("https://oauth.reddit.com/api/submit", headers=H, data={
        "sr": sub, "kind": "video", "title": title[:300], "url": video_url,
        "video_poster_url": poster_url, "api_type": "json", "resubmit": "true",
        "sendreplies": "false"}, timeout=120)
    try:
        errs = sb.json().get("json", {}).get("errors", [])
    except Exception:
        errs = [["PARSE", sb.text[:120]]]
    log(f"  reddit: {'OK' if sb.ok and not errs else 'FAIL ' + str(errs or sb.text[:200])}")

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
    # v2 chunked upload prin endpoint-urile dedicate (initialize/append/finalize)
    # 1) initialize (JSON) -> media_id
    init = requests.post(UPLOAD + "/initialize", auth=auth, json={
        "media_category": "tweet_video", "media_type": "video/mp4",
        "total_bytes": size}, timeout=60)
    if not init.ok:
        return log(f"  x: FAIL initialize {init.status_code} {init.text[:200]}")
    media_id = init.json()["data"]["id"]
    # 2) append (chunk-uri de 4MB, multipart cu binarul)
    CHUNK = 4 * 1024 * 1024
    with open(video, "rb") as f:
        idx = 0
        while True:
            buf = f.read(CHUNK)
            if not buf:
                break
            ap = requests.post(f"{UPLOAD}/{media_id}/append", auth=auth,
                               data={"segment_index": idx},
                               files={"media": ("chunk", buf, "application/octet-stream")},
                               timeout=300)
            if not ap.ok:
                return log(f"  x: FAIL append {idx} {ap.status_code} {ap.text[:200]}")
            idx += 1
    # 3) finalize
    fin = requests.post(f"{UPLOAD}/{media_id}/finalize", auth=auth, timeout=60)
    if not fin.ok:
        return log(f"  x: FAIL finalize {fin.status_code} {fin.text[:200]}")
    # 4) așteaptă procesarea video (dacă e cazul)
    info = (fin.json().get("data") or {}).get("processing_info")
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
             "tiktok": post_tiktok, "x": post_x, "threads": post_threads,
             "reddit": post_reddit, "linkedin": post_linkedin,
             "facebook_story": post_facebook_story, "instagram_story": post_instagram_story}
    for plat in entry["platforms"]:
        if plat in funcs:
            try:
                funcs[plat](folder)
            except Exception as e:
                log(f"  {plat}: EROARE {e}")

if __name__ == "__main__":
    main()
