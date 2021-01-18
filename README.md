# Communication with Viessmann heating via Optolink interface


![Python Logo](https://www.python.org/static/community_logos/python-logo.png "Sample inline image")

Python package to communicate with Viessmann heatings via the optolink serial interface.
It is suitable to replace vcontrold when using a python environment

Python package zur Kommunikation mit Viessmann-Heizungen über die Optolink serielle Schnittstelle.
Geeignet um vcontrold zu ersetzen wenn ohnehin mit Python gearbeitet wird.

Neuentwicklung basierend  auf 
[SmartHomeNG python Plugin]: https://github.com/sisamiwe/myplugins/tree/master/viessmann
[vcontrold]: https://github.com/openv

Motivation:
- Python-Modul um direkt auf die Viessmann-Heizung zugreifen zu können (ohne Umweg über vcontrold)

Einschränkungen:
 - Beta: Nur Basisfunktionen sind getestet
 - Die Parameter (z.B. Kommandodefinitionen) sind jetzt Teil der Klassen und nicht mehr zentral abgelegt.
   Nachteil ist die geringere Anwenderfreundlichkeit - Konfigurationen sollten eigentlich vom Code getrennt sein
   (Allerdings sind die vcontrold-XMLs auch nicht sonderlich gut wartbar)
   Vorteil ist dass Code und Daten jetzt nahe beieinander sind (objektorientierte Programmierung)
 - nur V200WO1C/P300 implementiert. Erweiterung über eine weitere class factory möglich

Beispielcode:
- testViessmann.py: führt einen Lesezugriff für alle definierten Kommandos durch.

[packaging guide]: https://packaging.python.org
[distribution tutorial]: https://packaging.python.org/tutorials/packaging-projects/
[src]: https://github.com/
[rst]: http://docutils.sourceforge.net/rst.html
[md]: https://tools.ietf.org/html/rfc7764#section-3.5 "CommonMark variant"
[md use]: https://packaging.python.org/specifications/core-metadata/#description-content-type-optional
