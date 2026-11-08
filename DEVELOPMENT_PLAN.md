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

## Historischer Entwicklungsstand bis 7. November 2026

> GitHub-Auftrag vom 7. November 2026: Die Übertragung des aktuellen Standes
> in das bestehende private Repository ist ausdrücklich freigegeben. Details
> und Grenzen: [GITHUB_DELIVERY.md](docs/GITHUB_DELIVERY.md). Frühere Aussagen
> „kein Git/kein Upload freigegeben“ beschreiben den Stand vor diesem Auftrag.

# 2.3.0b2 — abgeschlossen, Feature Freeze

7. November 2026: GoTo-/Autofokus-/Stacking-Korrektur sowie beide vorherigen
UX-Verbesserungen abgeschlossen. **154 Tests bestanden**. Echte Indoor-Tests
am S50 und S50 Pro; beide nach den eigenen Versuchen wieder geparkt.
Vollständige automatische Aufnahme unter Sternenhimmel bleibt ausdrücklich offen.

Windows-EXE, portable ZIP, Installer und App-Quellpaket neu erstellt. Portable
und installierte EXE sauber gestartet/beendet (Exit 0, READ ONLY). Finale
EXE-Läufe erkannten einen geparkten S50 Pro; S50 wurde dabei nicht erneut erkannt.
Installation/Reinstallation: 1.423 Dateien geprüft, keine Abweichung.
Deinstallation: Programm/Verknüpfungen/Registrierung entfernt, Benutzerprofil
unverändert. Prüfberichte: docs/B2_TEST_REPORT.md und docs/CONTROL_B2_REPORT.md.

Quellhash/ZIP/Icon-/Sicherheitsprüfung bestanden; 39 Upstream-Archive vorhanden.
Pakete/Abschlussberichte werden unter backups/beta-2.3.0b2 mit SHA256 gesichert.
Kein lokales Git, kein Upload. Die früheren b1-/b2-Ausgangspakete bleiben erhalten.
Keine Freigabe zur Weitergabe: Lizenz-/native Quellenfragen und externe Abnahmen
stehen weiter in BETA_RELEASE_CHECKLIST.md. Keine nächste autonome Featurephase.

## Vorheriger Verlauf (historisch)

# 2.3.0b2 — ausdrücklich beauftragtes Update, in Arbeit

Nur Tag-Nacht-Hintergrund und Windows-Standorteinstellungen. b1-Sicherung mit
23 Dateien erneut per SHA256 geprüft; kein lokales Git. Ausgangsregression:
95 Tests bestanden. Astropy wiederverwendet, keine neue Abhängigkeit.
Implementierung und erste Regression (119 Tests) erfolgreich; zusätzliche
Fehlerzweige werden geprüft. Abschließender Build/Installer/QA noch offen.
Keine realen Standortabfragen, Steueraktionen oder Veröffentlichung.
Nach Abschluss erneut Feature Freeze; der folgende b1-Verlauf ist historisch.

# Final Beta Preparation — abgeschlossen am 7. November 2026

Version 2.3.0b1 lokal gebaut und gesichert; Feature Freeze gilt. Standort,
Original-Icon, Über-Dialog, technische Lizenzprüfung, Paketierung und lokale
Regression abgeschlossen. 95 Tests, EXE und Installer erfolgreich geprüft.
Keine Weitergabe freigegeben: BETA_RELEASE_CHECKLIST.md nennt alle Blocker;
docs/BETA_TEST_REPORT.md trennt Simulation, Hardwarebelege und offene Abnahmen.
Sicherung: backups/beta-2.3.0b1. Keine nächste autonome Featurephase.
Neue Funktionen/Korrekturen/Feedbackbearbeitung nur nach ausdrücklichem Auftrag.

## Historischer Plan (keine automatische Fortsetzung)

# Seestar Studio — Entwicklungsplan V2 bis V2.2

Stand: 6. November 2026. Bestehende Anwendung modular erweitern; keine zweite App.
Priorität und Reihenfolge sind verbindlich. Eine Phase beginnt erst nach dem
Funktions-/Regressionsabschluss ihrer Vorgängerphase.

## Ausgangssicherung
- [x] Git-Status geprüft: kein Git-Repository; lokale Sicherung unter `backups/`.
- [x] Aktuelle Quellen und getesteter 0.1.0-Windows-Build mit SHA256 gesichert.
- [x] Bestehende Regressionstests: 16 bestanden.

