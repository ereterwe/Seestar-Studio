> Current Telescope Desk working documentation. Earlier release facts are preserved unchanged in [the Seestar Studio archive](docs/history/seestar-studio-b3/COMPATIBILITY.md). New build status: [minimization report](docs/compliance/MINIMIZATION_REPORT.md).

# 2.3.0b3 — lokale Compliance-Korrektur

8. November 2026: Der Projektverantwortliche hat klargestellt, dass b3 neu lokal
zu erstellen und der Quellcode auf GitHub zu aktualisieren ist. Kein b3-Link wird
benötigt. B2 bleibt als Vergleichsbasis unverändert. Keine neuen Funktionen.

Korrekturen: Colorama-Quellen/Lizenz, kollisionsfreie Vendor-Notices, neun unbenutzte
Qt-Dateien ausgeschlossen, öffentliche Projektangaben berichtigt, vollständiger
PASS/OPEN/BLOCKER-Prüfer und dokumentierte native/rechtliche Quellenlücken.
166 automatisierte Tests bestanden; b3-Build und Prüfstatus siehe
[Compliance-Bericht](docs/RELEASE_COMPLIANCE_REPORT_2.3.0b3.md).
Native Quellen-/Buildnachweise und Rechtsfragen sind keine geschlossenen Punkte.
Neue öffentliche Binär-Releases sind nicht durch den Quellcode-Push freigegeben.

# Kompatibilität — 7. November 2026

Historischer Stand vor dem Steuerungs-Bugfix, Beta 2.3.0b1: 95 automatisierte Tests, portable und installierte EXE lokal
geprüft. Während der finalen Beta-Läufe keine Geräte erkannt. Die folgenden
Hardwarebelege bleiben auf ihre tatsächlich geprüften Vorgängerversionen und
Funktionen begrenzt. Echte Windows-/Seestar-Positionsabfragen, externer PC,
RTSP und Langzeitbetrieb nicht nachträglich als bestätigt eingestuft.
Details: docs/BETA_TEST_REPORT.md.

Die Einstufung bezieht sich auf geprüfte Funktionen, nicht pauschal auf jede
Funktion eines Modells. Bibliotheksbasis: SeestarPy 0.8.0, derzeit fest versioniert.

| Modell | Einstufung | Nachweis / Grenze |
|---|---|---|
| Seestar S50 | **Hardwaregetestet** | Discovery, authentifizierte Telemetrie, RAW-Livestacks, native Anzeige; neue V2-Funktionen zunächst separat unbestätigt |
| Seestar S50 Pro | **Hardwaregetestet** | dieselben Viewer-Funktionen, individuelles Trennen/Reconnect; neue V2-Funktionen zunächst separat unbestätigt |
| Seestar S30 | **Theoretisch kompatibel** | Architektur und SeestarPy legen Kompatibilität nahe; keine echte Hardware, keine ausreichenden modellspezifischen Tests |
| Seestar S30 Pro | **Theoretisch kompatibel** | bekannte SeestarPy-Streamvarianten; keine echte Hardware, keine ausreichenden modellspezifischen Tests |
| Weitere Modelle | **nicht bewertet** | Erkennung vorhandener Fähigkeiten erforderlich; keine erfundenen Eigenschaften |

**Simuliert getestet** wird erst vergeben, wenn konkrete modellspezifische
Fixtures mit Herkunft und automatisierten Tests vorliegen. Die allgemeinen
Multi-Geräte-/Bild-/Fehlertests sind keine S30-Hardwaretests.
**Nicht unterstützt** wird nur bei nachgewiesener Inkompatibilität vergeben.

Kernregeln: keine festen IPs/Seriennummern, getrennte Sitzungen und Fehler,
variable Auflösungen/Formate, optionale Telemetrie, Fähigkeiten statt Modell-
Sonderfällen. Unbekannte Fähigkeiten bleiben unbekannt und werden nicht aktiv
durch gefährliche Befehle getestet. S50/S50 Pro haben praktische Priorität.

File Manager: SMB-Listen und JPEG-Download mit Abbruch/Resume/Duplikaterkennung
auf S50 und S50 Pro real bestätigt (`docs/PHASE1_TEST_REPORT.md`); größere
rekursive Transfers zusätzlich simuliert. Keine entsprechende Aussage für S30.

Historisch vor b2: Control Mode damals noch nicht real freigegeben.
Aktuelle Indoor-Nachweise siehe unten. Externe Windows-Installation mit anderer
S50-Hardware bleibt offen. Externe S50-Tests prüfen einen anderen PC, kein neues Modell.

V2-Status: Sky Explorer und Planner offline mit synthetischen Standorten geprüft.
Control Mode ausschließlich mit simulierten Geräten, einschließlich Antwortverlust,
DHCP-Identitätsabweichung und Freigabewiderruf. Session-Analyse mit simulierten
Zählerwechseln, Ausfällen, Neustarts und zwölf Stunden virtueller Messzeit geprüft.
Keine zwölfstündige reale Laufzeitprüfung. Nach der Offline-Entwicklung wurde ein S50 wieder eingeschaltet (drinnen).
45 Sekunden Discovery/Auth/Telemetrie lesend bestätigt, kein Bild verfügbar.
Keine Aufnahme oder Bewegung gestartet. V2.1-Importe bisher synthetisch getestet;
externe Ersteinrichtung mit echter Authentifizierung bleibt unbestätigt.

## V2.2 — neuer Nachweis

S50 und S50 Pro: paralleler Live Stack und authentifizierte Telemetrie während
laufender Aufnahmen erneut real geprüft (93 Sekunden, jeweils steigende
Stackzähler; `docs/V22_TEST_REPORT.md`). Keine echten Steueraktionen.

Live View: per Gerät separat implementiert und mit synthetischen Frames,
Fehlern, SDP-Antworten und lokalem Video geprüft. Beide echten Geräte stellten
im getesteten Aufnahmemodus keinen verfügbaren RTSP-Videostream bereit.
Daher **keine hardwarebestätigte Live-View-Kompatibilität** für irgendein Modell.
Portnummern aus SeestarPy sind nur Kandidaten; Kameraoptionen erfordern eine
positive SDP-Videoantwort. Weitere Firmware-/Kameravarianten bleiben offen.

## 2.3.0b2 — tatsächliche Indoor-Steuerung

S50 und S50 Pro: Auth/Status, Entparken/Parken, Sternenvorschau, mechanischer
GoTo innerhalb AutoGoto, Plate-Solving-Start/Fehler 251, AF-Start/Fehler 279,
manueller Stackbefehl und ausdrückliches Beenden geprüft. Beide wieder geparkt.
Beim S50 Pro wurden die neuen Produktionsabläufe einschließlich gezielter
Fehlerabbrüche genutzt. Keine erfolgreiche automatische Deep-Sky-Sequenz
behauptet: Solve-/AF-Erfolg und akzeptierte Bilder sind draußen abzunehmen.
Alle zusätzlichen Fehler-/Parallel-/Reconnect-Zweige automatisiert simuliert.
Keine Änderung der S30-/S30-Pro-Einstufung. Siehe docs/CONTROL_B2_REPORT.md.
