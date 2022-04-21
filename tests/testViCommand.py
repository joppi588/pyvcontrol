# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# Copyright 2021 Jochen Schmähling
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
#  Python Module for communication with viControl heatings using the serial Optolink interface
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <http://www.gnu.org/licenses/>.
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##

import unittest
from pyvcontrol.viCommand import viCommand,viCommandException


class testViCommand(unittest.TestCase):

    def test_vicmdnomatch(self):
        # Command not existing
        with self.assertRaises(viCommandException):
            vc = viCommand._from_bytes(b'\xF1\x00')
        with self.assertRaises(viCommandException):
            vc = viCommand('foo')

    def test_vicmdfrombytes(self):
        # create command from raw bytes
        vc = viCommand._from_bytes(b'\x00\xf8')
        self.assertEqual(vc.command_name, 'Anlagentyp')

    def test_vicmdAnlagentyp(self):
        # create command from string
        vc = viCommand('Anlagentyp')
        self.assertEqual(vc.hex(), '00f804')

    def test_vicmdWWeinmal(self):
        # create command from string
        vc = viCommand('WWeinmal')
        self.assertEqual(vc.hex(), 'b02001')

    def test_vicmdAussentemperatur(self):
        # create command from string
        vc = viCommand('Aussentemperatur')
        self.assertEqual(vc.hex(), '010102')

    def test_vicmdWarmwassertemperatur(self):
        # create command from string
        vc = viCommand('Warmwassertemperatur')
        self.assertEqual(vc.hex(), '010d02')


if __name__ == '__main__':
    unittest.main()