## Phase 1 — File Manager (höchste Priorität)
- [x] Read-only SMB-Adapter auf Basis der lokal geprüften SeestarPy-Anbindung.
- [x] Automatische Geräteanbindung, Verzeichnisbaum und Dateiliste mit Typ,
  exakter Größe und Zeit; Zielgruppierung, Mehrfachauswahl.
- [x] Einzel-/Verzeichnis-/Sessiondownloads, Fortschritt/Tempo/Restgröße,
  Abbrechen, erneutes Starten und Offset-Wiederaufnahme.
- [x] Größen-/Metadatenprüfung, lokale SHA256-Nachweise und Duplikaterkennung.
- [x] Sichere Windows-Pfade, keine Überschreibungen, keine Remote-Mutationen.
- [x] Kleine JPEG/PNG-Vorschauen, lokaler Cache; FITS nur lokal, falls sinnvoll.
- [x] Globale Downloadparallelität 1, konfigurierbare Bandbreite.
- [x] Fehler-/Resume-/Traversaltests; echte lesende Prüfung beider Geräte;
  Livebildregression, Dokumentation und reproduzierbarer EXE-Build.

## Phase 2 — Sky Explorer
**Abgeschlossen:** 39 Tests, native UI, Offline-Astronomie im Windows-Build,
Quellen/Lizenzen und gesicherter Build unter `backups/phase2`.
Abhängigkeit: Phase 1 fertig. Lokaler, lizenzierter Messier-/Caldwell-/NGC-/IC-
Katalog mit Alias-Suche, Typ, Koordinaten, Größe, Helligkeit, Sternbild,
Beschreibung und fotografischer Eignung. Explizite Standortkonfiguration,
korrekte Zeitzonen, Höhe/Azimut, Auf-/Untergang/Transit, Nachtverlauf,
Mondabstand/Dämmerung/Beobachtungsfenster. Geprüfte Kamera-FOVs, Zielauswahl mit
explizitem Teleskop und Bestätigung, keine Aktion allein durch Objektauswahl.
Abnahme: Katalog-/Astronomietests, GUI, Livebildregression, Build, Quellen/Lizenzen.

## Phase 3 — Optionaler Control Mode
**Implementiert, simuliert getestet:** 48 Tests insgesamt. Echte Steuerungstests
ausdrücklich ausstehend. API-Audit: `docs/CONTROL_API_AUDIT.md`.
Abhängigkeit: Phase 2. SeestarPy-API-Audit je Aktion. READ ONLY bleibt Standard.
GoTo, Tracking, Aufnahme/Stacking, Belichtung/Gain/Filter, Autofokus und Parken
nur soweit sicher unterstützt. Konkrete Bestätigung für Unterbrechungen und
persistent wirkende Änderungen. Keine Firmwareupdates. Tests ausschließlich
Mocks; reale Bewegungs-/Aufnahmebefehle erfordern zusätzliche Benutzerfreigabe.
Abnahme: unabhängige Zieladressierung, Sicherheits-/Fehlertests, GUI, Regression.

## Phase 4 — Observation Planner
**Abgeschlossen:** 52 Tests, native Mehrgeräte-Timeline und lokale Validierung.
Abhängigkeit: Phase 3. Lokale Listen je Gerät, Speichern/Laden, Fensterprüfung,
Reihenfolgeoptimierung, Zeitkonflikte und vergleichbare Timelines. Keine
automatische Hardwareausführung. Abnahme: Planung/Validierung/Zeitzonentests,
GUI und Livebildregression.

## Phase 5 — Session-Analyse
**Implementiert, simuliert getestet:** SQLite-Historie und native Vergleichskurven,
Ausfälle/Resets/Neustarts, zwölf Stunden virtuelle Daten, begrenzte Plotgröße.
Finaler V2-Build/Offline-Startprüfung erfolgreich (Exitcode 0), 61 Tests bestanden;
reale Langzeittests und Steuerungstests offen.
Abhängigkeit: Phase 4. SQLite-Historie je Gerät/Session, beobachtete Zeiten,
Framezähler, Integration mit transparenter Herkunft/Unsicherheit, Drops,
Temperatur/Akku/Verbindungsunterbrechungen. Kurven und Sessionvergleiche;
historische und aktuelle Daten klar getrennt. Abnahme: Persistenz-/Lückentests,
Regression, GUI, Build und Dokumentation.

## Optionale Erweiterungen nach Phase 5
RGB-Histogramm, nichtdestruktive Anzeigeparameter, begrenzte lokale
Stack-Snapshots und lokale Benachrichtigungen nach Nutzenprüfung.

