# Version 2 — Abschlussprüfung des lokalen Entwicklungsbuilds

Stand 6. November 2026, Version 2.0.0.dev2. Kein öffentlicher Release.

## Automatisiert / simuliert
61 pytest-Tests bestanden (Prozesscode 0). Vorhandene Viewer-Regressionen plus
Dateien/Resume/Fehler, Katalog/Aliase, Offline-Astronomie/DST/Polartag,
Steuerungsbestätigungen/Identität/Antwortverlust/Freigabewiderruf,
Planfenster/Konflikte/Persistenz und Historie/Ausfälle/Neustarts/Zählerwechsel.
Zwölf Stunden virtuelle Messwerte prüfen die begrenzte, lückentreue Darstellung;
keine Behauptung einer zwölfstündigen echten Laufzeit.

Native UI-Prüfung bei 1920×1080: Live Viewer unverändert, Sky Explorer,
gesperrter Control Mode, Planner mit zwei simulierten Geräten, Sessionvergleich
mit zwei künstlichen Messreihen. Standort dieser Prüfungen synthetisch,
nicht als persönlicher Beobachtungsort gespeichert.

## Windows-EXE
PyInstaller-Ordnerbuild gestartet, alle sechs Tabs vorhanden, lokaler Katalog
14.034 Einträge, Nachtberechnung erfolgreich, Control Mode false, Geräte leer
(beide ausgeschaltet), sauberer Shutdown aller Worker, Exitcode 0.
Nachweis `reports/v2-final-exe.json`, zugehörige native Screenshots.
Build `release/SeestarStudio-2.0.0.dev2-win64.zip`; nicht separat nur die EXE kopieren.

Lokaler Artefaktcheck: ZIP-CRC, Quellen/Katalog/Lizenzdateien vorhanden,
keine Authentifizierungs-PEMs/APKs, privaten Datenbanken, Logs oder Aufnahmen
in den geprüften Archiven. certifi enthält legitime öffentliche CA-Zertifikate.
Das ist keine abschließende Sicherheits-/Rechtsprüfung oder Git-Historienprüfung
(Projekt besitzt derzeit kein Git-Repository).

## Reale Tests und Grenzen
Viewer und File Manager bereits früher an S50/S50 Pro lesend geprüft:
`TEST_REPORT.md`, `PHASE1_TEST_REPORT.md`. Früher Sky-Probe-Lauf mit beiden
realen Bildstreams; dessen Ziel-/Stage-Berichtsfelder waren falsch benannt
und enthalten null, daher daraus keine Statusbehauptung ableiten.

Anschließend Benutzerhinweis: beide Geräte ausgeschaltet. Danach ausschließlich
Offline-/Mocktests. Keine echten Bewegungs-/Aufnahme-/Filterbefehle gesendet.
Echte Control-Mode-Tests, große Massendownloads, längerer Gesamtbetrieb,
Stromausfall, DHCP-Wechsel mit Hardware, Fremd-PC ohne Python und externer
S50-Nutzer bleiben offen. Keine S30-/S30-Pro-Hardware vorhanden.
