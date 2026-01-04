# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# Copyright 2021-2025 Jochen Schmähling
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
#  Python package for communication with Viessmann heatings using the serial Optolink interface
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

from unittest.mock import MagicMock, Mock

from serial import Serial

from pyvcontrol.vi_command import ViCommand
from pyvcontrol.vi_control import ViControl
from pyvcontrol.vi_data import ViData


class ViSerialMock(Mock):
    """Mock for serial interface, simulating the heating device."""

    def __init__(self, source=None, **kwargs):
        super().__init__(spec=Serial, autospec=True, **kwargs)
        self.sink = bytearray(0)
        self.source = source or bytearray(0)
        self.source_cursor = 0
        self.is_open = False
        self.open = Mock(side_effect=self._open)
        self.close = Mock(side_effect=self._close)
        self.write = Mock(side_effect=self._write)
        self.read = Mock(side_effect=self._read)

    def _open(self):
        self.sink = bytearray(0)
        self.is_open = True

    def _close(self):
        self.is_open = False

    def _write(self, payload):
        self.sink = self.sink + bytearray(payload)
        print(f"received {payload}, in total received {self.sink}")

    def _read(self, length):
        answer = self.source[self.source_cursor : self.source_cursor + length]
        self.source_cursor += length
        return answer


class ViControlMock(MagicMock):
    """Mock ViControl."""

    def __init__(self, vi_data=None):
        super().__init__(spec=ViControl)
        self.vi_data = vi_data or {}
        self.execute_read_command = Mock(side_effect=self._execute_read_command)
        self.execute_write_command = Mock(side_effect=self._execute_write_command)
        self.__enter__.side_effect = self._enter
        self.__exit__.side_effect = self._exit

    def _enter(self):
        return self

    def _exit(self):
        return

    def _execute_read_command(self, command: str):
        return self.vi_data[command]

    def _execute_write_command(self, command: str, value):
        vc = ViCommand.from_name(command)
        self.vi_data[command] = ViData.create(vc.unit, value)
