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

# Beta 2.3.0b1 — Abschluss, 7. November 2026

Lokaler Beta-Kandidat fertig gebaut; **FEATURE FREEZE**. **95 Tests bestanden**.
Standortvorschläge, Original-Icon, DE/EN-Über-Dialog und bereinigte Diagnose
implementiert. Portable und installierte EXE sauber gestartet/beendet. Echter
lokaler Installer-Lebenszyklus erfolgreich, persönliche Einstellungen erhalten.
Quellhash/ZIP/Sicherheitsprüfungen bestanden; 39 Upstream-Archive separat gesichert.
Pakete und Abschlussdokumente: backups/beta-2.3.0b1 (SHA256.json).

**Seestar Studio Beta – noch nicht freigabereif**: native Quellen-/Lizenzklärung,
visuelle Windows-Shell-Iconabnahme und externe/reale Abnahmen offen. Aktuelle
Beta-Läufe erkannten keine Teleskope; frühere Hardwarebelege bleiben getrennt.
Keine Veröffentlichung, kein Standortabruf, keine echten Steueraktionen.
Details: BETA_RELEASE_CHECKLIST.md und docs/BETA_TEST_REPORT.md.
Neue Änderungen und Feedbackbearbeitung ausschließlich nach neuem Auftrag.

## Historischer Entwicklungsverlauf (nachfolgende Statusangaben sind historisch)

# Aktueller Stand — V2.2 / 6. November 2026

Entwicklungsstand **2.2.0.dev1**. Die folgenden Angaben ersetzen ältere
Erreichbarkeits-/Versionsangaben im darunter erhaltenen Entwicklungsverlauf.

- Live View pro Gerät implementiert: Qt Multimedia/FFmpeg, unabhängige Worker,
  begrenzter Bildpuffer, FPS, Kameraerkennung per RTSP-SDP, Reconnect, separate
  Zoomzustände, Screenshot und vorhandene Vollbild-/Maximierungsfunktionen.
  Kein Gerätemoduswechsel, keine streamaktivierenden Geräte-RPCs.
- Grafischer Planner mit persistenten Slots, 5-Minuten-Raster, Drag/Resize,
  Kontextmenü, Wechselzeiten, Konflikten, Offline-Geräten und lokalen Plänen.
  Optimierung wird erst nach Prüfung einer Vorschau übernommen.
- Windows-Zeitzone als Vorgabe, UTC-Speicherung, explizite Behandlung von
  doppelten/nicht existierenden Uhrzeiten; V2.1-Import ohne Zeitverschiebung.
- Zentrale DE/EN-Ressourcen, Windows-Spracherkennung, unmittelbarer Wechsel,
  lokalisierte Zahlen/Datumswerte und Qt-Standarddialoge.
- 87 automatisierte Tests bestanden. Native DE/EN-Ansichten mit synthetischen
  Geräten geprüft; Bericht `reports/v22-ui-latest.json`. Keine echten Videobilder
  in diesem UI-Test. Details: `docs/V22_TEST_REPORT.md`.
- Reale lesende Dual-Geräteprüfung, 93 Sekunden: S50 vier Stackbilder,
  Zähler 63→66; S50 Pro sechs Stackbilder, Zähler 29→34. Stage blieb Stack.
  Beide lieferten dabei kein verfügbares RTSP-Video. Kein Moduswechsel und
  keine Aufnahmeunterbrechung ausgelöst. Echte Live-View-Abnahme ausstehend.
- FFmpeg-Lizenzangabe und Buildkonfiguration lokal geprüft, zusätzliche
  Lizenztexte aufgenommen. Vollständige rechtliche Veröffentlichungsklärung offen.