## Durchgehende Bedingungen
GUI blockiert nie durch Netzwerk/Dateiübertragungen; keine Schlüsselkopien oder
RPC-Geheimnisse in Logs. Keine realen Steueraktionen ohne neue Freigabe.
Simulierte Tests und echte Hardwaretests separat ausweisen. Fortschritt und
Fortsetzungsanweisung nach jeder Phase aktualisieren; funktionierenden Build
behalten. Keine automatischen Umgehungen von Sitzungs-/Nutzungslimits.

## Ergänzender Masterauftrag (6. November 2026)
Version 2 bleibt vorrangig. Schon jetzt: keine Modell-/IP-/Seriennummern-
Sonderfälle im Kern; Fähigkeiten als verfügbar/unbekannt behandeln, variable
Bildformate/-größen, getrennte Sitzungen. Ausschließlich lokale Nutzung ohne
Konten, Cloud-Login, Uploads oder externe Telemetrie. Lokale Kataloge und
Berechnungen; optionale Onlinefunktionen nur transparent und ausdrücklich.
Standorte sind private Konfiguration und bleiben außerhalb von Quellen/Release.

### Version 2.1 — erst nach Abschluss von Version 2
**Lokal implementiert als 2.1.0.dev1; externe Abnahme bleibt offen.**
71 Tests und native EXE erfolgreich; Setup mit synthetischen Importen,
Installer-Lebenszyklus auf Entwicklungs-PC geprüft. docs/V21_TEST_REPORT.md.
Erster Schritt: lokaler Authentifizierungsassistent; bestehende Konfiguration
unverändert. Ein S50 wieder online, steht drinnen: nur lesende Tests.
- Capability-basierte Erweiterbarkeit; Optimierung für reales S50/S50 Pro.
- Lokaler Setup-Assistent: vorhandene Auth unverändert erkennen; PEM-Import,
  optional rechtlich zu prüfende lokale APK/XAPK-Verarbeitung über SeestarPy;
  Profilablage, sichere Rechte, kein unbestätigtes Überschreiben.
- Portables ZIP auf fremdem PC ohne Python; Ersteinrichtung und Diagnose.
- Installer ohne unnötige Adminrechte, Startmenü/optionale Verknüpfung,
  Upgrade/Deinstallation ohne Verlust persönlicher Daten.
- Externer S50-Test auf anderem Windows-PC mit verständlicher Testanleitung.
  Keine Pflicht zu realen S30-/S30-Pro-Tests.

### Version 3 — Veröffentlichungsvorbereitung nach Version 2.1
Stabilisierung, vollständiges Lizenz-/Quelleninventar, Qt-/LGPL-Prüfung,
rechtliche Prüfung der Extraktion, Secret-/Datenschutzprüfung einschließlich
eventueller Git-Historie, Contributor-/Build-/Installations-/Changelog-Dokumente,
GitHub-Vorbereitung und reproduzierbarer Release-Build.
**Keine Veröffentlichung, Weitergabe oder Uploads ohne ausdrückliche Freigabe.**
Details: `LICENSING.md` und `COMPATIBILITY.md`.

## V2.2 — lokal implementiert, Hardware-Videoabnahme offen
1. Ausgangssicherung backups/v22-start; lokaler Ordner ohne Git-Repository.
2. Unabhängiger RTSP-Live-View, Qt Multimedia, nur verfügbare SDP-Videoquellen,
   keine Gerätemoduswechsel. Bestehender Stack bleibt getrennt.
3. Persistente Slots, Konflikte, Migration V1-Pläne.
4. Grafische Timeline mit Drag/Resize/Zoom und Mehrgeräteplanung.
5. Windows-Zeitzone, explizite DST-Behandlung, UTC-Speicherung.
6. Zentrale Deutsch/Englisch-Ressourcen und Sprachwechsel.
7. Regression, lesende Dual-Hardwareprüfung, Lizenzprüfung, Windows-Builds.
Beide Geräte nehmen laut Benutzer auf. Keine realen Steueraktionen.

Stand: Schritte 1–6 implementiert; 87 Tests erfolgreich. Native Windows-Builds
werden versionsgetrennt erzeugt. Reale Dual-Stack-Prüfung bestanden; RTSP in
den laufenden Aufnahmen nicht verfügbar. Grenzen/Nachweise: docs/V22_TEST_REPORT.md.
