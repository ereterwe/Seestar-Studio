# Technische Lizenzklärung — Ergänzung zu 2.3.0b3

Stand 8. November 2026. Diese Ergänzung bewertet den unveränderten ursprünglichen
b3-Binärbestand und neu beschaffte Nachweise. Sie erklärt keine endgültige
Rechtssicherheit. Ein Prüfstatus bezieht sich immer auf die bezeichnete Aussage.

## Selbständig erledigte Punkte

| Aussage | Nachweis / Ergebnis |
|---|---|
| Originalherkunft der übernommenen Binärdateien | Alle 27 Python-Dateien stimmen mit dem offiziellen Python-3.12.10-Embeddable-Paket überein. Die Dateien aus 15 weiteren Paketen stimmen mit den Original-Wheels überein; deren gesamte Archiv-SHA256 wurde gegen PyPI geprüft. |
| Quellen und Rezepte beschafft | 105 ausgewählte Quellarchive sind lokal erfasst und auf ihren dokumentierten SHA256 geprüft. Ein lokal berechneter Hash wird nicht als unabhängige Herausgebersignatur bezeichnet. |
| CPython-Abhängigkeiten | Vollständige CPython-3.12.10-Quellen, Windows-Projektskripte und die darin gepinnten source-deps für bzip2, xz, libffi, SQLite, OpenSSL und zlib vorhanden; Git-Revisionen stehen in den Archiven. |
| cryptography / OpenSSL / Rust | Originale Hersteller-Stücklisten identifizieren OpenSSL 4.0.3 und Rust-Komponenten. Die registrierten Cargo-Archive wurden anhand der Cargo.lock-Prüfsummen beschafft; lokale Crates liegen im cryptography-Quellarchiv. OpenSSL 3.0.16 aus CPython bleibt separat zugeordnet. |
| Pillow | Hersteller-SBOM gegen tatsächlich ausgelieferte Erweiterungen und Laufzeitmerkmale abgegrenzt. Kein irrtümlicher Nachweis von optionalem libimagequant, libxcb oder nicht ausgeliefertem FreeType. Windows-Buildskript, Patches und aktive Codecquellen vorhanden. |
| Astronomie / Expat | ERFA-Laufzeit 2.0.1 und SOFA 20231011 identifiziert. CPython verwendet Expat 2.7.1; Astropys separater vendorter Expat-Quellheader deklariert 2.7.3. Der tatsächlich benötigte CFITSIO-Kompressionsquellensatz samt Lizenz ist in Astropy enthalten. Keine unbelegte Zuordnung eines vollständigen CFITSIO-Pakets. |
| AVIF | dav1d 1.5.3 als Decoder und AOM 3.14.1 als Encoder identifiziert; beide Quellen und der gepinnte libyuv-Commit beschafft. |
| NumPy / BLAS | Originales openblas-libs-Rezept für 0.3.34.106.0 samt Windows-Patch gefunden; es pinnt OpenBLAS auf 446c436e10450c348169808f1a6b3fae0925c9f7. Quellen beschafft. Compiler-Runtime-Bestandteile bleiben einzeln zu prüfen. |
| FFmpeg | Öffentliches Qt-6.12.0-Windows-Rezept und Konfiguration gefunden. Das offizielle FFmpeg-9.0.1-Quellarchiv stimmt mit der im Qt-Rezept genannten SHA1 überein; SHA256 zusätzlich erfasst. |
| zlib-Eingang für FFmpeg | Qt-Rezept pinnt 1.3.1 und beschreibt zwei Änderungen: Entfernen des unistd.h-Includes und der festen Linker-Basisadresse. Passende Quellen und Patchanweisungen vorhanden. Isolierter Neuaufbau mit Funktionstest erfolgreich (Build/Test jeweils Exit 0). |
| Mesa / LLVM | Qt-Originalpaket anhand der veröffentlichten Rezept-Prüfsumme verifiziert. Alle PE-Programmsektionen entsprechen der b3-DLL; vollständige Dateihashes unterscheiden sich. Mesa 11.2.2 und LLVM 3.6.2 identifiziert und Quellen beschafft. Keine Gleichheit der Signaturen behauptet. |
| Lizenz-/Copyright-Sammlung | Originaltexte einschließlich neuer Quellen und Rust-Abhängigkeiten gesammelt. Colorama-Lücke und Vendor-Dateikollisionen bereits in b3 behoben. Neue Ergänzungen werden getrennt archiviert. |
| Microsoft-Projektvoraussetzungen | Stabile Community-2026-Installation und öffentliche GPL-Projektlizenz dokumentiert. Die Community-Bedingungen bieten hierfür einen kostenlosen Entwicklungsweg; eine kostenpflichtige Professional-/Enterprise-Lizenz ist als Voraussetzung nicht nachgewiesen. |
| APK-Hinweis | Deutsche/englische Benutzerinformation ergänzt: Selbstbeschaffung, keine APK/Schlüssel-Mitlieferung, lokale Verarbeitung, Verantwortung für ausgewählte Datei, Haftung nur im gesetzlich zulässigen Umfang. |

Die Lieferanten-SBOMs sind zusätzliche Belege, keine automatische Liste ausschließlich
unter Windows gelinkter Bestandteile. Die Rohrezepte liegen in den zugeordneten
Originalarchiven; `tools.resolve_native_sources` erfasst ihre Pfade und Hashes.
Die Quellen können umfangreicher sein als der tatsächliche Binärumfang.

