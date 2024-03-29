# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# Copyright 2021-2022 Jochen Schmähling
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

# Provides a mock class to simulate the behavior of viControl class on a machine not connected to Viessmann
# Usage: @patch('pyvcontrol.viTools.viControl', return_value=viControlMock())


from pyvcontrol.viData import viData
from pyvcontrol.viCommand import viCommand
import random


class viControlMock:
    def initialize_communication(self):
        return True

    def execute_read_command(self, cmdName):
        vc = viCommand(cmdName)
        return viData.create('IUNON', random.randint(0, 50))

    def execute_write_command(self, cmdName, value):
        vc = viCommand(cmdName)
        return None
