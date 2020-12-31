import unittest
import viCommand as v

class testViCommand(unittest.TestCase):
    def test_vicmdfrombytes(self):
        vc=v.viCommand.frombytes(b'\x00\xf8')
        self.assertEqual(vc.cmdname, 'Anlagentyp')

    def test_vicmdnomatch(self):
        with self.assertRaises(Exception):
            vc=v.viCommand.frombytes(b'\xF1\x00')



if __name__ == '__main__':
    unittest.main()
