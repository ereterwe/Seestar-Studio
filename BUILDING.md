# Windows-Build

B3 wird lokal neu gebaut; der Quellcode-Push ist beauftragt. Bestehende b2-Dateien
bleiben erhalten. Neue Pakete liegen unter `dist/2.3.0b3` und `release/*2.3.0b3*`.
Quellen-/Austauschprüfung: [COMPLIANCE_WORKFLOW.md](docs/COMPLIANCE_WORKFLOW.md).
Die Spec entfernt neun unbenutzte Qt-Dateien mit Importprüfung.

Lokaler Entwicklungsbuild, keine Veröffentlichungsfreigabe. Windows x64,
Python 3.12 x64. Im Projektordner:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\build.ps1
```

Buildskript führt pytest aus, erstellt den PyInstaller-Ordnerbuild und ein ZIP
unter `release/`. Den gesamten Anwendungsordner verwenden. Qt-DLLs bleiben
separat und austauschbar. Der PATH wird während der DLL-Auflösung kontrolliert,
damit keine fremde ICU-Version aus anderen Programmen eingebaut wird.
Der lokale Astropy-Hook schließt optionale Plot-/Testsammlungen aus; der von
Astropy zur Laufzeit importierte TestRunner bleibt enthalten.

Katalogdaten werden aus dem versionierten Projektbestand eingebaut, niemals
beim Programmstart aus dem Internet geladen. Schlüssel, APK/XAPK, Standorte,
DBs, Aufnahmen und Logs sind keine Build-Eingaben. Das Source-ZIP verwendet
eine explizite Pfad-/Dateityp-Liste. Bibliotheksversionen und Lizenzdateien
werden mitgeliefert; vollständiges öffentliches Corresponding-Source-Kit ist
vor einer Veröffentlichung noch zu vervollständigen (siehe LICENSING.md).

Zeitlich begrenzte Startprüfung der EXE (kann lesende LAN-Verbindungen aufbauen):

```powershell
.\dist\2.3.0b3\SeestarStudio\SeestarStudio.exe --smoke-seconds 35 --qa-sky --capture-after 25 --capture reports/exe.png
```

`--qa-sky` verwendet einen ausdrücklich synthetischen Standort in einem isolierten QA-Profil unter reports,
nicht in den persönlichen Benutzereinstellungen. `--startup-diagnostics` schreibt
bei Importfehlern nur Typ/Importname/Stackorte in `reports/startup-error.json`.
Kein Geheimnisdump. Keine echte Steuerung in Tests.

Die Anleitung ist reproduzierbar mit fixierten Paketversionen; bitidentische
Binärdateien und ein sauberer Fremd-PC-Build sind noch nicht nachgewiesen.

## Benutzer-Installer

Nach build.ps1: Inno Setup 7.1.1 x64 vom offiziellen Hersteller installieren,
Downloadsignatur prüfen, anschließend build-installer.ps1 ausführen. Alternativ
`build-installer.ps1 -Compiler 'C:\Pfad\ISCC.exe'`. Lokaler Compiler liegt unter
.build-tools/innosetup, wird nicht mitgeliefert. Script: installer/SeestarStudio.iss.
Kein automatischer Download oder Installationsschritt im Buildskript.
Installer und portable EXE sind derzeit nicht digital signiert. Der Installer
benötigt keine Administratorrechte und startet die Anwendung nicht automatisch.

## V2.2: getrennte Ausgabe und Video

Ausgabe: `dist/<Version>/SeestarStudio`; ZIP/Installer enthalten die Version
im Namen. Das Buildskript lehnt das Ersetzen einer laufenden Zielversion ab.
Die alte V2.1-Ausgabe unter `dist/SeestarStudio` bleibt erhalten.
`build-installer.ps1` übergibt den passenden Versionsordner an Inno Setup.

Qt Multimedia wird über den PyInstaller-Hook eingebaut, einschließlich
FFmpeg-Mediaplugin und Decoder-DLLs. Sprachressourcen und qtbase_de.qm sind
Build-Eingaben. `python -m tools.verify_release` prüft ZIP, Quellen,
Sprachressourcen, FFmpeg-DLL und unerwünschte private Dateitypen.

Bei `--qa-sky --smoke-seconds N` nutzt die EXE ein eigenes QA-Profil und eine
eigene Instanzsperre. Dadurch bleibt eine laufende Benutzerinstanz unberührt.
Diese Prüfung kann echte lesende Geräteverbindungen aufbauen; sie ist keine
reine Offlineprüfung, sofern das Netzwerk erreichbar ist. Keine Steuerbefehle.

## Beta-Metadaten und Quellen

Version zentral in seestar_studio/__init__.py; pyproject liest sie dynamisch.
build.ps1 erzeugt UTC-Buildmetadaten, Quellhash und native PE-Version. Icon in
seestar_studio/assets; `python -m tools.build_icon` erzeugt die Rasterformate.
PyWinRT 3.2.1 mit allen Projektionen gemeinsam pinnen, nicht nur Runtime upgraden.

Nach dem Build erfasst tools.license_audit die eingebauten PE-Dateien. Das Paket
enthält App-Quellen, Iconmaster, Bauanleitung, Lizenzen und technische Manifeste.
Drittanbieterquellen werden separat lokal archiviert; abrufbar mit dem ausdrücklich
aufgerufenen Entwicklerwerkzeug tools.fetch_dependency_sources. Es lädt öffentliche
Quellen, führt sie nicht aus und wird weder beim Appstart noch beim Build automatisch
aufgerufen. Details/Weitergabeblocker: LICENSING.md.

`python -m tools.package_dependency_sources` erzeugt aus dem geprüften Manifest
das separate versionsbezogene Upstream-Quellen-ZIP; kein Netzabruf. Dieses Archiv
ersetzt die noch offene native Corresponding-Source-Zuordnung nicht.
`python -m tools.verify_icon_resources` vergleicht alle sieben eingebetteten
PE-Iconbilder von EXE/Installer mit der Original-ICO.

Lokale finale Testnachweise: docs/BETA_TEST_REPORT.md. Die ausgelieferte ZIP
enthält die zum Build passenden App-Quellen. Reproduzierbar sind die dokumentierten
Bauschritte; byteidentische Ergebnisse über andere Maschinen/Zeitpunkte hinweg
sind wegen Zeitstempeln und Toolchain noch nicht nachgewiesen.

## Getrennter Compliance-Prüfstand vom 8. November 2026

Die ursprünglichen b3-Pakete werden für Vergleiche aufbewahrt. Der ergänzende
Prüfstand mit dem erweiterten APK-Hinweis liegt ausschließlich lokal unter
`dist/compliance-review-2.3.0b3/SeestarStudio` und
`release/compliance-review-2.3.0b3`. Er ist kein freigegebener öffentlicher Release.
Die folgenden Befehle zeigen den tatsächlich verwendeten getrennten Ausgabeweg;
für einen weiteren Lauf neue Verzeichnisnamen wählen, um Belege zu erhalten.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m tools.build_metadata
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --distpath dist/compliance-review-2.3.0b3 --workpath build/compliance-review-2.3.0b3 SeestarStudio.spec
.\.venv\Scripts\python.exe -m tools.license_audit --target dist/compliance-review-2.3.0b3/SeestarStudio --output reports/compliance-followup/review-inventory.json --docs-output reports/compliance-followup/review-dependencies.md
.\.venv\Scripts\python.exe -m tools.package_release --target dist/compliance-review-2.3.0b3/SeestarStudio --release-dir release/compliance-review-2.3.0b3 --inventory reports/compliance-followup/review-inventory.json
.\build-installer.ps1 -SourceRoot dist/compliance-review-2.3.0b3/SeestarStudio -OutputDirectory release/compliance-review-2.3.0b3
.\.venv\Scripts\python.exe -m tools.verify_release --portable release/compliance-review-2.3.0b3/SeestarStudio-2.3.0b3-win64.zip --output reports/compliance-followup/review-package-check.json
```

`tools.package_source_supplement` archiviert die zusätzlich beschafften
Originalquellen, Rezepte, Lieferanten-SBOMs und Notices separat. Es prüft lokale
Hashes und überschreibt kein vorhandenes Archiv. Keine SDK-/Compilerdateien,
Referenz-Wheels oder Nutzer-APK werden darin mitgeliefert. Öffentliche Testschlüssel
in unveränderten Upstream-Quellarchiven sind keine privaten Nutzer-/ZWO-Schlüssel.

Der kontrollierte zlib-Neuaufbau ist ein gesonderter Funktionstest mit Community-
Compiler und offiziellen, nur lokal bereitgestellten SDK-Dateien; er ersetzt keine
Laufzeit-DLL und beweist keinen vollständigen Neuaufbau von Qt/FFmpeg.
Aktuelle Ergebnisse und Grenzen: [TECHNICAL_LICENSE_RESOLUTION.md](docs/TECHNICAL_LICENSE_RESOLUTION.md)
und [COMPLIANCE_REVIEW_TESTS.json](docs/compliance/COMPLIANCE_REVIEW_TESTS.json).
