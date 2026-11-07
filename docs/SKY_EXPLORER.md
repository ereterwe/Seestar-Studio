# Sky Explorer (Phase 2)

Lokale Suche in OpenNGC (NGC/IC mit Ergänzungskatalog, 110 Messier-Zuordnungen,
109 Caldwell-Zuordnungen). Doppelte/nicht existente Einträge bleiben in der
Gesamtsuche erkennbar; Sammlungen zeigen die verwendbaren Einträge. M102 wird
als historisch umstrittener Kandidat NGC 5866 geführt. Unbekannte Werte bleiben
leer. Beschreibungen entstehen aus Typ/Sternbild, fotografische Hinweise sind
explizite Größenheuristiken und keine Vorhersage der Bildqualität.

## Datenherkunft und Lizenzen
OpenNGC: https://github.com/mattiaverga/OpenNGC, unveränderter Snapshot
`be3cd6c5498806a2fbb2f7e0452ef802dbb02be0`, abgerufen am 6. November 2026.
CC BY-SA 4.0, Mattia Verga und Mitwirkende. Original-README, Autoren, Feldführer,
Lizenztext, genaue URLs und SHA256 in `seestar_studio/catalog_data/`.
Der Katalog bleibt ein getrennt lizenziertes Datenwerk; seine Quellen und
Attribution werden mitgeliefert. Abgeleitete Daten unter derselben Datenlizenz.
M102-Unklarheit: https://heasarc.gsfc.nasa.gov/W3Browse/all/messier.html und
https://messier.lamost.org/seds/seds.org/messier/en/m/m102d.html.

## Astronomie
Astropy 8.0.2 / ERFA, ICRS-Katalogkoordinaten, topozentrische AltAz-Transformation.
Mond mit eingebauter Ephemeride; IERS-Netzdownloads ausdrücklich deaktiviert.
Standort ausschließlich nach ausdrücklicher Eingabe/Bestätigung; lokal in den
persönlichen Einstellungen, nicht im Release. Löschen im Sky Explorer möglich.
IANA-Zeitzone und UTC-Rechnung berücksichtigen Sommerzeit. Nacht = lokaler
Mittag bis nächster lokaler Mittag, also bei Zeitumstellung 23/25 Stunden.
Raster 5 Minuten; geometrischer Horizont ohne Refraktion/Geländemodell.
Horizontdurchgänge linear interpoliert; höchster Stand aus dem Raster.
Beobachtungsfenster konservativ aus vollständigen Rasterintervallen bei
Zielhöhe ≥30° und Sonne ≤−18°. Polartag/zirkumpolare Ziele werden berücksichtigt.
Veraltete/außerhalb des Gültigkeitsbereichs liegende Zeitdaten werden angezeigt.
Grundlagen: https://docs.astropy.org/en/stable/coordinates/solarsystem.html,
https://docs.astropy.org/en/stable/utils/iers.html.

## Bildfelder
Nominale optische Profile, unabhängig von Drizzle/Bildstreamauflösung.
S50: 1080×1920, 2,9 µm, 250 mm. S50 Pro Hauptkamera: 2160×3840,
2,9 µm, 260 mm. Pro Weitwinkel: 2160×3840, 1,6 µm, 6 mm.
Achsenwinkel = 2 atan(Pixelzahl × Pixelgröße / (2 × Brennweite)).
Schematischer, frei ausgerichteter Größenvergleich; keine behauptete aktuelle
Kameraorientierung. Weitwinkelwerte nominal, ohne Verzeichnungskorrektur.
Quellen: https://helpdesk.zwoastro.com/hc/en-us/articles/48476700259213-Seestar-S30-S50-S50-Pro-S30-Pro-Comparison,
https://us.seestar.com/products/seestar-s50-pro-smart-telescope,
https://www.vixen.co.jp/product/63001_1/ (S50-Pixelgröße).

Auswahl sendet keinen Teleskopbefehl. Beobachten/Planen sind Übergaben an die
nachfolgenden V2-Module; ein echter Steuerbefehl benötigt Control Mode,
explizites Gerät und konkrete Bestätigung.