## Noch nicht allein durch die vorliegenden Nachweise geschlossen

**Qt/PySide/Mesa:** Versionsgleiche Originalarchive und passende Binärdateien
belegen nicht jeden effektiven Buildschalter oder einen unbekannten Herstellerpatch.
Das Mesa-Paket enthält nur die DLL. Ein vollständiger produzierender Patch-/Buildsatz
für genau diesen alten Renderer ist damit nicht belegt. Dafür benötigt man
zusätzliche Herstelleraufzeichnungen oder einen eigenständig erstellten und
vollständig geprüften Ersatzbuild. Ein Austausch durch ein nicht gleichwertig
getestetes Paket würde die bewährte Anwendung gefährden und wird nicht als
erledigte Lizenzklärung ausgegeben.

**Native Gesamt-Reproduktion:** Ein einzelner erfolgreicher zlib-Build ist kein
Neuaufbau aller Qt-/FFmpeg-/Rust-/BLAS-Binärdateien. Bei OpenSSL-Artefakten verweist
die Hersteller-CI auf zusätzliche pyca/infra-Artefakte. Exakte historische CI-
Eingänge/Featureflags und verbleibende Compiler-Runtime-Zuordnungen brauchen weitere
Belege. Ein bitidentischer Gesamtbuild wird nicht pauschal als Lizenzpflicht behauptet.

Die Pflichten sind komponentenbezogen: GPL-/LGPL-Corresponding-Source und
Austauschbarkeit sind von bloßer Reproduzierbarkeitsqualität zu unterscheiden.
Bei permissiv lizenzierten Mesa-/LLVM-Komponenten ist ein unbekanntes historisches
Builddetail für sich allein keine nachgewiesene Pflicht zur Quelloffenlegung.
Es bleibt eine Genauigkeitslücke im Herkunftsbericht; Notices, eingebettete Teile
und die Gesamtintegration sind trotzdem zu prüfen. Der konservative Sammelstatus
des Auditwerkzeugs ersetzt diese Einzelbewertung nicht.

**Microsoft:** Kostenlose Community-Eignung ersetzt nicht die Prüfung der
Weitergabebedingungen konkreter älterer DLLs, Schutzbedingungen für nachgelagerte
Empfänger und der begründeten GPL-Systembibliotheksausnahme. Siehe
[MICROSOFT_RUNTIME_REVIEW.md](MICROSOFT_RUNTIME_REVIEW.md).

**Rechtsbewertung:** Patente, ZWO-Interoperabilität und Marken werden durch
Quellcodebeschaffung oder Disclaimer nicht rechtlich entschieden. Die Fakten und
konkreten Fragen stehen in den nachfolgenden Unterlagen. Kein Schlüssel, keine
APK und kein privates Nutzungsdatum werden für diese Prüfung benötigt.

## Übergabepaket

- [Codec-Fakten und Bedingungen](CODEC_LEGAL_REVIEW.md)
- [Microsoft-Runtime-Prüfung](MICROSOFT_RUNTIME_REVIEW.md)
- [ZWO-Interoperabilität](ZWO_INTEROPERABILITY_REVIEW.md)
- [Offene Rechtsfragen zur gezielten Prüfung](LEGAL_REVIEW_QUESTIONS.md)
- Maschinenbelege: `docs/compliance/NATIVE_SOURCE_RESOLUTION.json`,
  `PUBLISHER_WHEEL_VERIFICATION.json`, `CPYTHON_PUBLISHER_REFERENCE.json`,
  `CONTROLLED_ZLIB_BUILD.json`, `CODEC_REGISTRY.json`.

Die ursprünglichen b3-Archive bleiben erhalten. Ergänzende Quellen/Notices und
die überarbeitete Benutzerinformation werden als gesonderter lokaler Prüfstand
vorbereitet. Öffentliches Hochladen von Binärdateien erfolgt erst, wenn die
bezeichneten technischen und rechtlichen Freigabepunkte tatsächlich geklärt sind.

## Abschließende lokale Prüfung dieser Ergänzung

169 automatisierte Tests bestanden. Der getrennte portable Prüfstand und dessen
installierte EXE starten und beenden sich sauber. Installation, erneute Installation
und Deinstallation: jeweils Exit 0; alle 1.642 installierten Dateien entsprechen
dem ausgewählten Prüfstand. Persönliche Einstellungen blieben unverändert.
Die ZIP-Prüfung meldet keine verbotenen Dateien. Details und Grenzen stehen in
[COMPLIANCE_REVIEW_TESTS.json](compliance/COMPLIANCE_REVIEW_TESTS.json).
Dies sind lokale Software-/Installerprüfungen, keine neuen Hardwaretests und kein
Test eines fremden Windows-PCs. Der letzte Funktionstest der Benutzerinformation
verwendet ausschließlich kurzlebige synthetische Schlüssel.

Die ergänzten Abschlussnachweise werden außerhalb des unveränderten geprüften
Installer-Payloads dokumentiert. Aktuellere Dokumente im Repository sind daher
nicht automatisch identisch mit dem Dokumentationssnapshot im bereits gebauten ZIP.
