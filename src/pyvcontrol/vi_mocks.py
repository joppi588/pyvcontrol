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
"""Mocks for pyvcontrol objects."""

from unittest.mock import NonCallableMock

from pyvcontrol.vi_command import viCommand
from pyvcontrol.vi_control import control_set, viControl
from pyvcontrol.vi_data import viData


class ViSerialMock(NonCallableMock):
    """Mock for serial interface."""

    def __init__(self):
        super().__init__(spec=viControl)
        self._connected = False
        self._control_set = control_set
        self._serial_port = ""
        self._serial = []
        self.sink = bytearray(0)
        self.source = bytearray(0)
        self.source_cursor = 0

    def connect(self):
        self._connected = True
        self.sink = bytearray(0)

    def disconnect(self):
        self._connected = False

    def send(self, payload):
        self.sink = self.sink + bytearray(payload)
        print(f"received {payload}, in total received {self.sink}")

    def read(self, length):
        answer = self.source[self.source_cursor : self.source_cursor + length]
        self.source_cursor += length
        return answer


class ViControlMock(NonCallableMock):
    def __init__(self, vi_data=None):
        super().__init__(spec=viControl)
        self.vi_data = vi_data or {}
        self.initialize_communication.side_effect = self._initialize_communication
        self.execute_read_command.side_effect = self._execute_read_command
        self.execute_write_command.side_effect = self._execute_write_command

    def _initialize_communication(self):
        return True

    def _execute_read_command(self, command: str):
        return self.vi_data[command]

    def _execute_write_command(self, command: str, value):
        vc = viCommand(command)
        self.vi_data[command] = viData.create(vc.unit, value)
