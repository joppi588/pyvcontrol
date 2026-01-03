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

Einschränkungen/known issues:
 - Die Parameter (z.B. Kommandodefinitionen) sind hard coded.
 - nur V200WO1C/P300 implementiert. 

Beispielcode / Getting started: example.py: 
 - Liest RaumTempSollParty, erhöht den Wert um eins und stellt den Originalwert wieder her
 - Aufruf mit uv run pyvcontrol-example *)

Installation *)
 - uv add "pyvcontrol @ git+https://github.com/joppi588/pyvcontrol" --tag major.minor.patch
 

Referenzen:
[vcontrold]: https://github.com/openv (vcontrold)
[SHNGpyPlugin]: https://github.com/sisamiwe/myplugins/tree/master/viessmann (SmartHomeNG python Plugin)
[packaging guide]: https://packaging.python.org
[distribution tutorial]: https://packaging.python.org/tutorials/packaging-projects/
[src]: https://github.com/
[rst]: http://docutils.sourceforge.net/rst.html
[md]: https://tools.ietf.org/html/rfc7764#section-3.5 "CommonMark variant"
[md use]: https://packaging.python.org/specifications/core-metadata/#description-content-type-optional

*) Falls uv genutzt wird