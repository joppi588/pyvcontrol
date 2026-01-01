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


import pytest

from pyvcontrol.viCommand import viCommand, viCommandException


def test_vicommand_nomatch():
    # Command not existing
    with pytest.raises(viCommandException):
        _ = viCommand._from_bytes(b"\xf1\x00")
    with pytest.raises(viCommandException):
        _ = viCommand("foo")


def test_vicommand_frombytes():
    # create command from raw bytes
    vc = viCommand._from_bytes(b"\x00\xf8")
    assert vc.command_name == "Anlagentyp"


def test_vicommand_anlagentyp():
    # create command from string
    vc = viCommand("Anlagentyp")
    assert vc.hex() == "00f804"


def test_vicommand_wweinmal():
    # create command from string
    vc = viCommand("WWeinmal")
    assert vc.hex() == "b02001"


def test_vicommand_aussentemperatur():
    # create command from string
    vc = viCommand("Aussentemperatur")
    assert vc.hex() == "010102"


def test_vicommand_warmwassertemperatur():
    # create command from string
    vc = viCommand("Warmwassertemperatur")
    assert vc.hex() == "010d02"


def test_vicommand_betriebsmodus():
    # Given: When: Then: Correct viData is returned
    vc = viCommand("Betriebsmodus")
    assert vc.unit == "BA"
