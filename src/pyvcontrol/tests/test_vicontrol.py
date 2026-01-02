# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# Copyright 2022-2025 Jochen Schmähling
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
#  Python Module for communication with ViControl heatings using the serial Optolink interface
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

"""Test cases for class ViControl."""

from unittest.mock import patch

import pytest

from pyvcontrol.vi_control import CtrlCode, ViControl, ViControlError
from pyvcontrol.vi_mocks import ViSerialMock


@patch("pyvcontrol.vi_control.ViSerial", return_value=ViSerialMock())
def test_exec_forbidden_write_command(mock_vi_serial):
    mock_vi_serial.return_value.source = CtrlCode.ACKNOWLEDGE + bytes.fromhex("41 07 01 01 01 0d 02 65 00 7e")
    vc = ViControl()
    with pytest.raises(ViControlError):
        vc.execute_write_command("Warmwassertemperatur", 5)


@patch("pyvcontrol.vi_control.ViSerial", return_value=ViSerialMock())
def test_exec_write_command(mock_vi_serial):
    mock_vi_serial.return_value.source = CtrlCode.ACKNOWLEDGE + bytes.fromhex("41 07 01 01 01 0d 02 19 00 7e")
    vc = ViControl()
    vc.execute_write_command("SolltempWarmwasser", 35)


@patch("pyvcontrol.vi_control.ViSerial", return_value=ViSerialMock())
def test_exec_read_command(mock_vi_serial):
    mock_vi_serial.return_value.source = CtrlCode.ACKNOWLEDGE + bytes.fromhex("41 07 01 01 01 0d 02 65 00 7e")
    vc = ViControl()
    data = vc.execute_read_command("Warmwassertemperatur")
    assert data.value == 10.1


@pytest.mark.skip("Function calls not implemented.")
@patch("pyvcontrol.vi_control.ViSerial", return_value=ViSerialMock())
def test_exec_function_call(mock_vi_serial):  # noqa: ARG001
    vc = ViControl()  # noqa: F841


@patch("pyvcontrol.vi_control.ViSerial", return_value=ViSerialMock())
def test_exec_forbidden_function_call(mock_vi_serial):
    mock_vi_serial.return_value.source = CtrlCode.ACKNOWLEDGE + bytes.fromhex("41 07 01 01 01 0d 02 65 00 7e")
    vc = ViControl()
    with pytest.raises(ViControlError):
        vc.execute_function_call("Warmwassertemperatur", 5)
