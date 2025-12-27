# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# Copyright 2021-2025 Jochen Schmähling
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

# Tests the connection to Viessmann. Needs a physical connection

import logging
import unittest

from pyvcontrol.viCommand import viCommand
from pyvcontrol.viControl import viControl


class MyTestCase(unittest.TestCase):
    def test_readsequence(self):
        vo = viControl()
        vo.initialize_communication()

        for cmd in viCommand.command_set.keys():
            vd = vo.execReadCmd(cmd)
            print(f"{cmd} : {vd.value}")

    def test_readonly(self):
        pass

    def test_writesequence(self):
        # Ändert einen Datensatz und stellt ursprüngl. Wert wieder her
        vo = viControl()
        vo.initialize_communication()
        cmd = "RaumsolltempParty"
        v_orig = vo.execReadCmd(cmd).value

        vdw = vo.execWriteCmd(cmd, v_orig + 1)
        vdr = vo.execReadCmd(cmd)
        print(f"Read {cmd} : {vdr.value}")
        self.assertEqual(v_orig + 1, vdr.value)

        vdw = vo.execWriteCmd(cmd, v_orig)
        vdr = vo.execReadCmd(cmd)
        print(f"Read {cmd} : {vdr.value}")
        self.assertEqual(v_orig, vdr.value)


if __name__ == "__main__":
    logging.basicConfig(filename="testViessmann.log", filemode="w", level=logging.DEBUG)
    unittest.main()
