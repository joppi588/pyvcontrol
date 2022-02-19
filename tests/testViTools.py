import unittest
from unittest.mock import patch
from pyvcontrol.viControl import viControl
from pyvcontrol.viTools import vimonitor
from viControlMock import viControlMock


class testviTools(unittest.TestCase):

    @patch('pyvcontrol.viTools.viControl',return_value=viControlMock())
    def test_monitor(self,mock1):
        vimonitor(['Warmwassertemperatur','VorlauftempSek'])
        self.assertEqual(True, True)  # add assertion here

    @patch('pyvcontrol.viTools.viControl',return_value=viControlMock())
    def test_monitor_unknowncommand(self,mock1):
        vimonitor(['Warmwassertemperatur','Vorlauftemperatur'])
        self.assertEqual(True, True)  # add assertion here

if __name__ == '__main__':
    unittest.main()
