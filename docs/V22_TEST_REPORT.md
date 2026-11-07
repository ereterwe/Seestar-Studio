# V2.2 — Testbericht, 6. November 2026

## Automatisiert / simuliert

87 Tests bestanden; `reports/v22-final-tests.log`. Enthalten sind alle bisherigen
71 Tests und 16 neue Video-, Planner-/DST-/Persistenz-/Migrations-/Sprachtests.

Video: echtes Qt-Decoding eines synthetischen lokalen GIF-Videos, unabhängige
Gerätekarten, Erhalt des Stackbildes, SDP-Verfügbarkeit, Decoderfehler,
begrenzter Reconnect und beendete Worker. Das ist kein echter RTSP-Hardwaretest.
Planner: 22:05-Slot, alle Intervalle/Wechselzeiten, unabhängige Geräte,
Konflikte/Drag/Resize, Speichern/Neustart, V1-Import, Zeitwechsel (23/25 h),
Optimierung nur nach Vorschau. Sprache: Ressourcen, laufender Wechsel,
Systemfallback, Persistenz und Formate.

Native Ansichten: 1920×1080, sechs Tabs DE/EN, Einrichtung, Einstellungen,
Diagnose mit simulierten Geräten; `reports/v22-ui-latest.json` verweist auf
Screenshots/Textaudit. Keine echten Aufnahmen im simulierten UI-Test.

## Tatsächliche Hardware — nur lesend

`reports/v22-hardware.json`: 93 Sekunden, S50 und S50 Pro gleichzeitig.
S50: vier Stack-Aktualisierungen, Stackzähler 63→66.
S50 Pro: sechs Stack-Aktualisierungen, Stackzähler 29→34.
Beide meldeten Stage Stack. Sauberes Beenden, keine Steuerung/Modusänderung.

RTSP-DESCRIBE an den SeestarPy-Kandidatenports lieferte keine verfügbare
Videospur. Keine Videoframes empfangen. **Echter Live View ist nicht abgenommen.**
Keine Auskunft darüber, welcher andere Gerätemodus Video ermöglichen würde,
ohne diesen separat geprüft zu haben. Keine S30-/S30-Pro-Hardwaretests.

## Build / offene Abnahmen

Windows-Ausgabe wird unter dist/2.2.0.dev1/SeestarStudio erstellt; portable ZIP
und Installer unter release. Die ältere laufende V2.1-Anwendung bleibt erhalten.
Finale EXE-Prüfung erfolgreich: `reports/v22-exe.json`, Exitcode 0,
sauber beendete Worker, 1920×1080, sechs native Tabs, Control Mode deaktiviert.
Beide Geräte automatisch erkannt; echte RAW-16-Bit-Stackbilder (2160×3840)
und Telemetrie in der fertigen EXE angezeigt. Beim Screenshot S50-Zähler 185,
S50-Pro-Zähler 201, beide Stage Stack. Zusätzlich lokaler Katalog mit 14.034
Objekten und Offline-Astronomie erfolgreich berechnet (ausdrücklich synthetischer
QA-Standort in isoliertem Profil; keine Änderung persönlicher Standorte/Pläne).

Artefaktprüfung `reports/release-audit.json`: ZIP intakt, 1.406 Laufzeiteinträge,
152 Quelleinträge, 225 Lizenzeinträge; 0 verbotene private Dateitypen. Qt-
Videoplugin, avcodec-DLL und Sprachressourcen enthalten. Kein Ersatz für eine
vollständige Lizenz-, Daten- oder Git-Historienprüfung. Buildprotokolle:
`reports/build-v22.log` und `reports/build-installer-v22.log`.
Installer-Lebenszyklus bleibt offen, da die V2.1-Benutzerinstanz läuft.

Ausstehend: echter RTSP/H.264/Kamerawechsel/Latenz, mehrstündiger Betrieb,
physische Netz-/Stromausfälle, Fremd-PC ohne Python, V2.2-Installer-Lebenszyklus
bei geschlossener Benutzerinstanz, reale Steuerung (nicht freigegeben).
V2.1-Installer-Lebenszyklus zuvor geprüft, nicht als V2.2-Test umetikettiert.

Keine Veröffentlichung. Lizenz-/native Quellen-/Extraktionsrechtsprüfung vor
Weitergabe bleibt offen; LICENSING.md enthält die Einzelpunkte.
