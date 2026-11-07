# Sprache und Formate — V2.2

Einstellungen: Automatisch (Windows), Deutsch, English. Automatik wählt für
deutsche Windows-Sprache Deutsch, sonst Englisch. Die Wahl wird gespeichert
und unmittelbar angewendet; Geräteverbindungen bleiben bestehen.

Zentrale Ressourcen: seestar_studio/translations/messages.json. Die Quelle
ist ein stabiler interner Text; DE/EN sind Präsentationsvarianten. `source`
liefert diese kanonische Quelle, `tr` übersetzt die Darstellung. Protokollwerte,
Gerätekennungen, Dateinamen und gespeicherte Nutzdaten bleiben unverändert.
Formatplatzhalter sind zentral und werden automatisch geprüft.

TranslationController aktualisiert Qt-Widgets, Dialogtitel, Aktionen,
Tooltips, Tabellen, Komboboxen und Datumsfelder; Qt-Standarddialoge erhalten
qtbase_de.qm. Signalblockierung verhindert Aktionen durch reine Übersetzung.
Häufig aktualisierte Labels übersetzen direkt beim Setzen. Unbekannte Texte
bleiben lesbar; unerwartete fremde Serverfehlermeldungen werden nicht erfunden.

Zahlen verwenden QLocale, Datumswerte das gewählte Anzeigeformat; englische
Zeitdarstellung berücksichtigt das Windows-Kurzzeitformat. Planzeitzone und
Sprache sind unabhängig. Eigene neue QPainter-Texte explizit mit tr darstellen.

Tests: Ressourcen/Platzhalter, Fallback/Systemsprache, laufender Wechsel,
Persistenz, unveränderte technische Werte und Zahlenformate. Native DE/EN-
Ansichten aller Haupttabs sowie Einrichtung/Einstellungen/Diagnose geprüft.
Der automatisierte Textaudit deckt die gezeigten Ansichten ab, nicht jede
mögliche Firmware-Fehlermeldung.