V2.1 bleibt geöffnet und unverändert unter `dist/SeestarStudio`. Ein erster
Buildversuch scheiterte an einer gesperrten DLL; 92 fehlende Dateien wurden aus
V2.1-Backup wiederhergestellt, alle Inhalte gegen das Backup geprüft (0 Abweichungen).
Neue Builds liegen getrennt unter `dist/2.2.0.dev1/SeestarStudio`.
Keine Veröffentlichung, kein Push, keine echte Steueraktion. Lokal weiterhin
kein Git-Repository; vorhandene Sicherungen bleiben erhalten.

Finaler V2.2-EXE-Test: beide realen RAW-Stackbilder und Telemetrie sichtbar,
Katalog/Offline-Astronomie verfügbar, Control Mode aus, Exitcode 0 und sauberes
Beenden. Die laufende V2.1-Instanz blieb erhalten. Portable ZIP geprüft:
1.406 Laufzeit-/152 Quellen-/225 Lizenzeinträge, 0 verbotene Dateitypen.
EXE: dist/2.2.0.dev1/SeestarStudio/SeestarStudio.exe.
Paket und Installer: release/SeestarStudio-2.2.0.dev1-win64.zip bzw.
release/SeestarStudio-2.2.0.dev1-setup-win64.exe.
V2.2-Installation/Upgrade noch nicht ausgeführt; laufende Benutzerinstanz geschützt.

## Historischer Verlauf (ältere Versionsstände)

# Fortschritt — 6. November 2026

## Aktueller Stand
Version **2.1.0.dev1** lokal implementiert und gebaut: Einrichtungsassistent,
geschützte PEM/APK/XAPK-Imports, lesender Verbindungstest, Diagnoseexport,
portables ZIP und Benutzer-Installer. 71 Tests bestanden, Exitcode 0.
Native EXE und lokale Installation/erneute Installation/Deinstallation geprüft.
Details und offene Abnahme: docs/V21_TEST_REPORT.md.

S50 zunächst lesend erreichbar, am Ende der Fortsetzung UDP/TCP nicht mehr
erreichbar. Abschließender EXE-Test ohne Gerät; keine neue Livebild-Abnahme.
V2.1 ist noch nicht extern abgenommen. V3 bleibt nachgelagert.

### Historie dieses Entwicklungsstands
V2 abgeschlossen und unter `backups/v2-2.0.0.dev2` gesichert. Benutzer hat
anschließend zum Weiterarbeiten aufgefordert: V2.1 begonnen.
S50 wieder online, steht drinnen. 45 Sekunden lesend geprüft: verbunden,
authentifizierte Telemetrie, kein Bild verfügbar, sauberer Shutdown.
Nachweis `reports/v21-s50-indoor-readonly.json`. Keine Steueraktionen.

Version 2.0.0.dev2: Phasen 1–5 implementiert. 61 automatisierte Tests erfolgreich.
Finaler Windows-Build und Offline-Startprüfung erfolgreich abgeschlossen:
alle sechs nativen Tabs, 14.034 Katalogeinträge, Offline-Nachtberechnung,
Control Mode gesperrt, sauberes Herunterfahren, Exitcode 0.
Dieser V2-Abschluss war die Grundlage für V2.1; keine Veröffentlichung freigegeben.

## Funktionsumfang
1. File Manager: lesende SMB-Listen, sichere rekursive Downloads, Abbruch/Resume,
   Duplikatschutz, Größenprüfung, lokale Hashnachweise, Vorschauen, Bandbreitenlimit.
2. Sky Explorer: 14.034 lokale OpenNGC-Einträge, Messier/Caldwell/NGC/IC, Aliase,
   Standortbestätigung, Offline-Nachtberechnung und nominale Kamerabildfelder.
3. Optionaler Control Mode: READ ONLY als Standard, explizites Gerät und einzelne
   Bestätigung, Serienprüfung auf derselben Verbindung, keine Mutation-Retries.
4. Observation Planner: lokale Pläne, Dauer/Wechselzeit, Konflikte, Sichtbarkeit,
   heuristische Reihenfolge und Mehrgeräte-Timeline. Keine Ausführung.
