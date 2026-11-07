# Beta 2.3.0b1 — Abschlussprüfung, 7. November 2026

**Seestar Studio Beta – noch nicht freigabereif**

Lokale Beta-Pakete vorbereitet, keine Veröffentlichung oder Weitergabe.
Die Entwicklung dieses Auftrags endet mit Feature Freeze. Offene Abnahmen
und Lizenzfragen sind keine impliziten Folgeaufträge.

## Build und automatisierte Tests

Python 3.12.10 x64, SeestarPy 0.8.0, PySide6/Qt 6.12.0, PyInstaller 6.22.3.
Host Windows 10 (10.0.19045), keine Aussage über einen getesteten Windows-11-PC.
Buildzeit laut Metadaten: 2026-11-07T00:43:08.806598+00:00.
App-Quellhash: c08b7c59f6fa779a65d6baa4f178ef84fb65bfbbd38f100e8ecacf288644adeb.

**95 Tests bestanden in 11,98 Sekunden** (`reports/build-beta.log`).
Die neuen Tests prüfen Windows-Standortantworten, fehlende Dienste, Ablehnung,
Genauigkeit/Höhenbezug, Abbruch, manuelle Bearbeitung, Bestätigungsgrenze,
Zeitzonenvorschlag, lesenden Seestar-RPC mit Identitätsprüfung, Über-Dialog,
Versionsdaten, Dateiverweise und Icon-Größen. Vorhandene Tests für Streams,
Mehrgerätebetrieb/Ausfall, Dateitransfers, Planner/DST, Analyse, Einrichtung,
Steuerungssperren und Sprachwechsel laufen weiter erfolgreich.
Diese Tests verwenden Simulationen bzw. lokale Testdaten, keine realen
Windows-Positionsdienste und keine realen Steueraktionen.

## Gepackte Windows-Ausführung

Portable EXE: 45 Sekunden; über den Produktionsinstaller installierte EXE:
120 Sekunden. Beide mit isoliertem QA-Profil, 1920×1080, allen sechs Modulen,
14.034 Katalogobjekten und berechneter Sichtbarkeit an einem synthetischen Ort.
Beide sauber beendet, Exit 0; Icon und lokale Lizenz-/Quellverweise vorhanden;
WinRT-Projektion importierbar; Standort nicht angefordert; Control Mode aus.
Nachweise: `reports/beta-exe.json`, `reports/beta-installed.json`.
Keine Geräte in diesen Läufen erkannt; daher kein aktueller Beta-Hardwaretest.
Der Entwicklungs-PC besitzt Python; die EXE nutzt ihre gebündelte Laufzeit.
Ein frischer PC ohne Python wurde nicht getestet.

## Installer

Tatsächlicher Inno-Setup-Installer im abgegrenzten QA-Verzeichnis:
Installation, erneute Installation, Ausführung und Deinstallation jeweils
erfolgreich. Installierte EXE identisch zum portablen Build. Startmenü- und
Desktopverknüpfung angelegt, Iconpfade und UninstallDisplayIcon korrekt.
Danach Programm, Verknüpfungen und Registrierung vollständig entfernt;
Hashes der geprüften vorhandenen Einstellungen/Session-Datenbank unverändert.
Keine Schlüssel gelesen. Nachweis: `reports/beta-installer-result.json`.
Das ist ein lokaler Installertest, kein Upgradebeweis für jede frühere Version
und keine externe Neuinstallation. EXE und Installer sind nicht signiert.

## Visuelle Prüfung und Icon

Original-SVG, PNG und ICO vorhanden. EXE und Installer enthalten identische
Original-Icon-Bilddaten für 16/24/32/48/64/128/256 Pixel
(`reports/beta-icon-resources.json`). Natives Qt-Rendering des Über- und
Standortdialogs im gepackten Build geprüft. DE/EN-UI mit synthetischen Geräten
bei 100 % und QT_SCALE_FACTOR=1.5 betrachtet; Über-Dialog scrollbar, zentrale
Dialogtexte lesbar. Planner kürzt schmale Einträge bewusst; vollständige
Details bleiben über Auswahl/Bearbeitung zugänglich.

