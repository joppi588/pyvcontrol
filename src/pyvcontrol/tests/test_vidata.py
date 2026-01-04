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

# ruff: noqa: N802,N806
"""Test cases for class ViData."""

import pytest

from pyvcontrol.vi_data import ViData, ViDataError


class Test_ViDataBA:
    """Group tests for data type BA."""

    def test_BAEmpty(self):
        """Create empty class and check mode."""
        dBA = ViData.create("BA")
        assert dBA.value == "OFF"  # defaults to mode 'OFF'

    def test_BA02raw(self):
        """Create class with defined operation mode from raw byte."""
        dBA = ViData.create("BA", b"\x02")
        assert dBA.value == "HEATING_WW"

    def test_BA01(self):
        """Create class with constructor and parameter."""
        dBA = ViData.create("BA", "WW")
        assert dBA == b"\x01"

    def test_BA6666Empty(self):
        """Test call with non-existent mode."""
        with pytest.raises(ViDataError):
            ViData.create("BA", b"\x66\x66")

    def test_BAfoobar(self):
        """Test call with non-existent mode."""
        with pytest.raises(ViDataError):
            ViData.create("BA", "foobar")


class Test_ViDataDT:
    """Group tests for data type DT."""

    def test_DTempty(self):
        """Initialize empty device type (standard)."""
        dDT = ViData.create("DT")
        assert dDT.value == "unknown"

    def test_DTraw(self):
        """Initialize from raw data."""
        dDT = ViData.create("DT", b"\x20\x4d")
        assert dDT.value, "V200WO1C== Protokoll: P300"

    def test_DTstr(self):
        dDT = ViData.create("DT", "unknown")
        assert dDT == b"\x00\x00"


class Test_ViDataIS10:
    """Group tests for data type IS10."""

    def test_IS10(self):
        dIS10 = ViData.create("IS10", 10.15)
        assert dIS10.value == 10.1

    def test_IS10raw(self):
        dIS10 = ViData.create("IS10", b"e\x00")
        assert dIS10.value == 10.1

    def test_IS10minus(self):
        f = -9.856
        dIS10 = ViData.create("IS10", f)
        print(f"Hex representation of {f} is {dIS10.hex()}")
        assert dIS10.value == -9.8

    # TODO add test playing with different len arguments and limit values


class Test_ViDataIUNON:
    """Group tests for data type IUNON."""

    def test_IUNON(self):
        f = 415
        dIUNON = ViData.create("IUNON", f)
        print(f"Hex representation of {f} is {dIUNON.hex()}")
        assert dIUNON.value == f

    def test_IUNONraw(self):
        dIUNON = ViData.create("IUNON", b"\x9f\x01")
        assert dIUNON.value == 415


class Test_ViDataOO:
    """Group tests for data type OO."""

    def test_OO(self):
        f = "On"
        dOO = ViData.create("OO", f)
        print(f"Hex representation of {f} is {dOO.hex()}")
        assert dOO.value == f

    def test_OOraw(self):
        dOO = ViData.create("OO", b"\x02")
        assert dOO.value == "On"

    def test_OO_unknown_value(self):
        with pytest.raises(ViDataError):
            dOO = ViData.create("OO", "foo")  # noqa: F841

    def test_OO_default_value(self):
        dOO = ViData.create("OO")
        assert dOO.value == "Off"


class Test_ViDataEnergy:
    """Group tests for data type Energy."""

    def test_default(self):
        data_energy = ViData.create("F_E")
        assert data_energy.day == 0
        assert data_energy.week == 0
        assert data_energy.year == 2000
        assert data_energy.water_energy == 0
        assert data_energy.heating_energy == 0
        assert data_energy.cooling_energy == 0
        assert data_energy.water_electrical_energy == 0
        assert data_energy.heating_electrical_energy == 0
        assert data_energy.cooling_electrical_energy == 0

    def test_typical_values(self):
        example_data = bytes.fromhex("02 02 16 09 92 03 aa 00 99 00 2d 00 00 00 00 00")

        data_energy = ViData.create("F_E", example_data)
        value_dictionary = data_energy.value
        reference_dictionary = {
            "day": 2,
            "week": 9,
            "year": 2022,
            "heating_energy": 91.4,
            "heating_electrical_energy": 17.0,
            "water_energy": 15.3,
            "water_electrical_energy": 4.5,
            "cooling_energy": 91.4,
            "cooling_electrical_energy": 17.0,
            "total_energy": 91.4 + 15.3 + 91.4,
            "total_electrical_energy": 38.5,
        }

        assert value_dictionary == reference_dictionary

    def test_failed_init(self):
        example_data = 1.2
        with pytest.raises(ViDataError):
            ViData.create("F_E", example_data)
