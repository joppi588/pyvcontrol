import unittest
from pyvcontrol.viCommand import viCommand

class testViCommand(unittest.TestCase):

    def test_vicmdnomatch(self):
        # Commando existiert nicht
        with self.assertRaises(Exception):
            vc=v.viCommand.frombytes(b'\xF1\x00')

    def test_vicmdfrombytes(self):
        vc=viCommand.frombytes(b'\x00\xf8')
        self.assertEqual(vc.cmdname, 'Anlagentyp')

    def test_vicmdAnlagentyp(self):
        vc=viCommand('Anlagentyp')
        self.assertEqual(vc.hex(), '00f802')

    def test_vicmdWWeinmal(self):
        vc=viCommand('WWeinmal')
        self.assertEqual(vc.hex(), 'b02001')

    def test_vicmdAussentemperatur(self):
        vc=viCommand('Aussentemperatur')
        self.assertEqual(vc.hex(), '010102')

    def test_vicmdWarmwassertemperatur(self):
        vc=viCommand('Warmwassertemperatur')
        self.assertEqual(vc.hex(), '010d02')


if __name__ == '__main__':
    unittest.main()
