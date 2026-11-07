# V2.1 — lokaler Entwicklungsbuild 2.1.0.dev1

Stand: 6. November 2026. Keine öffentliche Freigabe.

## Automatisierte und native Prüfungen

- 71 pytest-Tests bestanden, Prozess-Exitcode 0. Gesamte V2-Regression enthalten.
- PEM/APK/XAPK ausschließlich mit zur Laufzeit erzeugten synthetischen RSA-Schlüsseln.
  Kein echter Schlüssel wurde für Importtests kopiert. Validierung, lokale
  SeestarPy-Extraktion, Archivpfade, Bestätigung, Abbruchbereinigung geprüft.
- Windows-DACL über icacls geprüft: geschützt, aktueller Benutzer und SYSTEM.
- Separater lesender Verbindungstest: expliziter Schlüsselpfad, Identitätsabweichung
  abgewiesen, keine globale Authentifizierungsänderung, keine Steuer-RPCs.
- GUI-Test mit ausstehendem Import: Abbruch wartet auf Ergebnis und bereinigt es.
- Nativer Assistent: drei Seiten visuell geprüft, synthetisches Profil, Abbruch
  ohne Aktivierung; reports/setup-ui.json und setup-*.png.
- Diagnoseexport: private Testwerte ausgeschlossen; boolesche Capability-Whitelist.
- Windows-Einzelinstanzmarker: zweite Instanz erkannt, Handle nach Schließen frei.
- Eigenständige EXE: 1920×1080, sechs Tabs, 14.034 Objekte, Offline-Nachtberechnung
  mit synthetischem Standort, READ ONLY, sauberer Shutdown, Exitcode 0.
  reports/v21-exe.json. Keine Geräte beim abschließenden EXE-Test erreichbar.
- Inno-Installer: Installation, erneute Installation und Deinstallation Exitcode 0.
  Installierte EXE identisch; Startmenü erstellt/entfernt, Registrierung entfernt,
  vorhandene Einstellungen/Historie unverändert; App nicht automatisch gestartet.
  Separater lokaler Testordner, reports/installer-qa.json. Kein Fremd-PC-Test.

## Echte Hardware in dieser Fortsetzung

S50 stand drinnen. Zunächst 45 Sekunden Discovery, Authentifizierung und Telemetrie
erfolgreich, sauberer Shutdown, kein Bild verfügbar. Nachweis:
reports/v21-s50-indoor-readonly.json. Der neue Einrichtungs-Verbindungstest wurde
danach einmal erfolgreich lesend am S50 ausgeführt (Toolausgabe dokumentiert).
Keine Importe/Aktivierungen echter Schlüssel, keine Steueraktion.

Bei der abschließenden Wiederholung kein UDP-Gerät mehr gefunden. seestar.local
löste noch auf, aber der Kommandokanal antwortete nicht auf den TCP-Test
(Timeout; reports/s50-reachability-latest.json). Ursache nicht festgestellt.
Der abschließende EXE-Test ist deshalb **keine Live-Hardware-Abnahme**.
Die alten erfolgreichen S50/S50-Pro-Viewer- und Downloadtests bleiben separat
in den V1-/V2-Berichten erhalten. Keine S30-/S30-Pro-Hardwaretests.

## Ausstehend

Externer PC ohne Python, externe S50-Ersteinrichtung mit eigener echter Quelle,
neue nächtliche Dual-Livestack-Abnahme, mehrstündiger realer Dauerbetrieb,
reale Steuerung nur nach ausdrücklicher Freigabe. Rechts-/Lizenz-/vollständige
Source-/Sicherheitsprüfung vor öffentlicher Weitergabe offen.
