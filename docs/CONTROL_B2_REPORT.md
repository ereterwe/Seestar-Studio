# Steuerungskorrektur 2.3.0b2 — 7. November 2026

## Ursachen und Korrektur

Der bisherige Button sendete `scope_goto([RA/15, Dec])`: eine mechanische
Montierungsbewegung, keine astronomische Beobachtung. Ein RPC-Code 0 wurde
irreführend als Bestätigung des gesamten Vorgangs dargestellt. Preview verlangte
einen bereits vorhandenen View-Modus; bei echter Leerlaufantwort `{}` blieb
der notwendige erste Vorschau-Start gesperrt. Zudem verlangte die UI eine
manuelle Filterauswahl. Stacking prüfte nur den Stage-Namen, nicht dessen
Zustand. Der Viewer verwarf relevante GoTo-/Solve-/AF-Ereignisse und behandelte
Ereignisfehler fälschlich wie fehlgeschlagene Status-/Authentifizierungsabfragen.

Die bevorzugte Aktion **Ziel anfahren & Aufnahme starten** verwendet jetzt
`iscope_start_view` mit lokalen Zielkoordinaten. **Nur GoTo** bleibt ausdrücklich
mechanisch. Die Vorschau benötigt eine bestätigte Kamera, ein entparktes Gerät
und keinen aktiven View; ein leerer Idle-View ist erlaubt. Standardmäßig wird
der aktuell ausgelesene Aufnahmefilter übernommen. Kein stiller Wechsel einer
persistent gespeicherten Option. Parken übernimmt den frisch gelesenen EQ-Modus.

Jedes Gerät besitzt seinen eigenen Worker, bestätigten unveränderlichen Intent,
Eventpuffer, Zeitlimit, Zustand und Verbindungszähler. Ein UI-Gerätewechsel
ändert kein laufendes Ziel und keine Folgeaktion. Gleichzeitige Aktionen auf
demselben Gerät und wiederverwendete Bestätigungen werden abgewehrt.

## Verifizierte Schnittstellenbasis

