# Observation Planner

Planung, Speicherung und Validierung ausschließlich lokal. Keine Verbindung
zum Steuerungsadapter und keine automatische Ausführung. Gerätezuordnung per
entdeckter Serienkennung oder frei benanntem Offline-Planungsplatz. Ziele aus
dem lokalen Sky Explorer; maximal 100 Einträge, je 1–720 Minuten, Wechselzeit
0–120 Minuten. Einträge bearbeiten, löschen oder umsortieren.

Zeitangaben mit ausdrücklichem UTC-Offset; wiederholte Stunden beim Wechsel
der Sommerzeit bleiben eindeutig. Die Timeline verwendet für alle Geräte UTC.
Standardmäßig laufen Einträge je Gerät nacheinander, Geräte parallel.
Feste Starts bleiben unverändert; Überlappungen und fehlende Wechselzeit werden
markiert. Unbekannter Standort bedeutet ungeprüfte Sichtbarkeit.

Optimierung ist eine Heuristik: früh endende verfügbare Beobachtungsfenster
zuerst, Warten auf den Beginn eines passenden Fensters möglich. Keine Garantie
eines global optimalen Plans. Bei festen Terminen wird die Reihenfolge dieses
Geräts beibehalten. Sichtbarkeit auf der dem Planbeginn zugehörigen Nacht
(lokaler Mittag bis Mittag), ≥30° und Sonne ≤−18°, 5-Minuten-Raster.
Wetter, Hindernisse, Akku, Meridianwechsel und tatsächliche GoTo-Dauer bleiben
unmodelliert. Wechselzeit ist eine explizite Benutzerannahme.

JSON-Pläne werden atomar gespeichert. Laden validiert Version, Größenlimit,
IDs, Geräte, Dauer und Zeitformate, bevor der aktuelle Plan ersetzt wird.
Standort-/Planänderungen verwerfen alte Validierungsergebnisse.
