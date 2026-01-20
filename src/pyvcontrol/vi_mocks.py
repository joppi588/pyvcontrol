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

from __future__ import annotations

from unittest.mock import MagicMock, Mock

from serial import Serial

from pyvcontrol.vi_command import COMMAND_SETS
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

    mock = Mock(spec=Serial, sink=bytearray(0), source=source or bytearray(0), source_cursor=0, is_open=False, **kwargs)
    mock.open.side_effect = lambda: _open(mock)
    mock.close.side_effect = lambda: _close(mock)
    mock.write.side_effect = lambda payload: _write(mock, payload)
    mock.read.side_effect = lambda length: _read(mock, length)

    return mock


def vi_control_mock(vi_command_data: dict[str, ViData] | None = None, **kwargs):
    """Setup Mock replacing ViControl.

    vi_command_data is used as source for read commands and sink for write commands.
    """

    def _enter(mock):
        return mock

    def _exit(mock, exc_type, exc_value, exc_traceback):  # noqa: ARG001
        if exc_type is not None:
            raise exc_type(exc_value)

    def _execute_read_command(mock, command: str):
        return mock.vi_command_data[command]

    def _execute_write_command(mock, command: str, value):
        vc = COMMAND_SETS["WO1C"][command]
        mock.vi_command_data[command] = ViData.create(vc.unit, value)

    mock = MagicMock(spec=ViControl, vi_command_data=vi_command_data or {}, **kwargs)
    mock.execute_read_command.side_effect = lambda command: _execute_read_command(mock, command)
    mock.execute_write_command.side_effect = lambda command, value: _execute_write_command(mock, command, value)
    mock.__enter__.side_effect = lambda: _enter(mock)
    mock.__exit__.side_effect = lambda exc_type, exc_value, exc_traceback: _exit(
        mock, exc_type, exc_value, exc_traceback
    )

    return mock
