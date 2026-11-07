# Tag-Nacht-Hintergrund — 2.3.0b2

Der Observation Planner verwendet ausschließlich den bereits bestätigten
Beobachtungsstandort. Ohne Standort bleibt die Timeline neutral und zeigt einen
Hinweis. Es wird weder eine Position ermittelt noch aus der PC-Zeitzone abgeleitet.
„Tag-Nacht-Hintergrund anzeigen“ / „Show Day/Night Background“ ist standardmäßig
aktiv und wird als lokale Anzeigeoption gespeichert.

## Berechnung

Vorhandene Astropy-Version 8.0.2, keine neue Abhängigkeit. `get_sun` mit eingebauter
Ephemeride, topozentrisches `AltAz`, geometrische Höhe bei Druck 0. Die vorhandene
Offline-IERS-Konfiguration bleibt aktiv; keine Netzwerkabfrage, keine Online-
Ephemeriden. Höhe/Koordinaten stammen aus dem bestätigten Standort.

Die Farbwerte werden kontinuierlich zwischen Sonnenhöhen-Stützpunkten
interpoliert: gedämpftes Gelb/Orange am Tag, Violett, Dunkelblau und fast Schwarz.
Phasengrenzen: 0°, −6°, −12°, −18°. Unter −18° astronomische Dunkelheit.
Die Farben sind eine Orientierung und keine physikalische Himmelshelligkeit.

Sonnenauf-/untergang: geometrisches Sonnenzentrum bei **−0,8333°**. Diese
übliche Näherung berücksichtigt mittlere Refraktion und Sonnenscheibenradius.
Die Dämmerungsschwellen bleiben geometrisch. Keine ungeeignete Anwendung der
Astropy-Refraktionsformel weit unter dem Horizont. Lokaler Horizont, Gelände,
Bäume/Gebäude und individuelle atmosphärische Bedingungen werden nicht modelliert;
Höhendip eines freien Meereshorizonts ebenfalls nicht. Keine sekundengenaue
Vorhersage eines beobachteten Sonnenaufgangs behauptet.

Zeitabstand höchstens eine Minute über den gesamten sichtbaren Zeitraum.
Schwellenübertritte werden mit Astropy erneut ausgewertet und per Bisektion
auf ein numerisches Intervall unter einer Sekunde eingegrenzt. Sehr kurze
Streifkontakte nahe einem Polarkreis können unter die Abtastauflösung fallen.
Warnungen zu außerhalb der Präzisionsgrundlage liegenden Zeitdaten erscheinen
als Näherungshinweis. Dunkelheitsdauer summiert die tatsächlich berechneten
Intervalle einschließlich am Darstellungsrand abgeschnittener Abschnitte.

## Zeitachse und Darstellung

Zeiten sind intern UTC-aware. Lokale Mittage begrenzen die Nacht; dadurch
bleiben 23-/25-Stunden-Nächte bei Sommerzeitwechseln korrekt. Die Anzeige nutzt
die Planzeitzone, unabhängig von Standort/Windows-Zeitzone. Feste Planblöcke
außerhalb einer Nacht erweitern die Timeline auf weitere lokale Nächte.
Jeder zusätzliche Tag wird neu berechnet; kein wiederholtes Tagesmuster.

Das Farbraster wird an absoluten Zeitpunkten verankert, wie Blöcke und Ereignisse.
Zoomen/Scrollen verändert keine Berechnung und verschiebt keine Sonnenzeit.
Alle Gerätespuren teilen denselben Verlauf. Deckende Blockfarben und helle
Beschriftungen bleiben erhalten. Dezente Linien zeigen Sonnenauf-/untergang,
Nachtbeginn und Nachtende; lokale Uhrzeit direkt am Marker, vollständige lokale
Zeit mit Datum/UTC-Offset als Tooltip. Bei Platzmangel entfallen überlappende
Markertexte, die Linie und ihr Tooltip bleiben bestehen.

Polartag wird nicht künstlich verdunkelt. Polarnacht wird nach tatsächlicher
Höhe eingefärbt und nicht pauschal als astronomische Nacht behandelt. Ein
Hinweis benennt Zeiträume ohne vollständige astronomische Dunkelheit.

## Verarbeitung und Grenzen

Ein eigener Worker, höchstens ein aktiver Auftrag, nur neuester gewünschter
Zeitraum; maximal vier Profile im Arbeitsspeicher. Alte Standort-/Datumsresultate
werden nicht angezeigt. Fehler führen zum neutralen Hintergrund ohne endlose
Wiederholungen. Beenden signalisiert Abbruch zwischen Berechnungsschritten.
Die Darstellung unterstützt bis zu 366 Tage; darüber verständlicher Hinweis
und neutraler Hintergrund. Berechnungen und Standorte werden nicht protokolliert.

## Referenzen und Prüfung

- [Astropy get_sun](https://docs.astropy.org/en/stable/api/astropy.coordinates.get_sun.html)
- [Astropy AltAz und Refraktionsgrenzen](https://docs.astropy.org/en/stable/api/astropy.coordinates.AltAz.html)
- [USNO Definitionen für Aufgang, Untergang und Dämmerung](https://aa.usno.navy.mil/faq/RST_defs)
- [USNO Referenzdaten-API](https://aa.usno.navy.mil/data/api)

Unabhängiger Abgleich für frei gewählte Testpunkte (52°/13°, −33°/151°, 0°/0°)
am 20. März 2026: Sonnenauf-/untergang und bürgerliche Dämmerung, UTC, jeweils
unter 90 Sekunden Differenz zu minuten-gerundeten USNO-Werten. Referenzen am
7. November 2026 einmalig als Entwicklungsprüfung abgerufen. Anwendung und
Tests verwenden keine Onlineabfrage und keine persönlichen Testkoordinaten.
Nautische/astronomische Schwellen zusätzlich durch Astropy-Höhen vor/am/nach
jedem berechneten Ereignis geprüft. Weitere Tests: Polar-, DST-, Mehrtages-,
Standortwechsel-, Cache-/Ausfall-, Render-/Zoom-/Scroll- und Einstellungsfälle.
