# Private GitHub-Übertragung — 7. November 2026

Der Benutzer hat nach Abschluss von 2.3.0b2 ausdrücklich die Übertragung nach
GitHub beauftragt. Ziel: https://github.com/ereterwe/Seestar-Studio.
Die private Sichtbarkeit und Schreibberechtigung wurden vorab über die
GitHub-API bestätigt. Das Remote enthielt vor dieser Übertragung keine Git-Refs.

## Umfang

- Aktueller Quellcode, Tests, Buildskripte, Katalogdaten mit Herkunftsnachweisen,
  Lizenztexte und Projektdokumentation auf `main`.
- Die geprüften 2.3.0b2-Pakete als **Release-Entwurf**: portable Windows-Version
  einschließlich EXE und Laufzeitdateien, Installer, App-Quellpaket,
  Upstream-Quellarchive und SHA256-Prüfsummen.
- Keine alte Versionssammlung, virtuelle Umgebung, lokalen Sicherungen,
  persönlichen Bilder/Standorte, Session-Datenbanken oder Rohdiagnosen.
- Keine Schlüssel, PEM-/APK-/XAPK-Dateien oder Zugangsdaten. Authentifizierung
  verbleibt ausschließlich auf dem jeweiligen Benutzer-PC.

Die Pakete bleiben byteidentisch mit dem geprüften Build. Seit dessen Erstellung
wurden für GitHub nur Ausschlussregeln, diese Übertragungsdokumentation und die
Git-Statusbeschreibung des lokalen Prüfwerkzeugs ergänzt. Der Anwendungscode
bleibt identisch; sein Quellhash lässt sich mit `build-info.json` im Paket
vergleichen. Das beigefügte App-Quellpaket enthält die Dokumentation zum
Buildzeitpunkt, das Git-Repository zusätzlich den späteren Übertragungsauftrag.

## Freigabegrenzen

Diese Freigabe betrifft das vorhandene **private** Repository und einen
Release-Entwurf. Sie ändert weder die Sichtbarkeit noch die dokumentierten
Abnahmegrenzen. Vollständige automatische Aufnahme unter Sternenhimmel,
externe Windows-Abnahmen und offene Lizenz-/native Quellenfragen bleiben offen.
Keine öffentliche Veröffentlichung, keine automatische Verteilung und keine
neue Funktionsentwicklung. Der Feature Freeze gilt weiter.
