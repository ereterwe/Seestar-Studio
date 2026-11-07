# Steuerungs-API-Audit — SeestarPy 0.8.0

Lokal geprüft: `raw.py`, `ui.py`, `connection.py`, `auth.py`. Keine realen
Steuerbefehle zum Prüfen gesendet. Prüfung der Implementierung ist kein
Hardware-Kompatibilitätsnachweis. Separate Verbindung pro Gerät; keine globale
Default-IP und niemals `ips="all"`.

| Aktion | Vorhandene Protokollabbildung | Besonderheit |
| --- | --- | --- |
| GoTo | scope_goto, [RA Stunden, Dec Grad] | Bewegung, ohne implizite Filteränderung |
| Tracking | scope_set_track_state, bool | Kann laufende Belichtungen beeinflussen |
| Vorschau starten | iscope_start_view, mode/target_ra_dec/target_name/lp_filter | Erfordert ausdrücklich gewählten Filter; kein verdeckter Default |
| Stacking starten | iscope_start_stack, restart=false | Bestehenden Stack nicht automatisch zurücksetzen |
| Stacking stoppen | iscope_stop_view, stage=Stack | Vorschau bleibt möglich |
| Aufnahme beenden | iscope_stop_view, stage=null | Beendet View/aktuelle Aktion |
| Belichtung | set_setting, expert_mode=true, exp_ms.stack_l | Persistente Änderung ausdrücklich bestätigen |
| Gain | set_control_value, [gain, Wert] | Zulässige Hardwaregrenzen nicht universell belegt |
| Filter | set_wheel_position, [Position] | 0 Dark / 1 Open / 2 LP laut API |
| Autofokus | start_auto_focuse | Operation kann Aufnahme unterbrechen |
| Parken | scope_park, equ_mode=aktueller Modus | Kein impliziter Moduswechsel; unbekannten Modus ablehnen |

`connection._Connection.send` wiederholt bei Verbindungsfehlern automatisch.
Für Mutationen ungeeignet: Antwortverlust darf keinen zweiten Start/GoTo
auslösen. Adapter verwendet das bestehende `_send_once` mit eindeutigen IDs,
aber genau einem Sendeversuch, begrenzter Antwortzeit und ohne RPC-Logging.
Ein Timeout nach dem Senden bedeutet **Ausgang unklar**, nicht sicher fehlgeschlagen.
Keine automatische Wiederholung oder Gegenaktion. Keepalive ist lesend und
bleibt bis zum Schließen der Steuerverbindung erhalten.

Control Mode ist nur sitzungsbezogen. Jede Aktion verlangt ein konkretes Gerät
und eigene Bestätigung mit Ziel, Parametern, aktuellem Aufnahmezustand und
Seiteneffekten. Bestätigung verfällt bei Geräte-/IP-/Zustandswechsel, Timeout
oder Wechsel in READ ONLY. Keine automatische Sequenz oder Planungsausführung.
Unmittelbar vor der Aktion wird die Serienkennung auf derselben authentifizierten
Verbindung lesend geprüft. Abweichende/fehlende Identität sperrt die Aktion;
nach Socketverlust darf eine Mutation nicht stillschweigend neu verbinden.
Neue Fähigkeiten aus `device.can_*` bleiben getrennte, echte Geräteangaben;
fehlende Angaben werden nicht aus Modellnamen erfunden.
