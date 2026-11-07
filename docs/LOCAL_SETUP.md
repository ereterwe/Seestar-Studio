# Lokale Einrichtung — V2.1

Der Assistent öffnet sich bei fehlender Konfiguration einmal automatisch und
ist jederzeit über **Einrichtung** erreichbar. Bestehende SeestarPy-Dateien
werden durch Existenzprüfung erkannt, nicht kopiert oder überschrieben.
Reihenfolge: ausdrücklich aktivierter Studio-Import, vorhandene Prozessvariable
SEESTAR_KEY_PATH, seestar.pem im Arbeitsordner, ~/.seestarpy/seestar.pem.
Gefunden bedeutet nicht am Gerät verifiziert.

Optional eine eigene PEM-Datei importieren oder eine rechtmäßig bezogene
APK/XAPK lokal auswählen. Die bestehende SeestarPy-Extraktion wird gekapselt,
nicht neu entwickelt. Unbekannte Formate führen zu verständlichen Fehlern.
Es gibt keinen Download, Upload, Cloud-Login oder mitgelieferten ZWO-Schlüssel.
Mehrere Kandidaten werden anhand öffentlicher SHA256-Fingerabdrücke auswählbar.
Eine Aktivierung benötigt eine ausdrückliche Bestätigung. Alte Dateien bleiben
erhalten. Änderungen gelten für neue Verbindungen, offene werden nicht beendet.

Importe liegen unter dem Qt-Benutzerkonfigurationsordner in authentication/keys.
Der Schlüsselname ist zufällig. Eine geschützte Windows-DACL erlaubt nur dem
aktuellen Benutzer und SYSTEM Vollzugriff; vor dem Schreiben der Schlüsselbytes
wird die Datei geschützt. Kein Schutz vor Prozessen desselben Benutzers oder
Administratoren, keine zugesicherte sichere Speicherlöschung. XAPK-Zwischendaten
werden in geschützten temporären Unterordnern verarbeitet und regulär entfernt.
Nach einem Prozess-/Systemabsturz können geschützte Reste verbleiben; keine
automatische Löschung fremder Dateien. Abbruch entfernt unaktivierte Kandidaten.

Der Verbindungstest authentifiziert eine separate Verbindung mit explizit
ausgewähltem Schlüssel und liest die Geräteidentität. Keine Steuerbefehle,
keine Wiederholung von Mutationen. Offline kann unbestätigt abgeschlossen werden.

**Diagnose** zeigt vor dem Speichern den gesamten lokalen JSON-Export. Keine
Seriennummern, IP-Adressen, Pfade, Ziele, Standorte, Bilder oder RPC-Inhalte.
Fehler werden als vorhanden/nicht vorhanden exportiert, nicht als Rohtext.
Keine automatische Übermittlung. Interne QA-Berichte im Entwicklungsordner
sind davon getrennt und dürfen nicht ungeprüft weitergegeben werden.

PEM-/APK-/XAPK-Import und Windows-Rechte wurden mit eigens erzeugten Testschlüsseln
geprüft, nicht mit neu importierten echten ZWO-Schlüsseln. Die rechtliche Prüfung
der Extraktionsverfahren vor öffentlicher Veröffentlichung bleibt offen.
