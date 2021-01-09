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

    def test_readonly(self):
        pass

    def test_writesequence(self):
        # Ändert einen Datensatz und stellt ursprüngl. Wert wieder her
        vo=viControl()
        vo.initComm()
        cmd='RaumsolltempParty'
        v_orig = vo.execReadCmd(cmd).value

        vdw = vo.execWriteCmd(cmd,v_orig+1)
        vdr = vo.execReadCmd(cmd)
        print(f'Read {cmd} : {vdr.value}')
        self.assertEqual(v_orig+1,vdr.value)

        vdw = vo.execWriteCmd(cmd,v_orig)
        vdr = vo.execReadCmd(cmd)
        print(f'Read {cmd} : {vdr.value}')
        self.assertEqual(v_orig,vdr.value)


if __name__ == '__main__':
    logging.basicConfig(filename='testViessmann.log', filemode='w', level=logging.DEBUG)
    unittest.main()
