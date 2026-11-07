# Testbericht — 5. November 2026

## Tatsächlich an Hardware getestet

Zwei automatisch entdeckte Teleskope, Firmware 9.75:

- S50 Pro, NGC 7000.
- S50, M31.

**90-Sekunden-Kerntest:** beide authentifiziert, beide echte RAW-Stacks in
2160 × 3840 Pixeln. Sechs unterschiedliche Pro-Frames, zwei S50-Frames.
Beide meldeten weiter `working / Stack`. S50 meldete zwischendurch einen
Bildverbindungsfehler; das letzte Bild blieb erhalten.

**150-Sekunden-Reconnect-Test:** nach Empfang beider Bilder wurde ausschließlich
die Studio-Sitzung eines Geräts getrennt, nach zwölf Sekunden wieder verbunden.
Neue Bilder nach Reconnect wurden beobachtet (etwa sechs Sekunden nach dem
Verbinden); das zweite Gerät lieferte weiter Stacks. Insgesamt wurden zehn
unterschiedliche Pro-Frames und vier S50-Frames erfasst. Beide Sitzungen wurden am Testende sauber geschlossen. Die korrigierte
Koordinatenübernahme liefert auch Höhe und Azimut.

**Native Oberfläche:** Qt-Renderaufnahme mit beiden echten Bildern und passender
Telemetrie geprüft. Kein automatisch abgeschnittener Bildrand, zwei gleichwertige
Karten, eindeutig als RAW-Stack beschriftet. Die externe Windows-Capture-API
lieferte zweimal einen Timeout; die Prüfung erfolgte deshalb zusätzlich über
`QWidget.grab()` innerhalb der real laufenden Anwendung.

Maschinenlesbare Nachweise (lokal, nicht im Quellarchiv veröffentlicht):

- `reports/hardware.json`
- `reports/hardware-reconnect.json`
- `reports/native-dashboard.png`
- Finaler EXE-Prüflauf: `reports/exe-dashboard.png` und `.json` (nach Build).

## Automatisierte Tests — simuliert, keine Hardwaretests

16 Tests in `tests/`, erfolgreich:

- Schreib-/Steuerbefehle werden vor dem Versand blockiert.
- RAW-Dekodierung/STF, JPEG ohne zweiten Stretch, Bayer-Preview.
- Gleiche Frames werden nicht neu dekodiert; korrupte Frames ersetzen kein Bild.
- Empfangsbudget, Zeitgrenze und Stop brechen fehlerhafte Transfers ab.
- Statusreconnect nach simuliertem Verbindungsfehler.
- Blockierendes `recv` wird beim Stop per Socket-Schließen beendet.
- Neuere Statuspolls ersetzen alte Events; Listenkoordinaten werden übernommen.
- Unbekannte Telemetrie bleibt unbekannt; null verworfene Frames sind korrekt.
- Mehrere Sitzungen, ein defektes Gerät, Pause/Resume, DHCP-Wechsel, Shutdown.
- Zoom und Bildposition bleiben bei Framewechsel erhalten.
- Raster, Reihenfolge, Maximieren, Rückkehr und Einstellungen.
- Veraltete Bilder bleiben sichtbar und markiert.
- PNG-Export und Wiederherstellung beschädigter Einstellungsdateien.

## Windows-Paketprüfung

Der erste EXE-Start deckte eine fremde `icuuc.dll` aus einem Poppler-Verzeichnis
im Entwicklungs-PATH auf. Deren ICU-ABI passte nicht zu Qt. Der Build isoliert
seine DLL-Suche jetzt auf die eigene Python-/Qt-Umgebung und Windows. Die
System-ICU wird nicht durch die fremde Bibliothek im Paket überschattet.
Dieser Fehler wurde im tatsächlichen EXE-Lauf gefunden, nicht durch Unit-Tests.

Der korrigierte **eigenständige EXE-Build** wurde anschließend 70 Sekunden mit
beiden realen Teleskopen ausgeführt. Bei der Aufnahme nach 55 Sekunden:
`frozen_executable=true`, Fenstergröße **1920 × 1080**, beide verbunden,
beide Bilder RAW 16-bit / 2160 × 3840, Framefolge S50 = 2 und Pro = 3,
keine Bildfehler. Das Programm beendete sich anschließend regulär (Exitcode 0).
Der Teststart erfolgte aus dem Build-Ordner, ohne Python-Startskript und ohne
eine kopierte Authentifizierungsdatei.

## Akzeptanzkriterien

| Kriterium | Ergebnis |
|---|---|
| Native Windows-Oberfläche startet | real gestartet |
| Beide Geräte automatisch gefunden | real bestätigt |
| Beide Stacks nebeneinander | real bestätigt, Qt-Aufnahme |
| Unabhängige Live-Aktualisierung | real bestätigt |
| Verfügbare Telemetrie | real bestätigt; unbekannte Werte `—` |
| Aufnahmen bleiben aktiv | Stacking vor und nach dem Test bestätigt, steigende Framezähler; nur geprüfte Lese-/Auth-/Bildmethoden |
| Individuelles Trennen/Wiederverbinden | real bestätigt |
| Geräteausfall isoliert | simuliert geprüft; kein absichtliches Ausschalten realer Geräte |
| Zoom/Maximieren | Qt-Funktionstests bestanden |
| Windows-EXE baubar | PyInstaller-Build erfolgreich; separater EXE-Lauf dokumentiert |

## Noch ausstehend

- Mehrstündiger Dauerlauf und systematische CPU/RAM-Messung über Stunden.
- Reales Ausschalten/Netzverlust eines Teleskops, Wiedererscheinen nach längerer
  Unterbrechung und realer DHCP-Adresswechsel.
- Interaktive Parallelbedienung der Android-App während der Studio-Nutzung.
- JPEG-Transfer an realer Hardware: beide Geräte lieferten Raw. Der Modus wurde
  bewusst nicht verändert; JPEG ist über synthetische Fixtures geprüft.
- Drei oder mehr reale Geräte (Raster mit drei Geräten simuliert getestet).
- OBS-Fensteraufnahme und gesonderter Test auf Windows 11; der vorhandene
  Entwicklungsrechner meldet Windows 10 Build 19045.

Es wurden keine langen Stabilitäts- oder Android-Tests als bestanden ausgegeben,
die nicht tatsächlich durchgeführt wurden.
