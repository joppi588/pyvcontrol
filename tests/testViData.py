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
from pyvcontrol.viData import viData as v, viDataException

class viDataTestCaseBA(unittest.TestCase):
    def test_BA04Empty(self):
        #create empty class and check mode
        dBA= v.create('BA')
        self.assertEqual(dBA.value, 'undefiniert') #defaults to mode 'undefiniert'

    def test_BA04raw(self):
        #create class with defined operation mode from raw byte
        dBA=v.create('BA',b'\x04')
        self.assertEqual(dBA.value, 'dauernd reduziert')

    def test_BA04(self):
        #create class with constructor and parameter
        dBA= v.create('BA', 'dauernd reduziert')
        self.assertEqual(dBA,b'\x04')

    def test_BA666Empty(self):
        #test call with non-existent mode
        with self.assertRaises(viDataException):
            v.create('BA',b'\x66\x66')


    def test_BAfoobar(self):
        #test call with non-existent mode
        with self.assertRaises(viDataException):
            v.create('BA', 'foobar')

class viDataTestCaseDT(unittest.TestCase):
    def test_DTempty(self):
        #initialize empty device typt (standard)
        dDT= v.create('DT')
        self.assertEqual(dDT.value, 'unknown')
    def test_DTraw(self):
        #initialize from raw data
        dDT=v.create('DT',b'\x20\x4D')
        self.assertEqual(dDT.value, 'V200WO1C, Protokoll: P300')

    def test_DTstr(self):
        dDT=v.create('DT','unknown')
        self.assertEqual(dDT,b'\x00\x00')

class viDataTestCaseIS10(unittest.TestCase):
    def test_IS10(self):
        dIS10=v.create('IS10',10.15)
        self.assertEqual(dIS10.value, 10.1)

    def test_IS10raw(self):
        dIS10=v.create('IS10',b'e\x00')
        self.assertEqual(dIS10.value, 10.1)

    def test_IS10minus(self):
        f=-9.856
        dIS10=v.create('IS10',f)
        print(f'Hex representation of {f} is {dIS10.hex()}')
        self.assertEqual(dIS10.value, -9.8)

    #TODO add test playing with different len arguments and limit values

class viDataTestCaseIUNON(unittest.TestCase):
    def test_IUNON(self):
        f=415
        dIUNON=v.create('IUNON',f)
        print(f'Hex representation of {f} is {dIUNON.hex()}')
        self.assertEqual(dIUNON.value, f)

    def test_IUNONraw(self):
        dIUNON=v.create('IUNON',b'\x9f\x01')
        self.assertEqual(dIUNON.value, 415)

class viDataTestCaseOO(unittest.TestCase):
    def test_OO(self):
        f='On'
        dOO=v.create('OO',f)
        print(f'Hex representation of {f} is {dOO.hex()}')
        self.assertEqual(dOO.value, f)

    def test_OOraw(self):
        dOO=v.create('OO',b'\x02')
        self.assertEqual(dOO.value, 'On')


if __name__ == '__main__':
    unittest.main()
