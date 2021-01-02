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


import unittest
from pyvcontrol import viData as v

class viDataTestCaseBT(unittest.TestCase):
    def test_BT04Empty(self):
        #create empty class and
        dBT= v.viDataFactory('BT')
        self.assertEqual(dBT.value, 'undefiniert') #defaults to mode 'undefiniert'

    def test_BT04raw(self):
        dBT=v.viDataFactory('BT',b'\x04')
        self.assertEqual(dBT.value, 'dauernd reduziert')

    def test_BT04(self):
        #create class with constructor and parameter
        dBT= v.viDataFactory('BT', 'dauernd reduziert')
        self.assertEqual(dBT,b'\x04')

    def test_BT666Empty(self):
        #test call with non-existent mode
        with self.assertRaises(v.viDataException):
            v.viDataFactory('BT',b'\x66\x66')


    def test_BTfoobar(self):
        #test call with non-existent mode
        with self.assertRaises(v.viDataException):
            v.viDataFactory('BT', 'foobar')

class viDataTestCaseDT(unittest.TestCase):
    def test_DTempty(self):
        #initialize empty device typt (standard)
        dDT= v.viDataFactory('DT')
        self.assertEqual(dDT.value, 'unknown')
    def test_DTraw(self):
        dDT=v.viDataFactory('DT',b'\x20\x4D')
        self.assertEqual(dDT.value, 'V200WO1C, Protokoll: P300')

    def test_DTstr(self):
        dDT=v.viDataFactory('DT','unknown')
        self.assertEqual(dDT,b'\x00\x00')

class viDataTestCaseIS10(unittest.TestCase):
    def test_IS10(self):
        dIS10=v.viDataFactory('IS10',10.15)
        self.assertEqual(dIS10.value, 10.1)

    def test_IS10raw(self):
        dIS10=v.viDataFactory('IS10',b'e\x00')
        self.assertEqual(dIS10.value, 10.1)

    def test_IS10minus(self):
        f=-9.856
        dIS10=v.viDataFactory('IS10',f)
        print(f'Hex representation of {f} is {dIS10.hex()}')
        self.assertEqual(dIS10.value, -9.8)

    #TODO add test playing with different len arguments and limit values

class viDataTestCaseIUNON(unittest.TestCase):
    def test_IUNON(self):
        f=415
        dIUNON=v.viDataFactory('IUNON',f)
        print(f'Hex representation of {f} is {dIUNON.hex()}')
        self.assertEqual(dIUNON.value, f)

    def test_IUNONraw(self):
        dIUNON=v.viDataFactory('IUNON',b'\x9f\x01')
        self.assertEqual(dIUNON.value, 415)

class viDataTestCaseOO(unittest.TestCase):
    def test_OO(self):
        f='On'
        dOO=v.viDataFactory('OO',f)
        print(f'Hex representation of {f} is {dOO.hex()}')
        self.assertEqual(dOO.value, f)

    def test_OOraw(self):
        dOO=v.viDataFactory('OO',b'\x02')
        self.assertEqual(dOO.value, 'Off')


if __name__ == '__main__':
    unittest.main()
