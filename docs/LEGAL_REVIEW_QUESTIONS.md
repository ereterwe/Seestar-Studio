# Gezielte Fragen für die rechtliche Prüfung

Produkt: Seestar Studio, kostenloser GPL-3.0-only-Windows-Client für lokale
Seestar-Teleskope. Prüfstand 8. November 2026. Technische Belege und Quellen sind
gesammelt; diese Fragen wurden keinem Dritten zugesandt; es wurde kein Patentpoolvertrag
abgeschlossen und keine externe Rechtsauskunft beauftragt.

## APK und Interoperabilität

Feststehend: Wir liefern weder ZWO-APK/XAPK, Firmware noch private ZWO-Schlüssel.
Der Nutzer beschafft seine Datei selbst von ZWO oder einem Internet-Mirror und
wählt sie ausdrücklich aus. Ein vorhandenes SeestarPy-Werkzeug liest lokal
unverschlüsselte PEM-Zeichenfolgen aus zwei bekannten nativen APK-Bibliotheken.
Es führt den ZWO-Code nicht aus. Ein Signaturschlüssel wird lokal für eine
Challenge verwendet; übertragen wird die Signatur. Der Assistent verlangt bereits
die Bestätigung der Nutzungs-/Auswertungsberechtigung.

Zu entscheiden:

1. Welche Voraussetzungen der einschlägigen Interoperabilitätsregeln sind im
   konkreten Nutzerfall erfüllt, einschließlich rechtmäßiger Nutzung, Erforderlichkeit,
   anderweitig verfügbarer Informationen und Beschränkung auf benötigte Teile?
2. Wie sind technische Zugangskontrolle, Vertragsbedingungen und Umgang mit dem
   proprietären Schlüssel einzuordnen? Gilt die Beurteilung gleichermaßen für die
   Bereitstellung des Werkzeugs und die konkrete Nutzung?
3. Welche Aussagen zur zulässigen APK-Herkunft sind vertretbar? Ein Mirror-Nachweis
   allein belegt weder Authentizität noch eine Berechtigung des Nutzers.
4. Ist der vorgeschlagene Nutzer-/Haftungshinweis wirksam und verständlich,
   insbesondere bei deutschem Recht und zwingender Haftung? Er soll keine
   uneingeschränkte Haftungsfreiheit oder Nutzungserlaubnis behaupten.
5. Ist die beschreibende Verwendung von ZWO/Seestar und der Name „Seestar Studio“
   mit dem sichtbaren Unabhängigkeitshinweis ausreichend abgesichert?

SeestarPys eigene Position und die gesetzlichen Primärquellen sind im
[Interoperabilitätsbericht](ZWO_INTEROPERABILITY_REVIEW.md) verlinkt. Die Position
des Bibliotheksautors wird als dessen Einschätzung behandelt.

## Microsoft

Die kostenlose Community-Lizenz enthält Wege für Individualentwicklung und
OSI-Open-Source-Projekte. Bitte die konkrete Publisher-/Lizenznehmerkonstellation,
Weitergabe älterer unmodifizierter MSVC-DLLs aus Python-/Qt-Wheels, einschlägige
REDIST-Liste und erforderliche Schutzbedingungen für Empfänger bestätigen.
Die GPL-Systembibliotheksausnahme ist komponentenbezogen zu begründen; Microsoft-
Code soll seine eigenen Bedingungen behalten. Eine Runtime-Endnutzerlizenz allein
ist keine Entwickler-Weitergabeerlaubnis. Details: [Microsoft-Prüfung](MICROSOFT_RUNTIME_REVIEW.md).

## Codecs

Der [Codec-Bericht](CODEC_LEGAL_REVIEW.md) enthält DLL-Identität, tatsächliche
Registrierungen und offizielle Programme/Schwellenbedingungen. Bitte klären:

1. Relevante Länder, veröffentlichende Rechtsperson, Stückzahlbegriff, erwarteter
   Vertriebsumfang und etwaige spätere Monetarisierung/Unterstützungsangebote.
2. Anwendbarkeit von AVC-, HEVC-, AAC- und gegebenenfalls AV1/VP9-Ansprüchen auf
   die separate Verbreitung unserer Software, einschließlich möglicher Ausnahmen.
3. Bedeutung bereits lizenzierter Hardware/Windows-Codecs und separat ausgelieferter
   Softwaredecoder. Keine automatische Weiterreichung von Deckung unterstellen.
4. Ob bei einem Nulltarif trotzdem Vereinbarung, Registrierung, Meldungen oder
   andere Bedingungen gelten. Keine Ableitung „bis zur Schwelle lizenzfrei“.
5. Relevanz ungenutzter, aber mitgelieferter Encoder/Decoder und der AVIF/AOM-
   Bildcodec-Funktionalität; sinnvoller Funktionsumfang einer schlankeren Variante.
6. Geltungsbereich, Laufzeit und mögliche Rechte außerhalb der genannten Pools.

Seestar Studio bietet keinen Internet-Videodienst an. OBS-Fensteraufnahme und
Nutzerübertragung durch fremde Dienste sind getrennt zu betrachten.
