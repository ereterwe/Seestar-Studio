# Telescope Desk 2.3.0b3 — GitHub draft beta update

11 November 2026: replace the obsolete b2 GitHub release draft with the current
Telescope Desk beta and update the English README/repository description.
The user authorized the source update and release replacement. Preserve source
history and local historical artifacts. Keep binary release visibility as draft
while native corresponding-source and legal review gates remain unresolved.

Includes the additional Pillow Tk/CMS/WebP exclusions, source-family mapping of
124 native files, 105 hash-checked source archives and corrected third-party
notices. 174 automated tests passed in the completed Pillow review. No new
hardware-test claim. See docs/releases/TELESCOPE_DESK_2.3.0b3.md.

## Earlier local refactor record

Product/package/EXE renamed; legacy profiles reused without copying keys.
Unused Qt Multimedia Widgets and Pillow AVIF excluded. FFmpeg retained unchanged.
172 tests passed; see the minimization report for final build and installer results.
No new public release or version increment. Below are unchanged historical records.

# 2.3.0b3 — lokale Compliance-Korrektur

8. November 2026: Der Projektverantwortliche hat klargestellt, dass b3 neu lokal
zu erstellen und der Quellcode auf GitHub zu aktualisieren ist. Kein b3-Link wird
benötigt. B2 bleibt als Vergleichsbasis unverändert. Keine neuen Funktionen.

Korrekturen: Colorama-Quellen/Lizenz, kollisionsfreie Vendor-Notices, neun unbenutzte
Qt-Dateien ausgeschlossen, öffentliche Projektangaben berichtigt, vollständiger
PASS/OPEN/BLOCKER-Prüfer und dokumentierte native/rechtliche Quellenlücken.
166 automatisierte Tests bestanden; b3-Build und Prüfstatus siehe
[Compliance-Bericht](docs/RELEASE_COMPLIANCE_REPORT_2.3.0b3.md).
Native Quellen-/Buildnachweise und Rechtsfragen sind keine geschlossenen Punkte.
Neue öffentliche Binär-Releases sind nicht durch den Quellcode-Push freigegeben.

# 2.3.0b2 — 2026-11-07

Separat freigegebene UX-Verbesserungen und anschließender Steuerungs-Bugfix:

- Offline-Tag-Nacht-Verlauf im Observation Planner auf Basis der bestätigten
  Position, Astropy-Sonnenhöhe und absoluter Zeitachse. Standardmäßig aktiv,
  lokal abschaltbar; Sonnenauf-/untergang und astronomische Nacht markiert.
  Polarfälle, fehlender Standort, mehrtägige Pläne und DST berücksichtigt.
- Windows-Standorteinstellungen bei verweigertem/deaktiviertem Zugriff direkt
  über Benutzeraktion öffnen. Getrennte Fehlerursachen, manuelle Alternative,
  keine Berechtigungsänderung oder automatische erneute Standortabfrage.
- Vollständige bestätigte Beobachtungssequenz neben mechanischem Nur GoTo;
  ereignisbasierte Zustände, gezielte Fehlerabbrüche und erneutes Statuslesen.
  Preview-/Stack-Freigaben und klare DE/EN-Sperrgründe korrigiert.
  S50/S50 Pro indoor geprüft; astronomischer Gesamterfolg weiterhin offen.
  Details: docs/CONTROL_B2_REPORT.md.
- Keine neuen Abhängigkeiten. Bestehendes Icon, Credits und Lizenztexte erhalten.
- Neue astronomische Referenz-, Render-, Worker- und Standortfehlertests.
  Test- und Buildnachweise: docs/B2_TEST_REPORT.md.
- Keine Veröffentlichung; bestehende Freigabeblocker bleiben bestehen.
  Nach Abschluss dieses Auftrags erneut Feature Freeze.

# 2.3.0b1 — Beta-Vorbereitung, 2026-11-07

- Optionale Windows-/Seestar-Standortvorschläge, Genauigkeit und Bestätigung;
  keine ungefragten Positionsabfragen und keine automatische Speicherung.
