# Lizenzklärung — aktueller Ergänzungsstand

Native Originalherkunft und Lieferanten-SBOMs geprüft; Originalquellen/Patches/
Buildrezepte ergänzt. Kontrollierter zlib-Neuaufbau mit Test erfolgreich.
APK-Eigenbeschaffung und Verantwortungsabgrenzung auf Deutsch/Englisch ergänzt.
Codec- und Microsoft-Bedingungen für die rechtliche Prüfung zusammengestellt.
Aktueller Status: [TECHNICAL_LICENSE_RESOLUTION.md](docs/TECHNICAL_LICENSE_RESOLUTION.md).
Ergänzter Prüfstand: 169 Tests bestanden; portable/installierte EXE sauber beendet;
Installation/Neuinstallation/Deinstallation erfolgreich, 1.642 Dateien ohne Abweichung.
Keine neuen Hardwaretests. Original-b3-Pakete anhand ihrer Hashes unverändert geprüft.
Noch offen bleiben die dort konkret bezeichneten Hersteller-Buildnachweise und
rechtlichen Entscheidungen. Neue öffentliche Binärdateien bleiben bis zur Klärung
zurückgestellt; alte b3-Dateien und ihre Hashes bleiben unverändert.

> B3-Prüfung abgeschlossen: 166 Tests; portable und installierte EXE starten und
> beenden sich sauber; Installation/Neuinstallation/Deinstallation erfolgreich,
> 1.443 Dateien ohne Abweichung und persönliche Einstellungen unverändert.
> ZIP, Installer, App-Quellen und 40 Upstream-Archive liegen lokal vor.
> Quellcode-Push beauftragt; native Quellen-/Lizenzblocker bleiben dokumentiert.

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

# 2.3.0b2 — Feature Freeze

Lokale Implementierung, 154 Tests, EXE/ZIP/Installer und Installationslebenszyklus
abgeschlossen. Keine weiteren Funktionen oder Hardwarebewegungen ohne Auftrag.
Sicherung: backups/beta-2.3.0b2; frühere Builds bleiben erhalten.

Ausstehende separate Abnahmen:
1. Vollständige automatische Beobachtung unter freiem Sternenhimmel: erfolgreiches
   Plate Solving, Autofokus, akzeptierte Subframes und paralleler Langzeitbetrieb.
2. Erneute Discovery des S50 prüfen, sobald es wieder erreichbar ist. Es bestand
   die Indoor-Tests; im letzten EXE-/Discovery-Lauf erschien nur noch der S50 Pro.
   Ursache nicht festgestellt, kein weiterer Bewegungs-/Aufnahmeversuch nötig.
3. Externer Windows-PC ohne Python, fremdes S50, tatsächliche Windows-11-/DPI-/
   Shell-Icon-Abnahme und optionale echte Standortabfrage.
4. Offene GPL/LGPL-/native Quellen-/Build-/Microsoft-/Codec-/Extraktionsfragen.
5. Veröffentlichung oder Weitergabe ausschließlich nach ausdrücklicher Freigabe.

Der Installer-Test wurde sauber deinstalliert; persönliche Einstellungen und
Session-Daten blieben erhalten. Anwendung über die lokale EXE oder den Installer
starten. Keine automatische Installation/Veröffentlichung im Anschluss.