Maßgeblich ist die **lokal installierte SeestarPy 0.8.0** (`ui.py`, `raw.py`,
`connection.py`, `dashboard/monitor.py`). Ergänzender Abgleich mit der
[Upstream-UI-Dokumentation](https://seestarpy.readthedocs.io/en/latest/api/ui.html)
und dem [Projekt](https://github.com/astronomyk/seestarpy). Die Dokumentationsseite
zeigt teilweise eine ältere Versionsüberschrift; die lokale Implementierung
entscheidet. Keine Bibliotheksänderung, keine neue Abhängigkeit.

| API | Bedeutung / Verwendung |
|---|---|
| `ui.goto_target(target_name, ra=None, dec=None, lp_filter=False, verbose=True, timeout=300)` | Startet astronomischen View und wartet auf AutoGoto; bei bekannten Koordinaten kein Online-Namensresolver nötig |
| `raw.iscope_start_view(ra=None, dec=None, target_name='Unknown', lp_filter=False, mode='star', mosaic=None)` | Drahtparameter `target_ra_dec`, RA in Stunden; mit Koordinaten AutoGoto, mit `[None,None]` Sternenvorschau |
| `ui.autofocus(verbose=True, timeout=180)` / `raw.start_auto_focuse()` | Benötigt aktiven View, wartet auf AutoFocus; lokale Verbindung mit Keepalive erforderlich |
| `ui.start_stack(restart=True)` / `raw.iscope_start_stack(restart=False)` | Studio sendet immer explizit `restart:false`, setzt vorhandene Stacks nicht still zurück |
| `get_view_state()` / `iscope_get_app_state()` | Tatsächliche View-/Stage-Zustände; frischer App-State wird vor Aktionen und während Abläufen gelesen |
| `get_device_state` / `get_setting` | Kamera/Montierung/Fokussierer und `auto_af` / `stack_after_goto`; keine automatischen Schreibzugriffe auf diese Optionen |
| `iscope_stop_view(stage=...)` | Eigene AutoGoto-/AutoFocus-Aktion gezielt stoppen; bestätigtes Stop Recording beendet den aktiven View |

Die App benutzt die gebundene SeestarPy-Verbindung mit derselben lokalen
Authentifizierung. Ereignishandler werden vor dem Start registriert und
blockieren nicht. `page`-Unterereignisse gelten nicht als erfolgreicher
Gesamtabschluss; `route`/`lapse_ms` kennzeichnen äußere Abschlüsse. Fehler
verhindern schon beim ersten gemeldeten Fehlschlag Folgeaktionen. Gerätezeit-
stempel vor der Startantwort werden nicht als neue Erfolgsmeldungen verwendet.

## Ablauf und Grenzen

Idle / TargetSelected → GoToRequested → tatsächliches Slewing → PlateSolving →
TargetAcquired nur nach erfolgreichem PlateSolve **und** AutoGoto → Autofocusing →
ReadyToStack → StartingStack → tatsächlich gemeldetes Stacking.
Completed, Failed, Cancelled und Unknown bleiben unterscheidbar. Sent/Accepted
sind keine Belege eines erfolgreichen astronomischen Abschlusses.

Bei `auto_af:true` wartet Studio auf den Firmware-Autofokus, statt ihn doppelt
auszulösen. Bei ausgeschalteter Automatik fordert es AF erst nach erfolgreicher
Zielerfassung an. Stacking folgt nur auf nachgewiesenen AF-Erfolg und aktive
Sternenvorschau. Firmware-Autostacking wird beobachtet statt doppelt angefordert.
Die Kombination `auto_af:false` / `stack_after_goto:true` wird mit Erklärung
abgewiesen: Eine sichere AF-vor-Stack-Reihenfolge ist damit nicht gewährleistet.
Unbekannte Flags sperren die vollständige Sequenz; Studio verändert sie nicht.

Kein Start nach festem Zeitintervall. 300 Sekunden begrenzen die komplette
Sequenz; kein automatischer Neustart. Fehler, fehlende Ereignisse, verlorene
Antworten und Verbindungswechsel bleiben sichtbar. Bei Ausfall kein blindes
Fortsetzen: eine neue identifizierte Verbindung liest den Ist-Zustand einmal
zurück. Der unabhängige Viewer aktualisiert weiter. Ein laufender Stack kann
bei einer Unterbrechung der Steuerverbindung fortbestehen.

Abbruch betrifft nur die eigene Sequenz. AutoGoto/AF werden bei bestätigter
aktiver Stage gezielt gestoppt. Eine eigene Stackinitialisierung mit Fehler
wird beendet; ein ohne bestätigte Voraussetzungen gestarteter Firmware-Stack
wird mit `stage:Stack` gestoppt. Diese zusätzlichen Abbruchzweige sind simuliert
geprüft. READ ONLY verhindert neue/Folgebefehle; es verspricht keinen physischen
Stopp bereits laufender Aktionen. Ein entfernter Client kann weiterhin Änderungen
auslösen: das Protokoll bietet keine atomare geräteweite Besitzsperre.

## Reale Tests im Innenraum

Explizite Freigabe der Steuerung und freier Bewegungsraum lagen vor. Dynamische
Discovery, keine festen IPs/Seriennummern im Produkt. Zunächst nur S50, danach
S50 Pro. Keine fremde laufende Aufnahme vorgefunden oder unterbrochen. Das
Katalogziel M81 lag bei den Tests etwa 99° von der Sonne entfernt. Keine
Firmware-/Reset-/Authentifizierungsänderung, kein Schreiben der Automatikflags.

| Test | S50 | S50 Pro |
|---|---|---|
| Auth / Status / Automatikflags | Code 0; beide Flags true | Code 0; beide Flags true |
| Entparken | ScopeMoveToHorizon complete, ca. 16,7 s | gleiches Ereignis, ca. 16,7 s |
| Sternenvorschau | ContinuousExposure working; zurückgelesen | derselbe echte Modus bestätigt |
| Autofokus | angenommen, gestartet, Fehler 279: keine Sterne | Produktionssteuerung: angenommen, gestartet, Fehler 279; eigener AF gezielt beendet |
| Astronomischer GoTo | ScopeGoto complete, dann PlateSolve working/fail 251 | Produktionssteuerung: dieselbe Folge, Fehler 251 erkannt |
| Fehlerabbruch | erster Solve-Fehler → einmal AutoGoto stoppen; kein App-AF/Stack | Produktionssteuerung bestätigt denselben gezielten Abbruch |
| Manueller Stackstart | Code 0; zunächst Initialise, später Stack working; 0 akzeptiert / 4 verworfen | Code 0; Initialise/PlateSolve fail, später Stack-cancel beim ausdrücklichen Stop belegt |
| Vorschau/Aufnahme beenden | tatsächliches View cancel / mode none | Produktionssteuerung: tatsächliches View cancel / mode none |
| Parken | ScopeHome complete, close:true | Produktionssteuerung: ScopeHome complete, close:true |

**Wichtige Firmwarebeobachtung:** Beide Geräte starteten nach dem Solve-Fehler
selbst einen AF-Schritt innerhalb AutoGoto. Studio sandte keinen AF-Folgebefehl,
sondern stoppte AutoGoto; die Firmware meldete den Abbruch. Ein manuell
angeforderter Stack kann zunächst Initialisierung/Plate Solving auslösen und
trotz Fehler später in Stack wechseln. Daher ist Code 0 niemals „Aufnahme
erfolgreich“. Die zusätzlichen Stop-Zweige wurden danach implementiert und
simuliert geprüft, ohne denselben fehlgeschlagenen Hardwareversuch zu wiederholen.

Beide Geräte am Testende wieder **geparkt**, `equ_mode:false` wie zu Beginn.
Produktions-UI-Freigaben wurden aus echten Rückantworten geprüft: nach Stop
Preview möglich/Stack gesperrt; während Sternenvorschau umgekehrt; geparkt beide
gesperrt. Wechsel zwischen getrennten Testverbindungen bestätigte erneutes
Statuslesen. Ein absichtlicher physischer Netzwerkausfall wurde nicht erzwungen.

Lokale, nicht gepackte Detailnachweise: `reports/control-s50-*.json`,
`reports/control-pro-*.json`, insbesondere `control-pro-production-*.json`.
Sie enthalten Befehle, Code, Zeiten, ausgewählte Ereignisse und Vor-/Nachzustand;
keine Authentifizierungsschlüssel. S50-Pro-Tests liefen durch den Produktions-
ControlService; S50-Tests prüften zunächst die gleichen direkten Drahtbefehle.

**Not Verifiable Indoors:** Erfolgreiches Plate Solving, sternbasierter
AF-Erfolg, akzeptierte Deep-Sky-Subframes und die vollständige automatische
Kette sind weiterhin unter Sternenhimmel abzunehmen. Kein S30/S30-Pro-Test.

## Automatisierte und native Prüfung

Regression ergänzt um manuelle/automatische Erfolgssequenzen, innere/veraltete
Ereignisse, Solve-/AF-Fehler, abgelehnten Stack, fehlenden Abschluss,
Verbindungsausfall in GoTo/AF/Stackstart, geänderte Verbindungsidentität,
erneuten Statusabruf, READ ONLY, Widerruf, Doppelstart, zwei unabhängige Geräte,
UI-Auswahlwechsel, frischen Fremd-Aufnahmestart vor Senden, Abbruch,
Vorschau-/Stack-Freigaben, Tooltips und DE/EN. Erfolgssequenzen sind simuliert.
Native UI-Prüfung im Windows-Qt-Modus; Offscreen-Fontdarstellung wurde nicht als
visuelle Abnahme verwendet. Build-/Paketresultate stehen in B2_TEST_REPORT.md
und der Beta-Checkliste.
