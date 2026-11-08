# Lizenzprüfung — Stand 8. November 2026

Projektlizenz: **GPL-3.0-only** (`LICENSE`). Das Repository ist öffentlich;
b3 wurde lokal gebaut, geprüft und sein Quellcode veröffentlicht. Die ursprünglichen
b3-Binärdateien bleiben erhalten. Aktuell werden technische Nachweise und eine
überarbeitete APK-Benutzerinformation als getrennter Prüfstand vorbereitet.

[Technische Klärung](docs/TECHNICAL_LICENSE_RESOLUTION.md),
[Codec-Fakten](docs/CODEC_LEGAL_REVIEW.md),
[Microsoft-Prüfung](docs/MICROSOFT_RUNTIME_REVIEW.md),
[ZWO/SeestarPy-Position](docs/ZWO_INTEROPERABILITY_REVIEW.md) und
[gezielte Rechtsfragen](docs/LEGAL_REVIEW_QUESTIONS.md) bilden den aktuellen Stand.

Die Originalherkunft aller 129 übernommenen nativen b3-Dateien wurde gegen die
Herstellerpakete geprüft. Erweiterte Quellarchive, Cargo-Abhängigkeiten, originale
Buildrezepte/Patches und Lieferanten-SBOMs wurden beschafft. Ein kontrollierter
zlib-Neuaufbau mit Funktionstest besteht. Die Zuordnung bestimmter ursprünglicher
Qt/Mesa/CI-Builddetails und rechtliche Freigaben bleiben offen; Quellenbeschaffung
allein ist keine vollständige Freigabe der Binärweitergabe. Keine kostenpflichtige
Microsoft-Entwicklerlizenz ist für dieses öffentliche GPL-Projekt als zwingende
Voraussetzung nachgewiesen; die Bedingungen der vorhandenen kostenlosen Community-
Route und konkreter Runtime-Weitergabe sind dennoch zu beachten.

Öffentliche neue Binärdownloads erfolgen entsprechend dem Auftrag erst nach
Klärung der dokumentierten Punkte. GPL-Rechte bleiben unberührt. Die folgenden
Abschnitte sind historische Prüfschritte; ältere Checklisten zeigen nicht den
heutigen Erledigungsstand.

## Historischer Erstcheck der tatsächlich installierten Komponenten

| Komponente | Version | Lizenz / Prüfstand |
|---|---|---|
| SeestarPy | 0.8.0 | GPLv3 laut lokaler METADATA und vollständiger LICENSE |
| PySide6 / Qt / Shiboken | 6.12.0 | LGPL-3.0 / GPL-2.0 / GPL-3.0-Optionen laut Paketmetadaten; mitgelieferte Qt-Module einzeln vor Release prüfen |
| NumPy | 2.5.4 | BSD-3-Clause, 0BSD, MIT, Zlib, CC0-1.0; verschachtelte Drittanbietertexte erhalten |
| Pillow | 13.0.0 | MIT-CMU laut Metadaten; native Codec-Abhängigkeiten separat prüfen |
| PyInstaller | 6.22.3 | GPL mit Bootloader-Ausnahme; Laufzeithinweise erhalten |
| pysmb | 1.2.15 | zlib/libpng-Lizenz laut Paket; bereits SeestarPy-Abhängigkeit |
| cryptography | 50.0.2 | Apache-2.0 / BSD; eingebettetes OpenSSL beachten |
| requests | 2.34.2 | Apache-2.0 |
| cffi / pycparser / pyasn1 | siehe requirements-lock.txt | MIT-0 / BSD; lokale Lizenztexte gesammelt |
| SQLite / sqlite3 | Python-/Systemlaufzeit | SQLite public domain; Python PSF-Lizenz erhalten |
| Astropy / IERS-Daten | 8.0.2 / 0.2026.11.2.0.34.55 | BSD-3-Clause; vollständige Paketnotices mitgeliefert |
| PyERFA / PyYAML | 2.0.1.5 / 6.0.3 | BSD-3-Clause einschließlich ERFA/SOFA-Hinweisen / MIT |
| OpenNGC | Snapshot be3cd6c5… | CC BY-SA 4.0; Originaldaten, Attribution und Quellenmanifest mitgeliefert |
| Icons / Bilder | keine externen Produktgrafiken eingebunden | eigene UI; private Hardwareaufnahmen gehören nicht in öffentliche Quellen |

Weitere Abhängigkeiten und exakte Versionen: `requirements-lock.txt`,
Build-Inventar `dependency-versions.json`. Der bestehende Packager sammelt
Lizenzdateien mit ihrer Verzeichnisstruktur, um gleichnamige Notices nicht
zu überschreiben. Qt-Lizenztexte werden zusätzlich beigelegt, weil die lokalen
Wheels nicht alle Open-Source-Texte mitliefern.

## Übernommener Code und Weitergabe
SeestarPy bleibt unverändert installiert. `backend.py` erweitert ScopeMonitor,
nutzt dessen Status-/Streamlogik und ergänzt Lebenszyklus/Read-only-Schutz.
Der File-Manager verwendet die von SeestarPy dokumentierte SMB-Anbindung und
die bereits vorhandene pysmb-Bibliothek, ohne ein neues SMB-Protokoll zu bauen.

