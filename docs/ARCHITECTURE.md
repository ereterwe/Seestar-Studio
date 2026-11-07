# Architektur

```text
Qt GUI thread                         Background
─────────────                         ──────────
DashboardWindow ── commands ────────► TelescopeManager
  TelescopeCard ◄── latest mailbox ──   │ discovery/lifecycle executor
    ImageViewer                       ├─ TelescopeSession (serial A)
  SettingsService                     │    NativeMonitor : ScopeMonitor
                                      │      ├─ authenticated event/RPC thread
                                      │      └─ image thread → ImagePipeline
                                      └─ TelescopeSession (serial B, …)
                                           independent sockets/workers
```

## Verantwortlichkeiten

- **TelescopeManager:** entdeckt Geräte, koordiniert Start/Pause/Reconnect und
  DHCP-Wechsel. Ein Gerätelebenszyklus kann warten, während andere Sitzungen ihre
  Daten weiter veröffentlichen. Ein begrenzter Latest-Value-Speicher enthält je
  Seriennummer nur aktuelle Telemetrie und das letzte erfolgreiche QImage.
- **TelescopeSession:** pro Gerät getrennte Lebenszyklen, letzte gültige Anzeige
  bleibt über eine neu erzeugte Verbindung hinweg erhalten.
- **NativeMonitor:** versionierter SeestarPy-Adapter. Nutzt die Bibliothek für
  Protokoll und Statusmapping, schützt ausgehende RPCs und verwaltet Sockets.
- **ImagePipeline:** RAW/JPEG-Dekodierung und STF aus SeestarPy; QImage besitzt
  seine Pixeldaten unabhängig vom temporären NumPy-Array.
- **TelemetryService:** liefert ein einheitliches Modell, erhält fehlende Werte
  und kennzeichnet berechnete Integration. Geräteinformationen sind Plain Text.
- **DashboardWindow / TelescopeCard / ImageViewer:** ausschließlich Qt Widgets.
  QGraphicsView behält Transform und Bildmitte bei Framewechseln. Kein Netzwerk
  im GUI-Thread. PNG/JPEG-Export läuft ebenfalls in einem Hintergrundthread.
- **SettingsService:** atomare lokale Speicherung von Reihenfolge, Fenstergröße
  und Detailsicht. Keine Geräteadresse und keine Authentifizierungsdaten darin.

## Nebenläufigkeit und Speicher

SeestarPy wird erst im Manager-Thread importiert, weil dessen Import bereits
Discovery ausführt. Das Fenster erscheint unabhängig von Discovery-Timeouts.
Jedes Gerät besitzt einen Status- und einen Bildthread. Frames werden nicht als
unbegrenzte Qt-Signalwarteschlange versendet. Das GUI fragt nur lokale Referenzen
alle 500 ms ab; ohne neues ImageFrame-Objekt wird kein QPixmap erneuert.

Sockets sind beim Stop aktiv geschlossen; Wartepausen sind abbrechbare Events.
Qt bleibt beim Herunterfahren bedienfähig, während es auf das Ende der Worker
wartet. Lifecycle-Fehler und ungültige Telemetrie einer Sitzung werden isoliert.
Logs enthalten ausschließlich festgelegte Meldungen und Ausnahmeklassennamen.

## Version 2: getrennte Erweiterungen

- `files/`: lesender SMB-Adapter, atomare Downloads mit Resume/Hashprüfung,
  globale Downloadwarteschlange und begrenzter Vorschaucache.
- `sky/`: lizenzierter lokaler Katalog, reine Berechnungsfunktionen, expliziter
  Standort. Ein Worker für Katalog/Berechnungen; veraltete Ergebnisse verworfen.
- `control.py`: optionaler ControlService. Absicht → konkrete Bestätigung →
  einmaliger Befehl je Gerät. Separate SeestarPy-Verbindung, gleiche vorhandene
  Authentifizierung, Serienprüfung auf der Verbindung, kein Mutation-Retry.
  Viewer-Allowlist unverändert. Unbekannte Voraussetzungen sperren Aktionen.
- `planner.py`: reine lokale Planung/Persistenz ohne Steuerungsadapter.
  Worker für Sichtbarkeit/Optimierung; gemeinsame Qt-Timeline.
- `history.py`: begrenzte Schreibqueue, eigener SQLite-Thread, separate lesende
  Abfragen. Whitelist für gespeicherte Telemetrie, keine Bilder/Standorte/Schlüssel.
  Native Kurven mit begrenzter Punktzahl; unbekannte Intervalle separat.

Alle Komponenten werden beim Fensterschließen asynchron angehalten. V2.1
ergänzt Einrichtung/Portabilität/Capabilities; V3 Veröffentlichungsvorbereitung.
V2.1-/V3-Funktionen wurden nicht vorgezogen.

## Grenzen

Der Adapter verwendet einige interne SeestarPy-Methoden. Die Version ist fixiert;
ein Bibliotheksupgrade ist eine gezielt zu testende Änderung. RAW-STF in voller
Auflösung braucht vorübergehend deutlich mehr Speicher als das 720-Pixel-Web-
Dashboard. Es gibt keine GPU-Abhängigkeit. Der Viewer exportiert 8-Bit-
Anzeigebilder; der File Manager lädt vorhandene RAW/FITS-Dateien unverändert.
OBS-Steuerung, Firmwareänderungen und ein Installer gehören nicht zu V2.
