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

"""Test cases for class viData."""

import pytest

from pyvcontrol.viData import viData as vd
from pyvcontrol.viData import viDataException


class viDataTestCaseBA:
    def test_BAEmpty():
        # create empty class and check mode
        dBA = vd.create("BA")
        assert dBA.value == "OFF"  # defaults to mode 'OFF'

    def test_BA02raw():
        # create class with defined operation mode from raw byte
        dBA = vd.create("BA", b"\x02")
        assert dBA.value == "HEATING_WW"

    def test_BA01():
        # create class with constructor and parameter
        dBA = vd.create("BA", "WW")
        assert dBA == b"\x01"

    def test_BA6666Empty():
        # test call with non-existent mode
        with pytest.raises(viDataException):
            vd.create("BA", b"\x66\x66")

    def test_BAfoobar():
        # test call with non-existent mode
        with pytest.raises(viDataException):
            vd.create("BA", "foobar")


class viDataTestCaseDT:
    def test_DTempty():
        # initialize empty device type (standard)
        dDT = vd.create("DT")
        assert dDT.value == "unknown"

    def test_DTraw():
        # initialize from raw data
        dDT = vd.create("DT", b"\x20\x4d")
        assert dDT.value, "V200WO1C== Protokoll: P300"

    def test_DTstr():
        dDT = vd.create("DT", "unknown")
        assert dDT == b"\x00\x00"


class viDataTestCaseIS10:
    def test_IS10():
        dIS10 = vd.create("IS10", 10.15)
        assert dIS10.value == 10.1

    def test_IS10raw():
        dIS10 = vd.create("IS10", b"e\x00")
        assert dIS10.value == 10.1

    def test_IS10minus():
        f = -9.856
        dIS10 = vd.create("IS10", f)
        print(f"Hex representation of {f} is {dIS10.hex()}")
        assert dIS10.value == -9.8

    # TODO add test playing with different len arguments and limit values


class viDataTestCaseIUNON:
    def test_IUNON():
        f = 415
        dIUNON = vd.create("IUNON", f)
        print(f"Hex representation of {f} is {dIUNON.hex()}")
        assert dIUNON.value == f

    def test_IUNONraw():
        dIUNON = vd.create("IUNON", b"\x9f\x01")
        assert dIUNON.value == 415


class viDataTestCaseOO:
    def test_OO():
        f = "On"
        dOO = vd.create("OO", f)
        print(f"Hex representation of {f} is {dOO.hex()}")
        assert dOO.value == f

    def test_OOraw():
        dOO = vd.create("OO", b"\x02")
        assert dOO.value == "On"

    def test_OO_unknown_value():
        with pytest.raises(viDataException):
            dOO = vd.create("OO", "foo")  # noqa: F841

    def test_OO_default_value():
        dOO = vd.create("OO")
        assert dOO.value == "Off"


class viDataTestCaseEnergy:
    def test_default():
        data_energy = vd.create("F_E")
        assert data_energy.day == 0
        assert data_energy.week == 0
        assert data_energy.year == 2000
        assert data_energy.water_energy == 0
        assert data_energy.heating_energy == 0
        assert data_energy.cooling_energy == 0
        assert data_energy.water_electrical_energy == 0
        assert data_energy.heating_electrical_energy == 0
        assert data_energy.cooling_electrical_energy == 0

    def test_typical_values():
        example_data = bytes.fromhex("02 02 16 09 92 03 aa 00 99 00 2d 00 00 00 00 00")

        data_energy = vd.create("F_E", example_data)
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

    def test_failed_init():
        example_data = 1.2
        with pytest.raises(viDataException):
            vd.create("F_E", example_data)
