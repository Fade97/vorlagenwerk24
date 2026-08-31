# -*- coding: utf-8 -*-
"""Baut die generierten Teile der Website: sitemap.xml und Ratgeber-Seiten.

Ratgeber-Workflow (vorbereitet für die Nischen-Ratgeber):
  1. Artikel als Markdown-ähnliche Textdatei in ratgeber/quellen/<slug>.txt
     (Format siehe ratgeber/quellen/BEISPIEL.txt: Kopfzeilen + Absätze).
  2. python build_site.py  ->  ratgeber/<slug>.html aus TEMPLATE + sitemap.xml.
  3. Committen und pushen — GitHub Pages liefert automatisch aus.

Bewusst ohne Jekyll/Framework: eine Python-Datei, volle Kontrolle, kein Build-Stack.
"""
import datetime
import html
import json
import pathlib
import re

HIER = pathlib.Path(__file__).parent
CFG = json.loads((HIER / "site_config.json").read_text(encoding="utf-8"))
BASE = CFG["base_url"].rstrip("/")
TEMPLATE = (HIER / "ratgeber" / "TEMPLATE.html").read_text(encoding="utf-8")
QUELLEN = HIER / "ratgeber" / "quellen"

def artikel_bauen():
    seiten = []
    for q in sorted(QUELLEN.glob("*.txt")):
        if q.stem.startswith("BEISPIEL"):
            continue
        kopf, _, body = q.read_text(encoding="utf-8").partition("\n\n")
        meta = dict(z.split(":", 1) for z in kopf.strip().splitlines())
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        absaetze = []
        for block in body.strip().split("\n\n"):
            if block.startswith("## "):
                absaetze.append(f"<h2>{html.escape(block[3:])}</h2>")
            elif block.startswith("- "):
                li = "".join(f"<li>{html.escape(z[2:])}</li>" for z in block.splitlines())
                absaetze.append(f"<ul>{li}</ul>")
            elif block.startswith("CTA:"):
                text, _, url = block[4:].strip().rpartition(" ")
                absaetze.append(f'<div class="cta">{html.escape(text)} <a href="{html.escape(url)}">Zur Vorlage →</a></div>')
            else:
                absaetze.append(f"<p>{html.escape(block)}</p>")
        seite = TEMPLATE
        for k, v in (("{{TITEL}}", meta["titel"]), ("{{BESCHREIBUNG}}", meta["beschreibung"]),
                     ("{{SLUG}}", q.stem), ("{{STAND}}", meta.get("stand", "")),
                     ("{{BASE}}", BASE), ("{{INHALT}}", "\n".join(absaetze))):
            seite = seite.replace(k, v if k == "{{INHALT}}" else html.escape(v) if k in ("{{TITEL}}", "{{BESCHREIBUNG}}") else v)
        ziel = HIER / "ratgeber" / f"{q.stem}.html"
        ziel.write_text(seite, encoding="utf-8")
        seiten.append(f"ratgeber/{q.stem}.html")
        print("gebaut:", ziel.name)
    return seiten

def sitemap(seiten):
    heute = datetime.date.today().isoformat()
    urls = ["", "impressum.html", "datenschutz.html"] + seiten
    eintraege = "\n".join(
        f"  <url><loc>{BASE}/{u}</loc><lastmod>{heute}</lastmod></url>" for u in urls)
    (HIER / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{eintraege}\n</urlset>\n", encoding="utf-8")
    print(f"sitemap.xml: {len(urls)} URLs")

if __name__ == "__main__":
    QUELLEN.mkdir(parents=True, exist_ok=True)
    sitemap(artikel_bauen())
