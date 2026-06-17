#!/usr/bin/env python3
"""Obține un YT_REFRESH_TOKEN pentru upload automat pe YouTube — se rulează O SINGURĂ DATĂ, local.

Pași (o singură dată):
  1. https://console.cloud.google.com → creează un proiect (sau folosește unul existent)
  2. APIs & Services → Library → caută „YouTube Data API v3" → ENABLE
  3. APIs & Services → OAuth consent screen → User type: External → completează datele,
     adaugă-te ca Test user (email-ul tău), scope: .../auth/youtube.upload
  4. APIs & Services → Credentials → Create Credentials → OAuth client ID →
     Application type: **Desktop app** → copiază Client ID + Client Secret
  5. Rulează:  python3 get_youtube_token.py
     Lipește Client ID + Secret când le cere, autorizează în browser cu contul
     canalului YouTube Clubul Financiar.
  6. Scriptul îți afișează 3 valori. Le pui în GitHub:
     repo → Settings → Secrets and variables → Actions → New repository secret:
        YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN

Necesită doar `requests` (pip install requests). Nimic altceva.
"""
import http.server
import socketserver
import threading
import urllib.parse
import webbrowser
import sys

try:
    import requests
except ImportError:
    sys.exit("Lipsește 'requests'. Rulează: pip install requests")

SCOPE = "https://www.googleapis.com/auth/youtube.upload"
PORT = 8765
REDIRECT = f"http://localhost:{PORT}/"

_code = {}

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(q)
        _code["code"] = params.get("code", [None])[0]
        _code["error"] = params.get("error", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        msg = "✅ Autorizat. Poți închide fila și te întorci în terminal."
        if _code.get("error"):
            msg = f"❌ Eroare: {_code['error']}"
        self.wfile.write(f"<html><body style='font-family:sans-serif;font-size:20px'>{msg}</body></html>".encode())

    def log_message(self, *a):
        pass


def main():
    print("=== Obținere YT_REFRESH_TOKEN (o singură dată) ===\n")
    client_id = input("Client ID (Desktop app): ").strip()
    client_secret = input("Client Secret: ").strip()
    if not client_id or not client_secret:
        sys.exit("Client ID/Secret lipsă.")

    auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": REDIRECT,
        "response_type": "code",
        "scope": SCOPE,
        "access_type": "offline",
        "prompt": "consent",
    })

    httpd = socketserver.TCPServer(("", PORT), Handler)
    t = threading.Thread(target=httpd.handle_request)  # un singur request
    t.start()

    print("\nSe deschide browserul pentru autorizare...")
    print("Dacă nu se deschide, copiază manual acest link:\n")
    print(auth_url, "\n")
    webbrowser.open(auth_url)
    t.join(timeout=300)
    httpd.server_close()

    if _code.get("error"):
        sys.exit(f"Autorizare eșuată: {_code['error']}")
    code = _code.get("code")
    if not code:
        sys.exit("Nu am primit codul de autorizare (timeout 5 min).")

    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT,
    }, timeout=60)
    if not r.ok:
        sys.exit(f"Schimb token eșuat: {r.text}")
    refresh = r.json().get("refresh_token")
    if not refresh:
        sys.exit("Nu a venit refresh_token. Reîncearcă (revocă accesul în myaccount.google.com "
                 "→ Security → Third-party access, apoi rulează din nou cu prompt=consent).")

    print("\n" + "=" * 60)
    print("GATA! Pune aceste 3 secrete în GitHub (Settings → Secrets → Actions):\n")
    print(f"  YT_CLIENT_ID      = {client_id}")
    print(f"  YT_CLIENT_SECRET  = {client_secret}")
    print(f"  YT_REFRESH_TOKEN  = {refresh}")
    print("=" * 60)


if __name__ == "__main__":
    main()
