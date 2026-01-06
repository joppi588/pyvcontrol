# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# Copyright 2022-2025 Jochen Schmähling
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

"""Test cases for class ViControl."""

import contextlib
import re
from unittest.mock import patch

import pytest
from serial import SerialException

from pyvcontrol.vi_command import ViCommandError
from pyvcontrol.vi_control import CtrlCode, ViConnectionError, ViControl
from pyvcontrol.vi_mocks import vi_serial_mock


@pytest.mark.parametrize(
    "serial_in,serial_out",
    [(CtrlCode.NOT_INIT, CtrlCode.SYNC_CMD), (CtrlCode.ERROR, CtrlCode.RESET_CMD), (b"\x04", CtrlCode.RESET_CMD)],
)
def test_vicontrol_init_behaviour(serial_in, serial_out):
    # GIVEN Serial interface returning a non-acknowledge code
    # WHEN Communication is initialized
    # THEN An error is raised, control codes are written
    init_retries = 3
    mock = vi_serial_mock(source=serial_in * init_retries)
    with (
        patch("pyvcontrol.vi_control.Serial", return_value=mock),
        pytest.raises(ViConnectionError, match=r"Could not initialize communication\."),
        ViControl(init_retries=init_retries) as vc,
    ):
        vc._initialize_communication()
    assert mock.sink == serial_out * init_retries


@pytest.mark.parametrize("command_name,allowed_access", [("Warmwassertemperatur", "read")])
def test_exec_forbidden_write_command(command_name, allowed_access):
    mock = vi_serial_mock(source=CtrlCode.ACKNOWLEDGE)
    with (
        patch("pyvcontrol.vi_control.Serial", return_value=mock),
        ViControl() as vc,
        pytest.raises(ViCommandError, match=re.escape(f"Command {command_name} only allows {allowed_access} access.")),
    ):
        vc.execute_write_command(command_name, 5)


def test_exec_write_command():
    mock = vi_serial_mock(source=CtrlCode.ACKNOWLEDGE * 2 + bytes.fromhex("41 07 01 01 01 0d 02 19 00 7e"))
    with patch("pyvcontrol.vi_control.Serial", return_value=mock), ViControl() as vc:
        vc.execute_write_command("SolltempWarmwasser", 35)


def test_exec_read_command():
    mock = vi_serial_mock(source=CtrlCode.ACKNOWLEDGE * 2 + bytes.fromhex("41 07 01 01 01 0d 02 65 00 7e"))
    with patch("pyvcontrol.vi_control.Serial", return_value=mock), ViControl() as vc:
        data = vc.execute_read_command("Warmwassertemperatur")
    assert data.value == 10.1


@pytest.mark.skip("Function calls not implemented.")
def test_exec_function_call():
    with ViControl():
        pass


def test_exec_forbidden_function_call():
    mock = vi_serial_mock(source=CtrlCode.ACKNOWLEDGE + bytes.fromhex("41 07 01 01 01 0d 02 65 00 7e"))
    with patch("pyvcontrol.vi_control.Serial", return_value=mock), pytest.raises(ViCommandError), ViControl() as vc:
        vc.execute_function_call("Warmwassertemperatur", 5)


def test_failed_open_lock_release():
    # GIVEN A ViControl object, ViControl context
    # WHEN Serial.open fails
    # THEN The lock is released

    class SerialMock:
        def open():
            raise SerialException

    with patch("pyvcontrol.vi_control.Serial", return_value=vi_serial_mock()):
        vc1 = ViControl()

    with (
        contextlib.suppress(ViConnectionError),
        patch("pyvcontrol.vi_control.Serial", return_value=SerialMock()),
        ViControl(),
    ):
        pytest.fail("Context shall not be entered")

    assert not vc1._viessmann_lock.locked()


@patch("pyvcontrol.vi_control.Serial", new=vi_serial_mock())
def test_vi_control_locked():
    # GIVEN A ViControl object with acquired lock
    # WHEN A second ViControl object tries to init
    # THEN Abort due to timeout. Still locked.
    vc1 = ViControl()
    vc1._viessmann_lock.acquire()

    with pytest.raises(ViConnectionError, match=r"Could not acquire lock, aborting\."), ViControl(lock_timeout=0.1):
        pytest.fail("Context shall not be entered")
    assert vc1._viessmann_lock.locked()
