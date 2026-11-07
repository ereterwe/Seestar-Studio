# Lokale Session-Analyse

SQLite-Datei `history.sqlite3` neben den persönlichen Einstellungen. Enthält
Gerätekennung/-modell, Ziel, beobachtete Zeiten, Status und ausgewählte numerische
Telemetrie. Keine Bilder, Authentifizierungsdaten, Netzwerkadressen oder Standorte.
Kein Upload. Schreibthread und separater Leseworker blockieren die GUI nicht.
15-Sekunden-Raster; Verbindungs-/Ziel-/Statuswechsel zusätzlich sofort. Begrenzte
Schreibwarteschlange, ausgelassene Pakete werden in der Oberfläche ausgewiesen.

Session beginnt beim ersten beobachteten Stack. Neue Session bei Zielwechsel,
Zählerrückgang oder Wiederkehr nach >5 Minuten Beobachtungslücke. Ein normaler
Stack-Stopp beendet die Session. Programmende markiert `monitor_closed`, ein
nicht sauber abgeschlossener früherer Lauf `monitor_interrupted`. Diese Angaben
behaupten keinen tatsächlichen Aufnahmebeginn/-schluss am Teleskop.

Kurze Ausfälle bleiben als Lücken mit fehlenden Messwerten erhalten; Cachewerte
werden nicht als neue gültige Messung eingetragen. Der angezeigte Zeitraum ist
die beobachtete Zeitspanne einschließlich möglicher Lücken, keine Belichtungszeit.

Zwei ausdrücklich ungefähre Integrationsgrößen:
- letzter akzeptierter Gerätezähler × aktuell gemeldete Belichtung (wie Viewer);
- Summe der Zählerzuwächse × unveränderte Belichtung ausschließlich zwischen
  verbundenen Messpunkten mit höchstens 30 Sekunden Abstand.

Bei Belichtungswechseln, fehlenden Werten oder Lücken wird das Intervall nicht
bewertet. Die Oberfläche zeigt deren Anzahl. Diese Schätzung kann nicht erkennen,
ob zwischen zwei Messpunkten die Belichtung vorübergehend geändert wurde.
Keine Behauptung einer exakten historischen Gesamtintegration.

Bis zu vier der 200 neuesten Sessions lassen sich vergleichen. Temperatur und
Akku auf relativer verstrichener Sessionzeit, unterschiedliche Dauern sind
separat angegeben. Höchstens 1.001 Plotpunkte pro Session; Lücken werden nicht
blind verbunden. Datenbankfehler lassen den Livebetrieb weiterlaufen.
Keine automatische Datenlöschung. Persönliche Datenbank nicht weitergeben oder
in Git/Release aufnehmen. Mehrstündiger realer Einsatz der Historie ausstehend;
aktuelle Tests verwenden ausschließlich simulierte Telemetrie.
