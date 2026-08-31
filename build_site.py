# -*- coding: utf-8 -*-
"""Baut die generierten Teile der Website: Ratgeber-Seiten, Ratgeber-Liste auf der
Startseite und sitemap.xml.

Ratgeber-Workflow:
  1. Artikel als Markdown-ähnliche Textdatei in ratgeber/quellen/<slug>.txt
     (Format siehe ratgeber/quellen/BEISPIEL.txt: Kopfzeilen + Absätze).
  2. python build_site.py  ->  ratgeber/<slug>.html aus TEMPLATE + Liste auf
     index.html (zwischen den RATGEBER-Markern) + sitemap.xml.
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
    """Baut ratgeber/<slug>.html; liefert [(pfad, titel, beschreibung), ...]."""
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
        seiten.append((f"ratgeber/{q.stem}.html", meta["titel"], meta["beschreibung"]))
        print("gebaut:", ziel.name)
    return seiten

def index_liste(seiten):
    """Schreibt die Ratgeber-Liste zwischen die Marker in index.html."""
    idx = HIER / "index.html"
    inhalt = idx.read_text(encoding="utf-8")
    items = "\n".join(
        f'      <li><a href="{pfad}"><b>{html.escape(titel)}</b>'
        f"<span>{html.escape(beschr)}</span></a></li>"
        for pfad, titel, beschr in seiten)
    neu, n = re.subn(
        r"(<!--RATGEBER:START-->).*?(<!--RATGEBER:END-->)",
        lambda m: f"{m.group(1)}\n{items}\n      {m.group(2)}",
        inhalt, flags=re.S)
    assert n == 1, "RATGEBER-Marker nicht (eindeutig) in index.html gefunden"
    idx.write_text(neu, encoding="utf-8")
    print(f"index.html: {len(seiten)} Ratgeber-Einträge")

def sitemap(seiten):
    heute = datetime.date.today().isoformat()
    urls = ["", "impressum.html", "datenschutz.html"] + [s[0] for s in seiten]
    eintraege = "\n".join(
        f"  <url><loc>{BASE}/{u}</loc><lastmod>{heute}</lastmod></url>" for u in urls)
    (HIER / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{eintraege}\n</urlset>\n", encoding="utf-8")
    print(f"sitemap.xml: {len(urls)} URLs")

if __name__ == "__main__":
    QUELLEN.mkdir(parents=True, exist_ok=True)
    seiten = artikel_bauen()
    index_liste(seiten)
    sitemap(seiten)
