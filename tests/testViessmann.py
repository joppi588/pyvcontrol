import unittest
import logging
from pyvcontrol.viControl import viControl

class MyTestCase(unittest.TestCase):
    def test_readsequence(self):
        vo = viControl()
        vo.initComm()

        vd = vo.execReadCmd('Aussentemperatur')
        print(f'Aussentemperatur: {vd.value} °C')

        vd = vo.execReadCmd('Warmwassertemperatur')
        print(f'Warmwassertemperatur: {vd.value} °C')

        vd = vo.execReadCmd('Anlagentyp')
        print(f'Anlagentyp: {vd.value}')

        vd = vo.execReadCmd('WWeinmal')
        print(f'Warmwasser einmalig: {vd.value}')

if __name__ == '__main__':
    logging.basicConfig(filename='testVDirekt.log', filemode='w', level=logging.DEBUG)
    unittest.main()
