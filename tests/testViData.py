# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# Copyright 2021 Jochen Schmähling
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

# test cases for class viData

import unittest
from pyvcontrol.viData import viData as vd, viDataException


class viDataTestCaseBA(unittest.TestCase):
    def test_BA04Empty(self):
        # create empty class and check mode
        dBA = vd.create('BA')
        self.assertEqual(dBA.value, 'undefiniert')  # defaults to mode 'undefiniert'

    def test_BA04raw(self):
        # create class with defined operation mode from raw byte
        dBA = vd.create('BA', b'\x04')
        self.assertEqual(dBA.value, 'dauernd reduziert')

    def test_BA04(self):
        # create class with constructor and parameter
        dBA = vd.create('BA', 'dauernd reduziert')
        self.assertEqual(dBA, b'\x04')

    def test_BA666Empty(self):
        # test call with non-existent mode
        with self.assertRaises(viDataException):
            vd.create('BA', b'\x66\x66')

    def test_BAfoobar(self):
        # test call with non-existent mode
        with self.assertRaises(viDataException):
            vd.create('BA', 'foobar')


class viDataTestCaseDT(unittest.TestCase):
    def test_DTempty(self):
        # initialize empty device type (standard)
        dDT = vd.create('DT')
        self.assertEqual(dDT.value, 'unknown')

    def test_DTraw(self):
        # initialize from raw data
        dDT = vd.create('DT', b'\x20\x4D')
        self.assertEqual(dDT.value, 'V200WO1C, Protokoll: P300')

    def test_DTstr(self):
        dDT = vd.create('DT', 'unknown')
        self.assertEqual(dDT, b'\x00\x00')


class viDataTestCaseIS10(unittest.TestCase):
    def test_IS10(self):
        dIS10 = vd.create('IS10', 10.15)
        self.assertEqual(dIS10.value, 10.1)

    def test_IS10raw(self):
        dIS10 = vd.create('IS10', b'e\x00')
        self.assertEqual(dIS10.value, 10.1)

    def test_IS10minus(self):
        f = -9.856
        dIS10 = vd.create('IS10', f)
        print(f'Hex representation of {f} is {dIS10.hex()}')
        self.assertEqual(dIS10.value, -9.8)

    # TODO add test playing with different len arguments and limit values


class viDataTestCaseIUNON(unittest.TestCase):
    def test_IUNON(self):
        f = 415
        dIUNON = vd.create('IUNON', f)
        print(f'Hex representation of {f} is {dIUNON.hex()}')
        self.assertEqual(dIUNON.value, f)

    def test_IUNONraw(self):
        dIUNON = vd.create('IUNON', b'\x9f\x01')
        self.assertEqual(dIUNON.value, 415)


class viDataTestCaseOO(unittest.TestCase):
    def test_OO(self):
        f = 'On'
        dOO = vd.create('OO', f)
        print(f'Hex representation of {f} is {dOO.hex()}')
        self.assertEqual(dOO.value, f)

    def test_OOraw(self):
        dOO = vd.create('OO', b'\x02')
        self.assertEqual(dOO.value, 'On')

    def test_OO_unknown_value(self):
        with self.assertRaises(viDataException):
            dOO = vd.create('OO', 'foo')

    def test_OO_default_value(self):
        dOO = vd.create('OO')
        self.assertEqual(dOO.value, 'Off')


class viDataTestCaseEnergy(unittest.TestCase):
    def test_default(self):
        data_energy = vd.create('F_E')
        self.assertEqual(data_energy.day, 0)
        self.assertEqual(data_energy.week, 0)
        self.assertEqual(data_energy.year, 2000)
        self.assertEqual(data_energy.water_energy, 0)
        self.assertEqual(data_energy.heating_energy, 0)
        self.assertEqual(data_energy.cooling_energy, 0)
        self.assertEqual(data_energy.water_electrical_energy, 0)
        self.assertEqual(data_energy.heating_electrical_energy, 0)
        self.assertEqual(data_energy.cooling_electrical_energy, 0)

    def test_typical_values(self):
        example_data = bytes.fromhex('02 02 16 09 92 03 aa 00 99 00 2d 00 00 00 00 00')

        data_energy = vd.create('F_E', example_data)
        value_dictionary = data_energy.value
        reference_dictionary = {
            'day': 2,
            'week': 9,
            'year': 2022,
            'heating_energy': 91.4,
            'heating_electrical_energy': 17.0,
            'water_energy': 15.3,
            'water_electrical_energy': 4.5,
            'cooling_energy': 91.4,
            'cooling_electrical_energy': 17.0,
            'total_energy': 91.4 + 15.3 + 91.4,
            'total_electrical_energy': 38.5,
        }

        self.assertEqual(value_dictionary, reference_dictionary)

    def test_failed_init(self):
        example_data = 1.2
        with self.assertRaises(viDataException):
            vd.create('F_E', example_data)


if __name__ == '__main__':
    unittest.main()
