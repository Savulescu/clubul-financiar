"""Sursă unică pentru navbar + footer pre-randate static (evită drift cu site.js).
Capturat din DOM-ul generat de site.js. site.js hidratează dacă markup-ul există deja."""
import os
_d = os.path.dirname(os.path.abspath(__file__))
NAV_HTML = open(os.path.join(_d, "_shell_nav.html"), encoding="utf-8").read().strip()
FOOTER_HTML = open(os.path.join(_d, "_shell_foot.html"), encoding="utf-8").read().strip()
