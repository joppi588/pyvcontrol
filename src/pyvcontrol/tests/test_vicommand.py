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


import pytest

from pyvcontrol.vi_command import ViCommand


def test_vicommand_nomatch(commands_wo1c):
    """Command not existing."""
    with pytest.raises(KeyError):
        _ = commands_wo1c[b"\xf1\x00"]
    with pytest.raises(KeyError):
        _ = commands_wo1c["foo"]


def test_vicommand_raw():
    """Create a raw command with default values."""
    vc = ViCommand(address="00F8", value_bytes=2, unit="IUNON")
    assert vc.address == b"\x00\xf8"


def test_vicommand_frombytes(commands_wo1c):
    """Create command from raw bytes."""
    vc = commands_wo1c[b"\x00\xf8"]
    assert vc.command_name == "Anlagentyp"


def test_vicommand_anlagentyp(commands_wo1c):
    """Create command from string."""
    vc = commands_wo1c["Anlagentyp"]
    assert vc.hex() == "00f804"


def test_vicommand_wweinmal(commands_wo1c):
    """Create command from string."""
    vc = commands_wo1c["WWeinmal"]
    assert vc.hex() == "b02001"


def test_vicommand_aussentemperatur(commands_wo1c):
    """Create command from string."""
    vc = commands_wo1c["Aussentemperatur"]
    assert vc.hex() == "010102"


def test_vicommand_warmwassertemperatur(commands_wo1c):
    """Create command from string."""
    vc = commands_wo1c["Warmwassertemperatur"]
    assert vc.hex() == "010d02"


def test_vicommand_betriebsmodus(commands_wo1c):
    """Given: When: Then: Correct ViData is returned."""
    vc = commands_wo1c["Betriebsmodus"]
    assert vc.unit == "BA"