5. Session-Analyse: SQLite, beobachtete Sessiongrenzen, unbekannte/lückenhafte
   Werte, ungefähre Integration, Unterbrechungen und Vergleichskurven.

## Reale Hardwaretests (bereits vor Abschaltung erfolgt)
S50 und S50 Pro: Discovery, Authentifizierung, Telemetrie, unabhängige Livebilder,
Viewer-Trennen/Reconnect; File-Manager-Listen und je ein JPEG mit Abbruch/Resume,
Größen- und Duplikatprüfung. Native Dateiansicht geprüft. Beim frühen Sky-Explorer-
Probe-Lauf beide Geräte verbunden und neue Bilder empfangen. Berichte:
docs/TEST_REPORT.md, docs/PHASE1_TEST_REPORT.md, reports/sky-ui.json.
Der ältere Sky-Probebericht enthält für Ziel/Stage null wegen falscher
Berichtsfeldnamen; daraus keine Aussage über diese Werte ableiten.

## Offline / simuliert geprüft
V2-Basis mit 61 Tests (V2.1 insgesamt 71): Viewer-Regression, Mehrgeräte-Isolation, Dateien/Resume/Pfade,
Katalog/Aliase, Zeitzonen/DST/Polartag, rein lokale Astronomie, Gerätebestätigung,
Freigabewiderruf, falsche Identität, keine Wiederholung nach Antwortverlust,
Planpersistenz/Konflikte/Fenster, SQLite-Neustarts/Zählerwechsel/Ausfälle.
Zwölf Stunden virtuelle Messwerte prüfen Plotbegrenzung und Lückendarstellung;
das ist kein zwölfstündiger realer Lauf. Native V2-Tabs mit simulierten Geräten
und synthetischem Standort visuell geprüft. Kein realer Steuerbefehl gesendet.

## Build und Sicherungen
Kein Git-Repository vorhanden. Ausgangsstand unter backups/baseline-20261105-205910,
Phase 1 unter backups/phase1-2.0.0.dev1, startbarer Phase-2-Build unter backups/phase2,
Phase-4-Quellen unter backups/phase4. Build nutzt fixierte Abhängigkeiten;
Astropy-Hook und Qt-DLL-Suche geprüft. V2-Archiv: release/SeestarStudio-2.0.0.dev2-win64.zip.
Aktuelle EXE unter dist/SeestarStudio/SeestarStudio.exe ist Version 2.1.0.dev1. Nachweise:
reports/v2-final-exe.json, reports/tests-final.log, reports/release-audit.json.
ZIP-Integrität und Ausschluss von privaten Daten-/Schlüsseldateien geprüft;
kein Ersatz für eine vollständige Sicherheits-/Lizenzprüfung vor Veröffentlichung.

## Grenzen / ausstehend
Aktueller Erreichbarkeitsstand siehe oben; Ursache des letzten Timeouts unbekannt.
Reale Steuerungstests
nur nach neuer ausdrücklicher Freigabe. Große reale Transfers, mehrstündiger
Gesamtbetrieb, echte Strom-/Netzausfälle, Fremd-PC ohne Python und externe S50-
Tests offen. Keine reale S30-/S30-Pro-Hardware und keine entsprechenden Behauptungen.

V2.1 lokal implementiert: Setup-Assistent/PEM-/APK-/XAPK-Import, Installer,
Diagnose. Externe Portabilitätsprüfung bleibt offen. Bestehende reale
Schlüsselkonfiguration unverändert. Lokaler Artefaktcheck: 0 verbotene Dateien,
1358 Laufzeit-Einträge, 135 Quellen-Einträge, 220 Lizenzeinträge.
V3: vollständige Lizenz-/Quellen-/Sicherheitsprüfung, Qt/native Abhängigkeiten,
rechtliche Prüfung der Extraktion, privater Datenbestand/eventuelle Git-Historie,
öffentliche Release-Vorbereitung. LICENSING.md und COMPATIBILITY.md beachten.
