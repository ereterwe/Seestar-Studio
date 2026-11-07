# Optionale Standortvorschläge

Kein Abruf beim Start. Nur „Windows-Standort verwenden“ mit zusätzlicher
Zustimmung ruft Windows.Devices.Geolocation.Geolocator auf. Der Windows-Dienst
kann Microsoft-Dienste und Netzwerkdaten verwenden. Seestar Studio verwendet
keine eigene IP-Geolocation und keinen eigenen Standortserver.

PyWinRT 3.2.1 ist konsistent mit allen 3.x-Projektionspaketen fest versioniert;
kein unkontrolliertes Mischen mit Runtime 4. RequestAccessAsync läuft im
Vordergrund auf dem Qt-GUI-Thread; Statusabnahme per Timer, kein blockierendes
Warten. Erst nach Allowed folgt eine einmalige Positionsabfrage mit Zeitlimit.
Abbrechen, manuelle Änderung oder Dialogende verwirft laufende Vorschläge.

Gemeldete horizontale Genauigkeit wird angezeigt; ab 1 km ausdrückliche grobe
Näherung. Höhenübernahme nur bei Geoidbezug (Meereshöhe), endlichem Wert und
gemeldeter vertikaler Unsicherheit von höchstens 100 m. Andernfalls Höhenfeld
beibehalten und manuell prüfen. Keine erfundenen Höhen oder Genauigkeitswerte.

SeestarPy 0.8.0 dokumentiert get_device_state mit location_lon_lat als [lon,lat].
Ein eigener begrenzter Read-only-Aufruf liest device und location_lon_lat,
prüft die Serienkennung der Antwort und schließt die Verbindung. Keine
set_user_location-Aufrufe. Höhe/Genauigkeit sind daraus nicht belegt und bleiben
unbekannt; gespeicherte Koordinaten können veraltet sein. Authentifizierung
nutzt ausschließlich die vorhandene SeestarPy-Konfiguration.

Nur Bestätigung speichert Site im Benutzerprofil. Daten werden weder in Logs
noch Diagnosen oder Release-Archiven übernommen. Windows-Zeitzone ist ein
Vorschlag aus tzlocal; Standort und Zeitzone bleiben unabhängig.

Automatisiert getestet: Ablehnung, fehlender Dienst, Erfolg mit Simulation,
Unsicherheit/Geoidbezug, Abbruch/späte Antworten, manuelle Korrektur, gültige
Wertebereiche und read-only Geräteidentität. Echte Standortabfragen noch offen.

Primärquellen:
https://learn.microsoft.com/en-us/windows/apps/develop/maps-and-location/get-location
https://learn.microsoft.com/en-us/uwp/api/windows.devices.geolocation.geolocator.requestaccessasync
https://pywinrt.readthedocs.io/en/latest/versioning/
Lokale API-Belege: installierte seestarpy/raw.py und winrt-Projektionssignaturen.
# Ergänzung 2.3.0b2

Bei verweigerter Berechtigung oder gemeldetem deaktiviertem Standortzugriff
erscheint „Windows-Standorteinstellungen öffnen“. Erst ein Klick öffnet über
Qt QDesktopServices den offiziellen URI `ms-settings:privacy-location`.
Dialog und Anwendung bleiben offen; keine Änderung der Berechtigungen und
keine automatische Folgeabfrage. Erneuter Abruf erfordert wieder die vorhandene
Benutzeraktion/Zustimmung. Bei Startfehler wird der manuelle Windows-10/11-Pfad
angezeigt; Koordinaten können weiterhin manuell eingegeben werden.

Fehlerkategorien: denied, disabled, no_data, failed, timeout, unsupported.
Sie beruhen auf GeolocationAccessStatus, PositionStatus, Timeout und bekannten
HRESULTs. Unbekannte Fehler werden nicht zu Berechtigungsproblemen umgedeutet.
Windows kann App-/System-/Richtliniensperren nicht in jedem Fall eindeutig
unterscheiden; „disabled“ beschreibt den gemeldeten API-Zustand, keine selbst
ermittelte Änderung eines globalen Windows-Schalters. Keine Rohfehlermeldungen
mit potenziell privaten Inhalten ausgegeben. Alle Meldungen DE/EN.

Tests verwenden Fake-WinRT-Antworten und einen abgefangenen URI-Aufruf; sie
ändern keine echten Datenschutzeinstellungen und fragen keine echte Position ab.

Primärquellen:
[Windows-Einstellungs-URIs](https://learn.microsoft.com/en-us/windows/apps/develop/launch/launch-settings),
[PositionStatus](https://learn.microsoft.com/en-us/uwp/api/windows.devices.geolocation.positionstatus),
[Microsoft-Standortleitfaden](https://learn.microsoft.com/en-us/windows/apps/develop/maps-and-location/get-location).

