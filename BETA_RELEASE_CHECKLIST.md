> Current Telescope Desk working documentation. Earlier release facts are preserved unchanged in [the Seestar Studio archive](docs/history/seestar-studio-b3/BETA_RELEASE_CHECKLIST.md). New build status: [minimization report](docs/compliance/MINIMIZATION_REPORT.md).

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

> GitHub-Auftrag vom 7. November 2026: Die Übertragung des aktuellen Standes
> in das bestehende private Repository ist ausdrücklich freigegeben. Details
> und Grenzen: [GITHUB_DELIVERY.md](docs/GITHUB_DELIVERY.md). Frühere Aussagen
> „kein Git/kein Upload freigegeben“ beschreiben den Stand vor diesem Auftrag.

# Telescope Desk Beta — 2.3.0b2

**Telescope Desk Beta – noch nicht freigabereif**

Stand: 7. November 2026. Lokaler Kandidat, keine Veröffentlichung/Weitergabe.
Umfang: Tag-Nacht-Hintergrund, Windows-Standorteinstellungen und der ausdrücklich
beauftragte GoTo-/Autofokus-/Stacking-Bugfix. Keine Veröffentlichung.
Die vorherige b1-Checkliste bleibt in backups/beta-2.3.0b1 erhalten.
Details/Nachweise: docs/B2_TEST_REPORT.md und docs/CONTROL_B2_REPORT.md.

## Implementierung und Tests

- [x] b1-Sicherung mit 23 Dateien per SHA256 überprüft; kein lokales Git.
- [x] Ausgangsregression: 95 Tests; UX-Build: 121 Tests; Steuerungsregression: **154 Tests bestanden**.
- [x] Offline-Sonnenhöhe mit vorhandener Astropy-Bibliothek; keine neue Abhängigkeit.
- [x] Kontinuierlicher Farbverlauf; 0/−6/−12/−18°-Phasen; Standardauf-/untergang
  bei −0,8333° mit Refraktion und Sonnenscheibenradius als Näherung.
- [x] Lokale Ereigniszeiten, UTC/DST, mehrtägige Timeline, Polar-/helle Sommernächte.
- [x] Unveränderte deckende Blöcke, Zoom/Scroll und gemeinsamer Verlauf aller Spuren.
- [x] Bestätigter Standort erforderlich, neutraler Hintergrund ohne Standort;
  standardmäßig aktive, lokal gespeicherte Anzeigeoption.
- [x] Berechnung im begrenzten Worker; alte Ergebnisse verworfen, Fehler neutral.
- [x] Windows-Settings-Button nur bei verweigertem/deaktiviertem Zugriff.
- [x] URI exakt ms-settings:privacy-location, nur explizite Benutzeraktion.
- [x] Fehlerarten getrennt, manueller Pfad bei Startfehler, erneute Abfrage
  ausdrücklich, keine automatische Änderung von Windows-Berechtigungen.
- [x] Alle Texte DE/EN; native Darstellung bei 100 %/emulierten 150 % geprüft.
- [x] Referenzabgleich USNO für drei synthetische Orte, Toleranz <90 Sekunden.
- [x] Siebentägiger Verlauf: 2,378 s; UI-Prüftimer maximal 37 ms Abstand.

## Steuerungskorrektur

- [x] Separates Nur GoTo und bevorzugte vollständige Beobachtungssequenz.
- [x] Tatsächliche Solve-/AF-/Stack-Ereignisse statt ACK als Erfolg behandeln.
- [x] Leerlaufkamera/Preview-/Stack-Freigaben, Standardfilter beibehalten, DE/EN-Gründe.
- [x] Unabhängige Geräte, Widerruf, Abbruch, Reconnect ohne automatische Fortsetzung.
- [x] Echte S50-/S50-Pro-Innenraumtests mit ausdrücklicher Bewegungsfreigabe.
- [x] Fehler 251/279 korrekt erkannt, keine App-Folgeaufnahme nach Solve-Fehler.
- [x] Beide Geräte wieder geparkt; Automatikflags/Montierungsmodus nicht verändert.
- [ ] Vollständige erfolgreiche automatische Beobachtung unter Sternenhimmel.

## Pakete und Sicherheit

- [x] Versionierte Windows-EXE, portable ZIP, Installer und passendes App-Quellpaket.
- [x] Portable EXE: 45 Sekunden, Verlauf/8 Ereignisse, Settings-URI simuliert,
  keine Positionsabfrage, READ ONLY, sauberes Ende (Exit 0).
- [x] Original-Icon, Credits, Lizenztexte und bestehende Funktionen erhalten.
- [x] Finaler b2-Installer-Lebenszyklus und installierte EXE: 1.423 Dateien
  identisch; Installieren/Reinstallieren/Deinstallieren Exit 0, Profil unverändert.
  Verbliebene Altinstanz zuvor mit ausdrücklicher Freigabe beendet.
- [x] ZIP-/Quellhash-/Iconprüfung bestanden; Abschlussstand mit SHA256 gesichert.
- [x] Finale portable/installierte EXE: sauberer Exit 0, READ ONLY, S50 Pro verbunden
  und geparkt. S50 dabei nicht erneut entdeckt; frühere Indoor-Nachweise separat.

## Weiter bestehende Abnahmen und Blocker

1. Genaues natives Quellen-/Patch-/Build-/statische-Bibliotheken-Mapping,
   Microsoft-Laufzeiten, Codec-/Extraktionsrechtsfragen offen (LICENSING.md).
2. Visuelle Windows-Shell-Iconabnahme, echte DPI-/Windows-11-Abnahme,
   Fremd-PC ohne Python, externer S50 und reale Langzeit-/Videotests offen.
3. Echte Windows-Standortabfrage und manuelles Öffnen der Windows-Einstellungsseite
   nicht automatisch durchgeführt. Simulierte Prüfungen sind kein echter Standorttest.
4. Vollständiger automatischer Deep-Sky-Aufnahmeerfolg unter Sternenhimmel offen.
5. Keine Freigabe zur externen Weitergabe oder Veröffentlichung erteilt.

Im ursprünglichen UX-EXE-Lauf wurden keine Teleskope erkannt. Danach echte
Indoor-Steuerung von S50/S50 Pro mit ausdrücklicher Freigabe geprüft; Details
im Steuerungsbericht. Keine S30-/S30-Pro-Hardwaretests, Konten, Cloudfunktionen
oder persönlichen Standortuploads.

Keine weitere Featureentwicklung. Es gilt erneut der verbindliche Feature Freeze. Neue Aufträge
und Testerfeedback-Priorisierung ausschließlich durch Mark. Kein Upload.
