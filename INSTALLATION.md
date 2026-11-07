# Lokale Installation — 2.3.0b2

Portable: release/SeestarStudio-2.3.0b2-win64.zip vollständig entpacken,
SeestarStudio/SeestarStudio.exe starten. Den gesamten Ordner mit _internal
zusammenlassen. Keine separate Python-Installation erforderlich. Einstellungen
liegen im Benutzerprofil, nicht auf dem USB-Stick/Programmordner.

Optionaler Installer: release/SeestarStudio-2.3.0b2-setup-win64.exe.
Installation für den aktuellen Benutzer unter LocalAppData/Programs/SeestarStudio,
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