- Originales App-Icon als SVG/PNG/ICO, durchgängige Windows-Integration.
- Scrollbarer Über-Dialog mit Credits, echten Versionen und lokalen Lizenzen.
- Zentrale Versionsmetadaten, native PE-Version, technische Quellen-/Lizenzmanifeste.
- Bereinigte Diagnosekategorien, Sicherheitsprüfung, externe Beta-Testanleitung.
- Weitergabe bleibt wegen dokumentierter Lizenz-/Quellenfragen und fehlender
  manueller Freigabe gesperrt. Feature Freeze nach Abschluss dieser Vorbereitung.

# 2.2.0.dev1 — 2026-11-06

- Unabhängiger Live Stack/Live View pro Gerät; Qt/FFmpeg-Video mit Kamera-SDP-
  Prüfung, FPS, Reconnect, begrenztem Puffer und sauberem Decoderende.
- Grafischer Mehrgeräte-Planer mit Drag/Resize, fünf Minuten Raster,
  zuverlässigen Slots und Wechselzeiten, Konflikten, lokalen Planbibliotheken,
  V2.1-Migration und bestätigter Optimierungsvorschau.
- Windows-Zeitzone, UTC-Persistenz und eindeutige Sommer-/Winterzeitbehandlung.
- Deutsch/English/Windows-Automatik mit zentralen Ressourcen und Live-Umschaltung.
- Versionsgetrennte Windows-Builds schützen eine laufende ältere Anwendung.
- 87 automatisierte Tests; reale parallele Stack-/Telemetrieprüfung erfolgreich.
  RTSP während der Aufnahmen nicht verfügbar; echte Videoabnahme bleibt offen.
- Qt-Multimedia-/FFmpeg-Lizenzhinweise ergänzt; keine Veröffentlichungsfreigabe.

# Changelog

## 2.1.0.dev1 — 6. November 2026, lokaler Entwicklungsbuild

- Nativer Einrichtungsassistent, vorhandene Authentifizierung bleibt unverändert.
- Explizite lokale PEM-/APK-/XAPK-Imports über SeestarPy; geschützte Windows-DACL,
  separater lesender Verbindungstest, Bereinigung nicht aktivierter Importe.
- Lokaler Diagnoseexport ohne Gerätekennungen, IPs, Standorte, Ziele oder Schlüssel.
- Installer für das Benutzerprofil, optionales Desktop-Icon, keine Administratorrechte.
- Einzelinstanzschutz und geordneter GUI-/Worker-Abbau.
- Externe S50-/Fremd-PC-Tests und öffentliche Freigabe weiterhin ausstehend.

## 2.0.0.dev2 — 6. November 2026, lokaler Entwicklungsbuild

- Sky Explorer mit lokalem OpenNGC, Messier/Caldwell/NGC/IC, Alias-Suche,
  Offline-Astronomie, ausdrücklich bestätigtem Standort und Bildfeldvergleich.
- Optionaler Control Mode mit gerätebezogener Bestätigung, Identitätsprüfung,
  getrennten Verbindungen und ohne automatisches Wiederholen von Mutationen.
  Ausschließlich simulierte Steuerungstests.
- Lokaler Observation Planner mit JSON-Speicherung, Konflikten, Sichtbarkeit,
  heuristischer Reihenfolge und Mehrgeräte-Timeline; keine Ausführung.
- SQLite-Session-Historie mit Lückenbehandlung und nativen Vergleichskurven.
- Lizenz-/Kompatibilitätsdokumentation und V2.1-/V3-Plan ergänzt.

## 2.0.0.dev1 — 6. November 2026

File Manager: lesende SMB-Listen, rekursive Downloads, Abbruch/Resume,
Größen-/lokale Hashprüfung, Vorschauen und Bandbreitenbegrenzung.

## 0.1.0 — 5. November 2026

Native Mehrgeräte-Liveansicht und Telemetrie, RAW/JPEG, Zoom/Maximieren,
Reconnect, bestehende lokale Authentifizierung, Windows-Ordnerbuild.

Beta-Abschluss 7. November 2026: 95 Tests; portable/ installierte EXE und
Installer-Lebenszyklus geprüft. Lokale Pakete gesichert, Feature Freeze.
Freigabeblocker und Testgrenzen: BETA_RELEASE_CHECKLIST.md. Keine Weitergabe.