GPLv3: Bei Binärweitergabe passende vollständige korrespondierende Quellen
einschließlich Buildskripten und Änderungen anbieten; Copyright/Lizenztexte
erhalten. Das derzeitige Quellarchiv enthält die Anwendung und verwendete
SeestarPy-Quellen, ist aber **noch kein vollständiges öffentliches Source-Kit
aller gebündelten nativen Drittbibliotheken**.

LGPLv3: Dynamisches Qt-Linking und Bibliotheksaustausch ermöglichen, erforderliche
Notices/Texte und Bibliotheksquellen bereitstellen; Änderungen und gegebenenfalls
Installations-/Relinkinginformationen dokumentieren. Aktuell kein technischer
Schutz gegen DLL-Ersatz. Die konkrete Distribution muss vor Release geprüft werden.

## ZWO-Komponenten / Authentifizierung
Die lokale SeestarPy-Implementierung beschreibt einen gemeinsamen, nicht pro
Seriennummer oder Benutzerkonto abgeleiteten Signaturschlüssel. Der Handshake
signiert eine Challenge; eine Seriennummer ist kein Eingabeparameter der
Signatur. Das stützt die Annahme für diesen Implementierungsstand, ist keine
Garantie für alle Firmwareversionen. Der Schlüssel selbst wurde nicht gelesen.

Kein Schlüssel und keine APK/XAPK werden mitgeliefert. Bestehende lokale
Authentifizierung bleibt unverändert. Der Setup-Assistent gehört zu Version 2.1.
Zulässigkeit von APK/XAPK-Extraktion, Reverse Engineering, Nutzungsbedingungen,
Weitergabe und Markenverwendung bleibt **rechtlich offen** und ist vor einer
öffentlichen Freigabe zu prüfen. Keine definitive Rechtssicherheit behaupten.

## Historische offene Release-Prüfpunkte
- [ ] Vollständige direkte/transitive/native Dependency- und Lizenzliste.
- [ ] Katalogdaten und astronomische Berechnungsbibliotheken lizenzieren/zuordnen.
- [ ] Vollständiges versionsgenaues Source-Kit und reproduzierbarer Fremd-PC-Build.
- [ ] Qt-/Codec-/OpenSSL-/MSVC-Laufzeitweitergabe und Copyrights prüfen.
- [ ] Rechtliche Prüfung der lokalen Extraktionsverfahren und ZWO-Bezeichnungen.
- [ ] Quellen, Archive und eventuelle Git-Historie auf Geheimnisse, Standorte,
  Bilder, Sessiondaten, Logs und nicht freigegebene Binärdateien prüfen.
- [ ] README, CONTRIBUTING, CHANGELOG, BUILDING, INSTALLATION vervollständigen.
- [ ] Ausdrückliche Benutzerfreigabe vor jeder Veröffentlichung/Weitergabe.

Referenzen: https://www.gnu.org/licenses/gpl-3.0.html,
https://www.qt.io/development/open-source-lgpl-obligations,
https://github.com/astronomyk/seestarpy.
## Ergänzung Phase 2: lokale Astronomie

Astropy 8.0.2 und astropy-iers-data 0.2026.11.2.0.34.55: BSD-3-Clause;
pyerfa 2.0.1.5: BSD-3-Clause mit ERFA/SOFA-Hinweisen; PyYAML 6.0.3: MIT.
Lizenzdateien werden vom Paketbestand übernommen. OpenNGC-Snapshot
be3cd6c5498806a2fbb2f7e0452ef802dbb02be0: CC BY-SA 4.0 (Datenwerk getrennt
vom GPL-Programm). Unveränderte Daten, Originalhinweise, Quellen und Lizenz
liegen in `seestar_studio/catalog_data/`; siehe `docs/SKY_EXPLORER.md`.
Keine fremden Objektbilder oder geschützten Prosatexte eingebaut.
Vor Veröffentlichung bleiben vollständige Lizenz-/Quellenprüfung und Prüfung
der Katalog-ShareAlike-Pflichten erforderlich.


## V2.1: Einrichtung und Installer

Lokaler Assistent implementiert; Importtests ausschließlich mit synthetischen
RSA-Schlüsseln. Keine Aussage zur rechtlichen Freigabe echter APK-Auswertung.
Inno Setup 7.1.1 (Buildwerkzeug/Installer-Laufzeit): eigene permissive Lizenz,
Copyright Jordan Russell 1997–2026 und Martijn Laan 2000–2026. Originaltext
in third_party_licenses/INNO-SETUP-LICENSE.txt, Hinweise unverändert erhalten.
Quelle: https://jrsoftware.org/files/is/license.txt und https://jrsoftware.org/isdl.php.
Offizieller Compiler-Download vor lokalem Einsatz signaturgeprüft (Pyrsys B.V.).
Keine bekannte Unvereinbarkeit aus diesem ersten Check; vollständiges Inventar
aller nativen Laufzeiten und Corresponding Source bleibt ein V3-Prüfpunkt.

## V2.2: Video / Qt Multimedia

