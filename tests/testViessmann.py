import unittest
import logging
from pyvcontrol.viControl import viControl
from pyvcontrol.viCommand import viCommand

class MyTestCase(unittest.TestCase):
    def test_readsequence(self):
        vo = viControl()
        vo.initComm()

        for cmd in viCommand.commandset.keys():
            vd = vo.execReadCmd(cmd)
            print(f'{cmd} : {vd.value}')


if __name__ == '__main__':
    logging.basicConfig(filename='testViessmann.log', filemode='w', level=logging.DEBUG)
    unittest.main()
