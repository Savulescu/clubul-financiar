#!/usr/bin/env python3
"""Preview local pentru docs/ care se comportă ca GitHub Pages:
- /educatie → educatie.html (URL-uri fără extensie, cum sunt toate linkurile interne)
- /dir → /dir/index.html ; 404 → docs/404.html (ca pe live)
Usage: python3 _preview.py [port]   (default 8765)
"""
import os, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765

class Pages(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=DOCS, **kw)

    def send_head(self):
        path = self.path.split("?", 1)[0].split("#", 1)[0]
        fs = self.translate_path(path)
        if not os.path.exists(fs):
            if os.path.exists(fs + ".html"):
                self.path = path + ".html" + (("?" + self.path.split("?", 1)[1]) if "?" in self.path else "")
            elif os.path.exists(os.path.join(DOCS, "404.html")):
                self.path = "/404.html"
        return super().send_head()

    def log_message(self, fmt, *args):
        pass  # liniște — erorile de TLS/https ale browserului umpleau logul

if __name__ == "__main__":
    print(f"Preview pe http://localhost:{PORT} (docs/, extensionless ca GitHub Pages)")
    ThreadingHTTPServer(("", PORT), Pages).serve_forever()
