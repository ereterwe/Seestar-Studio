# Live View — V2.2

Jede Gerätekarte hat Live Stack/Live View. Die Wahl wird je stabiler
Gerätekennung lokal gespeichert. Stack- und Videobild behalten getrennte
Zoom-/Verschiebewerte. Einpassen, 100 %, Maximieren per Doppelklick,
Fenstervollbild (F11) und Bild speichern gelten für die gewählte Quelle.
Die FPS-Anzeige misst angenommene Decoderbilder, nicht eine zugesicherte
Kamerabildrate. Bei einem Fehler bleibt das letzte Videobild als veraltet sichtbar.

Die Anwendung abonniert ausschließlich bereits verfügbare Videoquellen.
Bei fehlendem Stream bleibt eine verständliche Meldung; zurück zu Live Stack
wechseln. Die Anwendung startet keinen Natur-/Mondmodus, stoppt keine
Aufnahme und ändert keinen Filter. Es gibt keinen versteckten Einzelbild-
Fallback, der als flüssiges Video bezeichnet würde.

## Technische Grundlage

Lokal geprüft: SeestarPy 0.8.0, `stream.build_rtsp_url`, RTSP_PORT 4554 und
RTSP_PORT_WIDE 4555. Diese sind Kandidaten, keine universelle Modellzusage.
Ein begrenztes RTSP-DESCRIBE muss SDP mit einer Videospur liefern, bevor eine
Kamera angeboten wird. Kein start_view/get_current_img und keine anderen
streamaktivierenden Geräte-RPCs im Videoadapter.

VideoSession kapselt einen eigenen QThread pro aktiviertem Gerät. VideoWorker
besitzt QMediaPlayer/QVideoSink; Bildkonvertierung erfolgt im Worker. Der
thread-sichere Puffer hält nur das jüngste Bild; GUI-Abnahme alle 50 ms,
maximal 30 angenommene Frames/s. RTSP nutzt Qt LowLatencyStreaming und
begrenzte Probe-/Timeoutwerte. Qt/FFmpeg wählt den verfügbaren Decoder,
Hardwarebeschleunigung wird nicht garantiert. Kein Audioausgang.

12 Sekunden ohne Bild lösen Fehler/Reconnect mit 5–30 Sekunden Wartezeit aus.
Kamera-/Ansichtswechsel beendet den alten Decoder. Veraltete, überholte
Konfigurationsanfragen werden verworfen. Gerätefehler bleiben getrennt.
GUI und Stack-Pipeline warten nicht auf Video.

## Tests / Grenzen

Synthetisches lokales Video läuft durch den echten Qt-Decoder; SDP-, Fehler-,
Reconnect-, Mehrgeräte- und Ressourcenfreigabetests vorhanden. Reale RTSP-
Wiedergabe/H.264/Latenz/Hardwaredecodierung/Weitwinkel/Langzeitbetrieb noch offen.
Während der lesenden S50/S50-Pro-Prüfung lief auf beiden Deep-Sky-Stacking;
kein RTSP-Video verfügbar, keine Modusänderung vorgenommen.

Qt 6.12 Multimedia verwendet das mitgelieferte FFmpeg 9.0.1. Lokale DLL
meldet LGPL 2.1 or later; Buildkonfiguration und Lizenzhinweise dokumentiert.
Vollständige Prüfung vor Veröffentlichung: `../LICENSING.md`.
