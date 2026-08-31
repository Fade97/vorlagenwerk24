# VorlagenWerk24 — Website

Statischer OnePager + Ratgeber-Gerüst. Live auf GitHub Pages, später Umzug auf eigene Domain.

## Struktur
- `index.html` / `styles.css` — OnePager (Markenfarben aus dem Listing-Design)
- `impressum.html`, `datenschutz.html` — Pflichtseiten (noindex)
- `ratgeber/` — SEO-Ratgeber je Nische: Quelle als `.txt` in `ratgeber/quellen/`,
  dann `python build_site.py` → HTML + sitemap.xml (Format: `quellen/BEISPIEL.txt`)
- `site_config.json` — `base_url` (bei Domain-Umzug ändern + CNAME-Datei anlegen)

## Deploy
Push auf `main` → GitHub Pages liefert automatisch aus (Branch main, Root).

## Offene Schritte nach Deploy
1. Pinterest-Claim: pinterest.com → Einstellungen → Beanspruchte Konten → Website →
   HTML-Tag kopieren und in `index.html` in den `<head>` einfügen, pushen, bestätigen.
2. Bei eigener Domain: base_url in site_config.json + canonical in index.html ändern,
   `CNAME`-Datei mit der Domain anlegen, DNS auf GitHub Pages zeigen.
