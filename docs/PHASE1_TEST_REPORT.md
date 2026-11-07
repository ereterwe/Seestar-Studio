# Phase 1 — File Manager, 6. November 2026

## Echte Hardware
Nur S50 und S50 Pro wurden verwendet. Kein S30-/S30-Pro-Test.

`reports/files-hardware.json` protokolliert:
- S50: 35 Beobachtungsverzeichnisse, FITS/JPEG erkannt; ein vorhandenes JPEG
  mit 1.131.005 Bytes abgebrochen, ab Offset fortgesetzt, vollständig gespeichert
  und beim erneuten Aufruf ohne erneuten Transfer als Duplikat erkannt.
- S50 Pro: 7 Beobachtungsverzeichnisse zu diesem Zeitpunkt, FITS-Subframes/JPEG
  erkannt; entsprechender Test mit 2.829.593 Bytes erfolgreich.
- Beide echten Livebildstreams während desselben Testlaufs: S50 zwei verschiedene
  Frames, S50 Pro drei. Am Ende beide verbunden, ohne Bildfehler, Stacking gemeldet.
- SMB-Dateigröße entspricht jeweils exakt der lokalen Größe. Lokale SHA256-
  Nachweise vorhanden; kein serverseitiger Dateihash behauptet.
- Manager und Verbindungen wurden sauber geschlossen.

`reports/file-ui.json` und `reports/file-manager.png`: Dateiliste im integrierten
nativen Tab mit beiden echten Geräten. Inzwischen 8 Pro-Ordner (Gerätedaten sind
dynamisch). Während dieses separaten GUI-Laufs meldete das Pro zeitweise
`ContinuousExposure` statt `Stack` und lieferte beim Screenshot keinen Stack;
dieser Zustand wurde als fehlendes Bild angezeigt. Keine Betriebsart wurde durch
Studio geändert. Der vorangehende parallele Livebildtest ist separat belegt.

## Simulierte Tests
33 gesamte Tests bestanden: alle 16 Viewer-Regressionen plus File-Manager-
Tests für Traversal, Windows-Namen, nicht überschreibende Dateipublikation,
Duplikate, unterbrochene/korrupt gewordene Teiltransfers, Offset-Resume,
Dateiveränderungen, kurze Reads, leere Dateien, rekursive Mehrgeräte-Aufträge,
Shutdown, Preview-Cache, RAW-Preview-Vermeidung und native Dateiliste.

## Grenzen / ausstehende Tests
Keine Remote-Dateien geändert. Ganze große Sessions und viele gleichzeitige
Benutzeraufträge wurden simuliert, nicht als stundenlange reale Massendownloads
getestet. Echter DHCP-Wechsel, Abbruch durch Stromausfall, fremder Windows-PC
und lange WLAN-Stabilität bleiben offen. FITS-Vorschauen sind optional und nicht
implementiert; FITS-Downloads und Dateityperkennung sind vorhanden.
