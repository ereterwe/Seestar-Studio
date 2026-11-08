> Current Telescope Desk working documentation. Earlier release facts are preserved unchanged in [the Seestar Studio archive](docs/history/seestar-studio-b3/INSTALLATION.md). New build status: [minimization report](docs/compliance/MINIMIZATION_REPORT.md).

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

# Lokale Installation — 2.3.0b2

Portable: release/TelescopeDesk-2.3.0b2-win64.zip vollständig entpacken,
TelescopeDesk/TelescopeDesk.exe starten. Den gesamten Ordner mit _internal
zusammenlassen. Keine separate Python-Installation erforderlich. Einstellungen
liegen im Benutzerprofil, nicht auf dem USB-Stick/Programmordner.

Optionaler Installer: release/TelescopeDesk-2.3.0b2-setup-win64.exe.
Installation für den aktuellen Benutzer unter LocalAppData/Programs/TelescopeDesk,
Startmenüeintrag, Desktopverknüpfung optional. Keine Administratorrechte nötig.
Vor Upgrade die laufende Anwendung selbst schließen. Installer startet die App
nicht automatisch. Deinstallation entfernt Programmdateien, erhält aber eigene
Konfiguration, Schlüssel, Standorte, Downloads, Pläne und Session-Historie.

Entwicklungsbuild ohne digitale Signatur, keine öffentliche Weitergabe freigegeben.
Eigenständiger Build auf Entwicklungs-PC geprüft; sauberer Fremd-PC ohne Python
und externer S50-Test weiterhin offen. Kein pauschales Kompatibilitätsversprechen.

PC und Geräte müssen im erreichbaren lokalen Netzwerk sein. Geräteadressen
werden dynamisch erkannt. Kein Konto/Cloud-Login erforderlich. Bestehende lokale
SeestarPy-Authentifizierung wird unverändert verwendet. Bei fehlender Einrichtung
öffnet sich der lokale Assistent; später über Einrichtung erneut erreichbar.
Eigene PEM oder berechtigt verwendbare APK/XAPK ausdrücklich auswählen. Niemals
Schlüssel oder APKs in ein weitergegebenes Programmpaket legen.
Details und Grenzen: docs/LOCAL_SETUP.md.

Sky Explorer, lokale Planung und vorhandene Session-Analyse funktionieren ohne
Teleskope/Internet. Ein Beobachtungsstandort muss ausdrücklich bestätigt werden;
er wird nicht automatisch ermittelt. READ ONLY bleibt der Standard.
Während eines Innentests keine Bewegung, Fokussierung oder Aufnahme auslösen.
Externe Testanleitung: docs/EXTERNAL_S50_TEST.md.

V2.2 ergänzt Live View, grafische Planung und Einstellungen für die Sprache.
Ein Ansichtswechsel aktiviert keinen Gerätemodus. Bei fehlendem RTSP-Video
bleibt Live Stack verfügbar. Bestehende V2.1-Pläne über Import laden; die
Originaldateien bleiben erhalten. Neue Pläne werden lokal automatisch gesichert.

Beta-Weitergabestatus: BETA_RELEASE_CHECKLIST.md. Neu: Original-Icon und Über-
Dialog, optionale Standortvorschläge nach Zustimmung. Die tatsächliche Windows-
Positionsabfrage auf einem fremden PC bleibt zu prüfen.
