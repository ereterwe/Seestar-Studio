# Originales Telescope-Desk-Icon

Eigenständige geometrische Observatoriumskuppel mit Stern in Dunkelblau,
Anthrazit und Türkis. Kein übernommenes Markenlogo, keine fremden Grafiken,
keine Fonts. Entwurf als SVG mit Codex-Unterstützung nach Marks Gestaltungsauftrag;
kein generativer Bilddienst. Lizenz: GPL-3.0-only, telescope_desk/assets/ICON-LICENSE.txt.

Master: telescope_desk/assets/TelescopeDesk.svg. PNG: 1024×1024. ICO:
16/24/32/48/64/128/256 Pixel, transparente Außenbereiche und Antialiasing.
Reproduzierbare Erzeugung: `python -m tools.build_icon` (Qt SVG, Pillow).

QApplication/QDialog verwenden dasselbe Icon. Windows-App-ID:
TelescopeDesk.Desktop. EXE und Installer erhalten das ICO als native Ressource;
Startmenü/Desktop referenzieren die EXE samt AppUserModelID. UninstallDisplayIcon
zeigt ebenfalls auf die installierte EXE. Kein zusätzlicher Splashscreen.

QA: Größen/Alpha/Konturen automatisiert, native Dialoge visuell. Die finale
Explorer-/Taskleisten-/Installationsprüfung wird in BETA_RELEASE_CHECKLIST.md
festgehalten. Windows kann alte Symbole zwischenspeichern; zuerst den neuen
Versionspfad prüfen, keinen globalen Icon-Cache ungefragt löschen.
