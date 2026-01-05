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

from unittest.mock import Mock

from serial import Serial

from pyvcontrol.vi_command import ViCommand
from pyvcontrol.vi_control import ViControl
from pyvcontrol.vi_data import ViData


def vi_serial_mock(source=None, **kwargs):
    """Create mock for serial interface, simulating the heating device."""

    def _open(mock):
        mock.sink = bytearray(0)
        mock.is_open = True

    def _close(mock):
        mock.is_open = False

    def _write(mock, payload):
        mock.sink = mock.sink + bytearray(payload)
        print(f"received {payload}, in total received {mock.sink}")

    def _read(mock, length):
        answer = mock.source[mock.source_cursor : mock.source_cursor + length]
        mock.source_cursor += length
        return answer

    mock = Mock(spec=Serial, **kwargs)

    mock.sink = bytearray(0)
    mock.source = source or bytearray(0)
    mock.source_cursor = 0
    mock.is_open = False
    mock.open.side_effect = lambda: _open(mock)
    mock.close.side_effect = lambda: _close(mock)
    mock.write.side_effect = lambda payload: _write(mock, payload)
    mock.read.side_effect = lambda length: _read(mock, length)

    return mock


def vi_control_mock(vi_data=None, **kwargs):
    """Mock ViControl."""

    def _enter(mock):
        return mock

    def _exit(mock):  # noqa: ARG001
        return

    def _execute_read_command(mock, command: str):
        return mock.vi_data[command]

    def _execute_write_command(mock, command: str, value):
        vc = ViCommand.from_name(command)
        mock.vi_data[command] = ViData.create(vc.unit, value)

    mock = Mock(spec=ViControl, **kwargs)
    mock.vi_data = vi_data or {}
    mock.execute_read_command.side_effect = lambda command: _execute_read_command(mock, command)
    mock.execute_write_command.side_effect = lambda command, value: _execute_write_command(mock, command, value)
    mock.__enter__.side_effect = lambda: _enter(mock)
    mock.__exit__.side_effect = lambda: _exit(mock)