Der Windows-Computer-Use-Zugriff auf Explorer scheiterte mit
„Computer Use app approval timed out“. Keine UI-Aktion danach ausgeführt.
Explorer-/Taskleisten-/Startmenü-/Desktop-/installierte-Apps-Icons deshalb
visuell **nicht abschließend abgenommen**. PE-Ressourcen und Shortcutpfade
belegen die Einbindung, nicht den tatsächlichen Shell-Cache. Kein Icon-Cache
gelöscht. 150-%-Qt-Skalierung ersetzt keinen echten Windows-DPI-/Monitorwechsel.

## Hardwarebelege und Grenzen

Die gesicherte V2.2-EXE zeigte beide echten RAW16-Livestacks (2160×3840) und
Telemetrie während laufender Aufnahmen. Ein separater 93-Sekunden-Lauf hatte
vier bzw. sechs neue Stackbilder mit steigenden Zählern. Vorherige lesende
Downloadtests sind in PHASE1_TEST_REPORT.md dokumentiert. Keine Aufnahme
unterbrochen oder Steuerung ausgelöst. V22_TEST_REPORT.md beschreibt Grenzen.

Kein echter RTSP-Stream im getesteten Stackmodus; Live View einschließlich
Kamerawechsel weiterhin nur lokal/simuliert geprüft. Keine S30/S30-Pro-Hardware.
Ausstehend: echter Windows-Standort nach persönlicher Zustimmung, Seestar-
Positionsabruf, externe Authentifizierung, externer S50/Fremd-PC, mehrstündiger
realer Gesamtbetrieb, tatsächliche Windows-11-/DPI-/Shell-Abnahme. Kurze saubere
Läufe sind kein Nachweis der Langzeitstabilität oder Abwesenheit jedes Speicherlecks.

## Lizenz, Sicherheit und lokale Pakete

44 installierte Pakete, 139 native PE-Dateien technisch inventarisiert;
39 unveränderte Upstream-Archive mit Prüfsummen, 204 originale zusätzliche
Lizenz-/Notice-Dateien und 98 Qt-Attributionsmanifeste gesammelt. Qt-GPL-Module
nicht pauschal als LGPL eingestuft. Native Build-/Patch-/statische Bibliotheks-
Zuordnung, Laufzeitbedingungen und Extraktionsrechtsfragen bleiben offen.
Das Upstream-Archiv ist Prüfmaterial, kein bestätigter vollständiger
Corresponding-Source-Nachweis. Einzelheiten: ../LICENSING.md.

Autorenquellen-Musterscan ohne Treffer; Laufzeit-/App-Quellpaket ohne private
Dateitypen, abgesehen vom öffentlichen certifi-CA-Bundle. Keine Benutzerkeys,
APKs, Standortkonfigurationen, privaten Bilder, Logs oder Session-Datenbanken
in diese Pakete übernommen. Unveränderte Upstream-Quellen können eigene
öffentliche Testfixtures enthalten; sie stammen nicht aus dem Benutzerprofil.
Die Prüfungen sind keine Garantie gegen jede unbekannte sensible Zeichenfolge.
Lokal kein Git; offizielles Remote lieferte null Referenzen. Keine erreichbare
Historie geprüft, keine Historie verändert und kein Upload.

Artefakte unter `release/`: portable ZIP, Installer, App-Source-ZIP,
separates Upstream-Source-ZIP, jeweils 2.3.0b1. Das App-Quellarchiv stimmt
per Hash mit dem EXE-Buildeingang überein. Pakete und Abschlussdokumente
unter `backups/beta-2.3.0b1/` mit SHA256 gesichert. Private QA-Berichte und
Screenshots werden weder in Git noch in Release-Quellen aufgenommen.

Der endgültige Freigabestatus und die verbindlichen offenen Punkte stehen in
../BETA_RELEASE_CHECKLIST.md. Auch geschlossene externe Weitergabe benötigt
geklärte Lizenzpflichten und Marks ausdrückliche Freigabe.
