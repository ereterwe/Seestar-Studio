# Grafischer Observation Planner — V2.2

1. Nacht und Zeitzone wählen; Windows-Zeitzone ist die Vorgabe.
2. Teleskop wählen. Verbundene Geräte stehen zuerst, bekannte Geräte bleiben offline planbar.
3. Ziel im Sky Explorer wählen, im Planner hinzufügen, Dauer und vorgeschlagenen Start prüfen.
4. Weitere Ziele hinzufügen: 20:00–22:00 plus fünf Minuten Wechsel ergibt 22:05.
5. Balken ziehen, am rechten Rand in fünf Minuten Schritten verlängern oder verkürzen,
   doppelklicken zum Bearbeiten, Kontextmenü zum Duplizieren/Löschen.

Ein Zeitmaßstab für alle Geräte; zeitgleiche Ziele verschiedener Teleskope
sind erlaubt. Wechselzeiten sind grau. Rot bedeutet Zeitkonflikt, Orange
ungünstige Astronomie, Blau ungeprüft, Grün erfolgreich geprüft. Kleine Balken
haben vollständige Tooltips. Zoom über +/− oder Strg+Mausrad, horizontal scrollen.

Der nächste freie Zeitraum berücksichtigt alle Intervalle und Wechselzeiten
auf dem ausgewählten Gerät. Standardmäßig werden neue Ziele angehängt;
„Frühere Lücken nutzen“ sucht auch passende Lücken. Manuelle Änderungen
verschieben andere Einträge nicht. „Nächster freier Zeitraum“ korrigiert nur
den ausgewählten Eintrag. Optimierung zeigt zuerst alte/neue Zeiten zur
Prüfung; Abbrechen erhält den bestehenden Plan.

Astronomische Prüfungen laufen im Hintergrund auf Basis des ausdrücklich
bestätigten Sky-Explorer-Standorts. Höhe/Azimut, Auf-/Untergang, Dunkelheit und
Sichtbarkeitsfenster werden berechnet; ein freier Slot allein wird nicht grün.
Zeit- und Standortwahl sind unabhängig. Kein Standort wird aus Windows abgeleitet.

Die lokale Planbibliothek speichert Änderungen atomar im Benutzerprofil unter
plans. Neue Nacht, Duplizieren, Löschen, Import und Export sind verfügbar.
Exportierte V2.1-Pläne werden als neue lokale Kopie übernommen; explizite UTC-
Zeitpunkte bleiben unverändert, bisher implizite Reihenfolgen werden mit
Wechselzeiten materialisiert. Prüfungen werden beim Laden neu berechnet.

Formatversion 2 speichert UTC-Zeitpunkte, ursprüngliche Planungszeitzone,
Datum, stabile Gerätekennungen, Ziele, Dauer, Wechselzeit und Prüfergebnisse.
Doppelte Uhrzeiten verlangen die erste/zweite Variante; nicht existierende
Sommerzeit-Uhrzeiten werden abgewiesen. Eine Nacht kann 23 oder 25 Stunden haben.
Sprache beeinflusst gespeicherte Zeiten nicht. Höchstens 100 Einträge pro Plan.

Der Planer besitzt keinerlei Geräteausführung. Bearbeiten/Speichern startet
keine Aufnahme oder Bewegung. Eine spätere Ausführung benötigt einen eigenen
freigegebenen Workflow.
