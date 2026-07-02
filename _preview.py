#!/usr/bin/env python3
"""Preview local pentru docs/ care se comportă ca GitHub Pages:
- /educatie → educatie.html (URL-uri fără extensie, cum sunt toate linkurile interne)
- /dir → /dir/index.html ; 404 → docs/404.html (ca pe live)
- scoate `upgrade-insecure-requests` din CSP la servire: pe live site-ul e pe HTTPS,
  dar local Safari upgradează asset-urile la https:// contra unui server http →
  pagină fără CSS/JS („pare stricat"). Fișierele din repo NU sunt modificate.
Usage: python3 _preview.py [port]   (default 8765)
"""
import os, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765

class Pages(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DOCS, **kw)

    def resolve(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        fs = self.translate_path(path)
        if os.path.isdir(fs):
            fs = os.path.join(fs, "index.html")
        if not os.path.exists(fs):
            if os.path.exists(fs + ".html"):
                return fs + ".html", 200
            return os.path.join(DOCS, "404.html"), 404
        return fs, 200

    def do_GET(self):
        fs, code = self.resolve()
        if fs.endswith(".html") and os.path.exists(fs):
            with open(fs, "rb") as fh:
                body = fh.read()
            body = body.replace(b"; upgrade-insecure-requests", b"")
            body = body.replace(b"upgrade-insecure-requests", b"")
            self.send_response(code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()

    def log_message(self, fmt, *args):
        pass  # liniște — tentativele https ale browserului umpleau logul

if __name__ == "__main__":
    print(f"Preview pe http://localhost:{PORT} (docs/, ca GitHub Pages, CSP fără upgrade)")
    ThreadingHTTPServer(("", PORT), Pages).serve_forever()
