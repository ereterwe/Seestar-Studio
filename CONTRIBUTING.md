> Current Telescope Desk working documentation. Earlier release facts are preserved unchanged in [the Seestar Studio archive](docs/history/seestar-studio-b3/CONTRIBUTING.md). New build status: [minimization report](docs/compliance/MINIMIZATION_REPORT.md).

# Entwicklungsregeln

Projekt noch nicht öffentlich freigegeben. Änderungen lokal prüfen und in
PROGRESS.md/NEXT_STEPS.md dokumentieren. Python 3.12, vorhandene Versionen aus
requirements-lock.txt, Tests mit `python -m pytest -q`.

- Viewer-Allowlist erhalten; Steuerung über getrennten, ausdrücklich
  freigeschalteten Adapter. Keine realen Steuerungstests ohne Benutzerfreigabe.
- Keine festen IPs, Benutzerpfade, Seriennummern oder Modell-Sonderfälle im Kern.
- Keine erfundenen Fähigkeiten/Messwerte; fehlende Daten als unbekannt anzeigen.
- Netzwerk, Downloads, Berechnungen und Datenbankzugriffe außerhalb des GUI-Threads.
- Geheimnisse, Standorte, APK/XAPK, Aufnahmen, DBs und Logs aus Quellen/Builds halten.
- Hardwaretests, simulierte Tests und theoretische Kompatibilität unterscheiden.
- Lizenz/Urheber/Quellen für neue Abhängigkeiten und Daten dokumentieren.

Beiträge zum Programm müssen mit GPL-3.0-only vereinbar sein. Katalogdaten
unterliegen ihrer eigenen CC-BY-SA-4.0-Lizenz. Rechtsfragen vor Veröffentlichung
prüfen, nichts eigenmächtig hochladen oder weitergeben.

## Beta Feature Freeze

Nach Abschluss der Final Beta Preparation endet die eigenständige Featureentwicklung.
Auch kleine Zusatzfunktionen, automatische Feedbackauswertung und Planung sind
nicht freigegeben. Mark sammelt und priorisiert Testerfeedback persönlich.
Änderungen, einschließlich Fehler-/Sicherheits-/Dokumentationskorrekturen, nur
auf neuen ausdrücklichen Auftrag. Kein Push/Release/Sichtbarkeitswechsel ohne Freigabe.
