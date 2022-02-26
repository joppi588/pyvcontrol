# Communication with Viessmann heating via Optolink interface


![Python Logo](https://www.python.org/static/community_logos/python-logo.png "Sample inline image")

Python package to communicate with Viessmann heatings via the optolink serial interface.
Replacement for vcontrold when using a python environment.

Python package zur Kommunikation mit Viessmann-Heizungen über die Optolink serielle Schnittstelle.
Geeignet um vcontrold zu ersetzen wenn ohnehin mit Python gearbeitet wird.

Neuentwicklung basierend  auf 
-  [SmartHomeNG plugin (Python)][SHNGpyPlugin]
-  [vcontrold][vcontrold]

Motivation:
- Python-Modul um direkt auf die Viessmann-Heizung zugreifen zu können (ohne Umweg über vcontrold)

Einschränkungen:
 - Die Parameter (z.B. Kommandodefinitionen) sind Teil der Klassen und nicht mehr zentral abgelegt.
   Nachteil ist die geringere Anwenderfreundlichkeit - Konfigurationen sollten eigentlich vom Code getrennt sein
    - nur V200WO1C/P300 implementiert. Erweiterung über eine weitere class factory möglich

Beispielcode:
- testViessmann.py: führt einen Lesezugriff für alle definierten Kommandos durch.

[vcontrold]: https://github.com/openv (vcontrold)
[SHNGpyPlugin]: https://github.com/sisamiwe/myplugins/tree/master/viessmann (SmartHomeNG python Plugin)
[packaging guide]: https://packaging.python.org
[distribution tutorial]: https://packaging.python.org/tutorials/packaging-projects/
[src]: https://github.com/
[rst]: http://docutils.sourceforge.net/rst.html
[md]: https://tools.ietf.org/html/rfc7764#section-3.5 "CommonMark variant"
[md use]: https://packaging.python.org/specifications/core-metadata/#description-content-type-optional
