# File Manager — Version 2, Phase 1

Neuer nativer Tab in derselben Anwendung. Automatische Verbindung zu den
Dateifreigaben dynamisch erkannter Teleskope. Der Liveviewer läuft unabhängig
weiter. Keine Dateischreib-, Lösch-, Umbenennungs- oder Bewegungsbefehle am Gerät.

## Bedienung
Gerät und Verzeichnis links auswählen; Ordner doppelklicken oder im Baum öffnen.
`MyWorks` enthält gespeicherte Beobachtungsordner, häufig nach Ziel benannt.
Die Tabelle zeigt Typ, Größe und lokalen Anzeigezeitpunkt (sofern vom Server
gemeldet). FITS-/RAW-Subframes werden anhand Dateityp/Ordnernamen gekennzeichnet.
Strg/Shift erlaubt Mehrfachauswahl; die Suche filtert Dateiname und Typ.

Zuerst einen lokalen Downloadordner auswählen. „Auswahl herunterladen“ unterstützt
Dateien und Ordner; „Ganzen Ordner herunterladen“ schließt Unterverzeichnisse ein.
Zielstruktur: `<gewählter Ordner>/<Modell_Serienkennung>/<Gerätepfad>`.
Keine erfundenen Aufnahmezeitpunkte: Zeitstempel werden nur aus den tatsächlichen
Dateimetadaten angezeigt, deshalb keine künstliche Datumsgruppierung.

Die Warteschlange zeigt Fortschritt, Restbytes, Geschwindigkeit und Dateianzahl.
Ein globaler Downloadworker begrenzt die Parallelität. Standardlimit 2 MiB/s;
1/5/10 MiB/s oder kein Limit explizit wählbar. Hohe Bandbreite kann den Live-
RAW-Transfer beeinträchtigen; während Aufnahmen ist das Standardlimit sinnvoll.

## Abbruch, Wiederaufnahme, Integrität
- Abbruch beendet zwischen 256-KiB-Blöcken bzw. nach Netzwerk-Timeout (8 s).
- Teiltransfers liegen ausschließlich lokal in `.studio-partials` unter dem
  ausgewählten Ziel. „Erneut starten / Fortsetzen“ prüft Identität, Größe,
  Änderungszeit und lokalen SHA256-Checkpoint, dann liest SMB ab dem Offset.
- Auch nach App-Neustart dieselbe Auswahl und denselben Zielordner verwenden:
  vorhandene passende Teiltransfers werden erkannt.
- Nach Abschluss werden Servergröße/-Änderungszeit nochmals geprüft. Eine sich
  während der Aufnahme ändernde Datei wird nicht als fertiger Download freigegeben.
- SHA256 ist ein **lokaler Integritätsnachweis**. Der SMB-Server liefert hier
  keinen Dateihash; End-to-End-Hashgleichheit kann daher nicht behauptet werden.
- Bereits heruntergeladene unveränderte Dateien werden anhand gespeichertem
  Nachweis plus lokalem Hash übersprungen. Andere vorhandene Dateien werden
  nicht überschrieben. Bei Konflikt anderen Zielordner wählen.
- Pfad-Traversal, Windows-Gerätenamen und unzulässige Zeichen werden behandelt;
  veränderte Namen erhalten einen deterministischen Suffix. Symlinks/Reparse-
  Points des Geräts werden nicht verfolgt.

## Vorschauen
JPEG/PNG-Auswahl lädt maximal 8 MiB mit begrenztem Tempo, verkleinert lokal auf
640 × 480 und hält maximal 150 erzeugte Cachebilder im Benutzerprofil vor.
Gleiche Dateien werden über Gerät/Pfad/Größe/Zeit wiedererkannt. Keine RAW-/FITS-
Downloads für Vorschaubilder. Lokale FITS-Vorschauen sind optional und derzeit
nicht implementiert; der Download der vollständigen FITS-Datei ist unterstützt.
Der private Cache gehört nicht in öffentliche Release-Artefakte.

## Technische Grundlage
`SeestarFileClient` verwendet dieselbe SMB-Gastanbindung und Freigabe wie
SeestarPy 0.8.0 (`EMMC Images`, TCP 445) mit der bereits installierten pysmb-
Bibliothek. Vollständige SMB-Listen vermeiden die unvollständigen RPC-Alben
und den globalen Dateiseiten-Cursor der Firmware. Die API ist pro Gerät gebunden
und stellt ausschließlich `list`, `stat`, `read` und `close` bereit.

Keine Authentifizierungsschlüssel erforderlich/kopiert für diese Dateifreigabe;
die vorhandene SeestarPy-Authentifizierung des Liveviewers bleibt unverändert.
Ein nicht erreichbares oder anders implementiertes Dateisystem wird als Fehler
angezeigt; es gibt keine Modellnamen-Sonderfälle oder behaupteten Fähigkeiten.