Keine neue Python-Videobibliothek. Vorhandenes PySide6_Addons / Qt Multimedia
6.12.0 wird jetzt genutzt. QMediaPlayer/QVideoSink verwenden eigene Decoder-Threads;
Qt-FFmpeg-Windows-Bibliotheken werden dynamisch gebündelt. Lokales avcodec-63.dll
meldet FFmpeg 9.0.1, LGPL 2.1 oder später; Buildkonfiguration ohne enable-gpl
oder enable-nonfree, mit shared und ohne static. Nachweis reports/video-codec-build.json.
Original-LGPL-2.1-Text und FFMPEG-NOTICE.txt hinzugefügt. PySide6_Addons-Lizenzen
werden zusätzlich aus dem installierten Paket übernommen.

Keine pauschale rechtliche Freigabe: vor Weitergabe weiterhin exakte FFmpeg-/Qt-
Quellen und Buildrezepte, transitive Copyrights, Austauschbarkeit sowie mögliche
Codec-Patentpflichten prüfen. Offizielle Referenzen:
https://doc.qt.io/qt-6/qtmultimedia-index.html
https://doc.qt.io/qt-6/qplaybackoptions.html
https://raw.githubusercontent.com/FFmpeg/FFmpeg/n9.0.1/COPYING.LGPLv2.1

## Final Beta Preparation — 7. November 2026

Technisches Vollinventar der 44 installierten Pakete: docs/DEPENDENCIES.md.
Das Build-Inventar dependency-inventory.json erfasst zusätzlich sämtliche
gebündelten DLL/PYD/EXE-Dateien mit SHA256, Imports und Versionsressourcen.
Die Umgebungsliste enthält auch Entwicklungswerkzeuge und ist nicht identisch
mit der tatsächlich gebündelten Untermenge.

Neu: PyWinRT-Runtime und drei Projektionen 3.2.1 (MIT), typing_extensions 4.16.0
(PSF-2.0). Lizenztexte werden mit ihrer ursprünglichen Struktur erhalten.
Eigenes Icon als SVG/PNG/ICO: GPL-3.0-only, Herkunft unter docs/ICON.md.

39 unverändert heruntergeladene Quellenarchive decken die ausgewählten
Python-Komponenten und die verwendeten Qt-Modulfamilien ab. PySide6/Addons/
Essentials/Shiboken besitzen kein PyPI-sdist, sind aber durch das offizielle
pyside-setup-6.12.0-Archiv abgedeckt. Manifest: docs/DEPENDENCY_SOURCES.json,
Prüfsummen und bestätigte Herausgeber-Digests soweit verfügbar. Separate lokale
Drittanbieter-Quellen-ZIP. Kein Download beim Programmstart oder normalen Build.
204 zusätzliche originale Lizenz-/Notice-Dateien aus diesen Archiven und
98 Qt-Attributionsmanifeste wurden aufgenommen. Originalpfade/Hashes im Index.
Diese Sammlung ist teilweise bewusst umfangreicher als der Binärumfang.

Qt Virtual Keyboard ist unter der GPLv3-Option zu berücksichtigen, nicht
pauschal als LGPL-Modul bezeichnen. Für das GPL-3.0-only-Gesamtprojekt ergibt
sich daraus im technischen Erstcheck kein unmittelbarer Lizenzwiderspruch.
Vollständige Modul-/Drittanbieterzuordnung und konkrete Weitergabe bleiben zu prüfen.

Weitergabeblocker: genaue native Source-/Patch-/Buildoption-Zuordnung,
statisch eingebettete Unterbibliotheken (z. B. OpenSSL/Rust/Mesa/Codecs),
Microsoft-Laufzeitbedingungen, Codecpatente und rechtliche Zulässigkeit lokaler
APK/XAPK-Extraktion nicht abschließend geklärt. Upstream-Quellen allein sind
keine garantierte vollständige Corresponding Source. Auch ein geschlossener
Betatest ist Weitergabe; keine gesetzeskonforme Freigabe pauschal behauptet.

Primärquellen zur Prüfung:
https://www.gnu.org/licenses/gpl-faq.en.html#UnchangedJustBinary
https://www.ffmpeg.org/legal.html
https://doc.qt.io/qt-6/licensing.html
https://doc.qt.io/qt-6/qtvirtualkeyboard-index.html
https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.12.0-src/
https://download.qt.io/official_releases/qt/6.12/6.12.0/submodules/
# Ergänzung 2.3.0b2 — 7. November 2026

Keine neue Abhängigkeit oder fremde Grafik. Sonnenpositionen verwenden die
bereits inventarisierte Astropy 8.0.2 (BSD-3-Clause) mit vorhandenen ERFA/IERS-
Komponenten. Windows-Link verwendet vorhandenes Qt/PySide6 und einen offiziellen
Windows-URI. Original-Icon, Credits und sämtliche Lizenztexte bleiben erhalten.
Numerische USNO-Testreferenzen sind mit Quelle dokumentiert, keine übernommene
Programmbibliothek. Vorhandene native Quellen-/Lizenz- und Weitergabeblocker
bleiben durch dieses UX-Update unverändert offen.

