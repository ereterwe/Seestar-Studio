# Abschließende Prüfung — 2.3.0b2 mit Steuerungskorrektur

7. November 2026. **154 Tests bestanden in 22,16 s** beim finalen Build.
Nachweis: reports/build-b2-verified.log. Der astronomische Erfolgsablauf ist
simuliert; reale Indoor-Steuerung beider Modelle und Grenzen stehen im
[Steuerungsbericht](CONTROL_B2_REPORT.md).

- Neue portable EXE 60 s und installierte EXE 50 s tatsächlich gestartet;
  beide Exit 0 und clean_shutdown:true, Control Mode:false.
- S50 Pro authentifiziert/verbunden/geparkt in beiden finalen EXE-Läufen.
  S50 in diesen Läufen und einem separaten frischen Discovery nicht erkannt;
  Ursache nicht festgestellt. Zuvor erfolgreich geprüfte S50-Befehle bleiben
  ausdrücklich getrennte Nachweise. Kein neuer paralleler Livebildtest behauptet.
- Beide EXEs: nativer Planer-Verlauf, acht Sonnen-/Dämmerungsereignisse,
  Windows-Settings-URI simuliert korrekt, keine echte Positionsabfrage.
- Native DE/EN-Steuerungsoberfläche, bestätigte Geräteauswahl, erhaltenes
  Original-Icon und lokale Lizenzverweise geprüft. Kein Test einer Sonnenausrichtung.
- Echter lokaler Installer: Installieren + Reinstallieren erfolgreich, 1.423
  Payload-Dateien byteidentisch; Startmenü/Desktop/Deinstallations-Icon korrekt.
  Deinstallation Exit 0; Programm, Verknüpfungen und Registrierung entfernt;
  Einstellungen/Session-Daten per Vor-/Nachhash unverändert.
- ZIP-Integrität und App-Quellhash geprüft, 434 Lizenzdateieinträge, keine
  unerlaubten Schlüssel/APKs/Datenbanken/Logs im Paket. 155 eigene Textdateien
  geprüft, keine Musterfunde. 44 Pakete / 139 native Dateien inventarisiert.
- Alle sieben Original-Iconauflösungen in EXE und Installer byteidentisch.
  39 Upstream-Quellarchive zusätzlich verifiziert/gebündelt; kein Nachweis,
  dass alle nativen Corresponding-Source-/Build-Fragen damit geklärt wären.
- Nach dem Installertest nur Abschlussdokumentation neu gepackt. EXE und
  sämtliche Laufzeitdateien bleiben per Manifest identisch zum geprüften Stand.

Lokale Nachweise: reports/b2-control-exe.json, b2-control-installed.json,
beta-installer-result.json, release-audit.json, beta-icon-resources.json,
beta-security-audit.json, b2-control-runtime-manifest.json. Private Screenshots
und reale Diagnosen liegen ausschließlich in reports/ bzw. der lokalen Sicherung.
Pakete und Berichte: backups/beta-2.3.0b2, SHA256.json. Kein lokales Git.

**Feature Freeze. Keine Veröffentlichung oder Weitergabe.** Erfolgreiche
Gesamtaufnahme unter Sternen, Fremd-PC, Windows 11/DPI, Langzeit-/Video- und
Standorttests sowie Lizenz-/native Quellenfragen bleiben gesondert offen.
Die folgende Dokumentation beschreibt den gesicherten früheren UX-Ausgangsbuild.

## Historischer UX-Bericht

# Ergänzung: Steuerungskorrektur derselben Version

7. November 2026: Nach dem ursprünglichen UX-Auftrag zusätzlich ausdrücklich
beauftragter GoTo-/Autofokus-/Stacking-Bugfix. 154 Regressionstests erfolgreich.
Reale Indoor-Prüfung beider Modelle und detaillierte Grenzen:
[CONTROL_B2_REPORT.md](CONTROL_B2_REPORT.md). Der folgende UX-Bericht beschreibt
den gesicherten Ausgangsbuild; neue endgültige Paketprüfungen werden ergänzt.

# Seestar Studio 2.3.0b2 — Prüfung vom 7. November 2026

Nur die beiden ausdrücklich freigegebenen Änderungen: astronomischer
Tag-Nacht-Hintergrund und Windows-Standorteinstellungen bei Zugriffsproblemen.
Keine neuen Abhängigkeiten, keine neue Gerätefunktion, kein Upload.

## Ausgangspunkt und Regression

Kein lokales Git-Repository; die b1-Sicherung mit 23 Dateien erneut vollständig
per SHA256 geprüft. Ausgangssuite: **95 bestanden**, 12,43 Sekunden.
Abschließende Suite im b2-Build: **121 bestanden**, 18,10 Sekunden.
Nachweise lokal: reports/b2-baseline-tests.log und reports/build-b2.log.
Alle bisherigen 95 Tests bleiben enthalten. Neue Fälle in test_solar.py und
test_location_b2.py; keine reale Standortabfrage oder Berechtigungsänderung.

## Astronomie und Darstellung

Astropy 8.0.2 unverändert wiederverwendet. Refraktion/Sonnenradius über den
Standardhorizont −0,8333°, Dämmerung geometrisch bei −6/−12/−18°.
Methodik und Quellen: DAY_NIGHT_BACKGROUND.md.

