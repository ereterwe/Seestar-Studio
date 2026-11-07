# Phase A — SeestarPy-Prüfung, 5. November 2026

## Lokaler Referenzstand

Python 3.12.10, SeestarPy **0.8.0**, NumPy 2.5.4, Pillow 13.0.0.
Das Projekt enthielt anfangs ausschließlich die funktionierende `.venv`.
Der installierte Code wurde unmittelbar untersucht. Die verlinkte Online-
Dokumentation bezeichnet sich zum Prüfzeitpunkt teilweise als 0.7.1; für den
Adapter ist deshalb ausdrücklich die lokale 0.8.0-Implementierung maßgeblich.

## Wiederverwendete Komponenten

| Bereich | Lokale Implementierung | Verwendung in Studio |
|---|---|---|
| Discovery | `connection.discover`, UDP 4720, `scan_iscope`; `DISCOVERED` enthält Seriennummer, Modell, IP, Geräte-ID | unverändert; automatisch alle 60 s |
| Geräteidentität | Seriennummer als Dictionary-Schlüssel, IP nur Adresse | unverändert; DHCP-Wechsel erzeugt neue Verbindung |
| Multi-Geräte | `dashboard.monitor.Fleet` hält einen `ScopeMonitor` je Seriennummer | Lebenszyklusmodell übernommen, eigener Manager |
| Statusverbindung | `ScopeMonitor._read_events`, TCP 4700, JSON-RPC und Ereignisse | direkt wiederverwendet |
| Telemetrie | `ScopeMonitor.snapshot`, `_view`, `_stack`, `status.coord_pair` | wiederverwendet, Werte normalisiert |
| Authentifizierung | `auth.authenticate`, lokale Schlüsselfindung | unverändert; keine eigene Schlüsselverwaltung |
| Bildprotokoll | `stream._read_frame`, `_send_json`, `is_image_frame`, `is_stacked_frame` | direkt wiederverwendet |
| RAW / JPEG | `decode_payload`, `to_display8`, `auto_stretch`; Bayer-Blockmittel | wiederverwendet; Ausgabe als QImage |
| Bildtakt | `ScopeMonitor._poll_frames` | unverändert: Stack vor Preview, adaptive Pausen |
| Reconnect | getrennte Command/Image-Loops | gleiche Strategie; aktives Socket-Close ergänzt |

`Fleet` ist für einen Webserver passend, bietet aber keine Monitor-Factory und
kein dauerhaftes Pausieren einzelner Geräte. Sein direkter Einsatz würde für
vollauflösende QImages und individuelle Lebenszyklen globale Monkeypatches oder
weitreichende interne Eingriffe verlangen. Studio verwendet stattdessen einen
kleinen eigenen Manager und einen versionierten `NativeMonitor`-Adapter.

## Warum die Bildausgabe angepasst ist

Der Browser-Encoder skaliert auf 720 Pixel und erzeugt JPEGs mit Qualität 82.
Das reicht nicht für eine native 100-%-Ansicht. Studio dekodiert stattdessen in
voller Stack-Auflösung, verwendet denselben STF und kopiert das RGB-Ergebnis in
ein eigenständig besitzendes QImage. QPixmap entsteht erst im GUI-Thread.
JPEG wird anhand seiner tatsächlichen Nutzdaten erkannt und nicht gestretcht.
Preview-Bayerdaten werden wie im Dashboard als 2×2-Luminanzvorschau behandelt.

## Ergänzungen für Zuverlässigkeit

- Upstream `stop()` wartet nur begrenzt, ohne alle blockierenden Sockets aktiv
  zu schließen. Studio hält die Sockets je Monitor und unterbricht sie aktiv.
  Nach einem Benutzer-Reconnect wird ein neuer Monitor erzeugt.
- Gleiche Bild-Nutzdaten werden anhand eines BLAKE2-Digests nicht neu verarbeitet.
  Empfangszeit und Zeit der letzten sichtbaren Bildänderung bleiben getrennt.
- Ein neuer App-State-Poll ersetzt ältere View-/Stack-Events. Damit überschreibt
  ein altes Ereignis nicht dauerhaft einen inzwischen neu abgefragten Zielnamen.
- Koordinaten können als Dictionary **oder Liste** ankommen. Beide Formen werden
  angenommen; die Listenform wurde am realen Gerät berücksichtigt.
- Abgeleitete Integrationszeit ist ausdrücklich als Näherung markiert.
- Der standardmäßig angenommene Transfermodus `Raw` aus dem Dashboard wird bei
  fehlender Geräteangabe nicht als bestätigte Telemetrie ausgegeben.
- Ausgehende Nachrichten sind auf eine explizite Lese-/Auth-/Bild-Allowlist begrenzt.
- Keine HTTP-Schicht, keine WebView, keine Änderungen an SeestarPy in `.venv`.

## Geprüfte ausgehende Methoden

Status: `get_device_state`, `scope_get_equ_coord`, `scope_get_horiz_coord`,
`iscope_get_app_state`, `get_wheel_position`, `test_connection`.

Authentifizierung: `get_verify_str`, `verify_client`, `pi_is_verified`.

Bilder: `get_stacked_img`, `get_current_img`.

Discovery wird separat von SeestarPy als UDP `scan_iscope` durchgeführt.
Weder `begin_streaming` noch `stop_streaming`, `set_setting`, GoTo-, Filter-,
Montierungs- oder Aufnahmebefehle sind über den Adapter zulässig.

## Referenzen

- https://github.com/astronomyk/seestarpy
- https://seestarpy.readthedocs.io/en/latest/api/dashboard.html
- https://seestarpy.readthedocs.io/en/latest/examples/live_dashboard.html
- https://seestarpy.readthedocs.io/en/latest/api/stream.html

Die Authentifizierungsdatei wurde nicht geöffnet, kopiert oder ausgegeben.
Die reale Anmeldung wurde ausschließlich von SeestarPy ausgeführt.