Sonnenauf-/untergang und bürgerliche Dämmerung für drei frei gewählte
Teststandorte am 20. März 2026 gegen USNO-Referenzdaten geprüft: alle unter
90 Sekunden Abweichung zu den auf Minuten gerundeten Referenzen. Keine
persönlichen Koordinaten an den Dienst gesendet. Diese einmalige Online-
Entwicklungsprüfung ist kein Bestandteil der Anwendung oder Testsuite.
Alle Dämmerungsereignisse zusätzlich mit Astropy-Höhen vor/am/nach dem Ereignis
geprüft. Tests decken Polartag, Polarnacht ohne durchgehende astronomische
Dunkelheit, helle Sommernächte, beide Hemisphären, 23-/25-Stunden-Nächte,
mehrtägige Pläne und Standortänderungen ab.

Renderprüfungen: gemeinsame Farben aller Gerätespuren, deckende unveränderte
Beobachtungsblöcke, absolute Ereignispositionen, Zoom, horizontales Scrollen,
neutrale Rückkehr beim Ausschalten. Einstellungen werden lokal wiederhergestellt.
Fehlender Standort startet keinen Worker und keinen Positionsabruf. Worker-Test
verifiziert das Verwerfen alter Ergebnisse, Cache, Fehler ohne Wiederholschleife
und sauberes Ende. Die neue Berechnung steuert keine Geräte.

Native DE/EN-Darstellung bei 100 % sowie QT_SCALE_FACTOR=1.5 geprüft. Kein
zurückgebliebener deutscher Text im englischen Prüflauf erkannt. Verlauf,
Markierungen, Beobachtungsblöcke und neuer Standortbutton lesbar.
150-%-Qt-Skalierung ist kein Nachweis echter Windows-DPI-/Monitorwechsel.
Bei engem Platz werden Markertexte ausgelassen, ihre Linie und Tooltip bleiben.

Zusätzlicher Lauf mit sieben Tagen: 10.081 Sonnenhöhen, 56 Ereignisse,
2,378 Sekunden Berechnung; UI-Prüftimer lief 118-mal, größte gemessene Lücke
37 Millisekunden (reports/b2-performance.json). Das ist ein lokaler kurzer
Reaktionsfähigkeitstest, kein Langzeit-/Speicherleck- oder Fremd-PC-Nachweis.

## Standortzugriff

Simulierte Kategorien: Berechtigung verweigert, deaktivierter Zugriff,
vorübergehend keine Daten, sonstiger Fehler, Timeout, fehlende API sowie
bekannte Windows-Fehlercodes. Unbekannte Fehler werden nicht pauschal als
fehlende Berechtigung angezeigt. Direktbutton nur für denied/disabled.

Erfolgreicher und fehlgeschlagener URI-Aufruf (False sowie Ausnahme) getestet.
Abgefangener URI exakt `ms-settings:privacy-location`; keine automatische
Folgeabfrage. Dialog bleibt offen, erneute explizite Abfrage nach simuliertem
Berechtigungswechsel funktioniert. Manuelle Eingabe, Bestätigung und DE/EN-
Wechsel bleiben erhalten. Echte Windows-Einstellungen nicht verändert;
echte Standortabfrage und manuelle Windows-Endabnahme weiterhin offen.

## Windows-Build

Version 2.3.0b2; Python 3.12.10, PySide6/Qt 6.12.0, SeestarPy 0.8.0.
Buildzeit 2026-11-07T10:39:10.227200+00:00.
App-Quellhash: 15e2aeacd2c401ffe28fcf765ae8ff0dc8ac39bd8c854bcb37a1ea59d8c01fe0.

PyInstaller-Build und Inno-Setup-Installer erfolgreich erstellt. Portable
EXE 45 Sekunden mit isoliertem QA-Profil geprüft, Exit 0, sauberes Beenden,
14.034 Katalogeinträge, berechneter Tag-Nacht-Verlauf und acht Ereignisse.
Standort-Fehler und Settings-URI innerhalb der gepackten Anwendung simuliert;
URI abgefangen, Windows-Seite nicht geöffnet. Kein echter Standort angefordert.
Icon, vorhandene Lizenz-/Quellverweise und echte Versionsdaten vorhanden.
Nachweis: reports/b2-exe.json; Screenshots sind private QA-Dateien.

Während dieses Laufs keine Teleskope erkannt; kein neuer Hardwareerfolg
behauptet. READ ONLY blieb aktiv. Bisherige S50-/S50-Pro-Nachweise siehe
BETA_TEST_REPORT.md und V22_TEST_REPORT.md; keine S30-Hardwaretests.

**Installierter b2-Build noch ausstehend:** Eine bestehende Seestar-Studio-
Instanz läuft. Sie wurde nicht beendet. Der Benutzer wurde um das Schließen
für den isolierten Installertest gebeten. Der erfolgreiche b1-Installertest
ist kein Ersatz für diesen b2-Test. Installer nicht über laufende App erzwungen.

## Grenzen und Weitergabe

Anwendung/Installer nicht digital signiert. Tatsächlicher frischer Windows-PC
ohne Python, externer S50, echter Standortdienst, Windows-Shell-Iconabnahme,
reale Video- und Langzeittests bleiben offen. Frühere Lizenz-/native Quellen-
Zuordnung und Extraktionsrechtsfragen sind durch b2 nicht gelöst.
Freigabestatus: ../BETA_RELEASE_CHECKLIST.md. Keine Veröffentlichung oder
Weitergabe, kein Zugriff auf private Schlüssel. Frühere Releases bleiben erhalten.
