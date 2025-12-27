# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# Copyright 2022 Jochen Schmähling
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

# test cases for class viControl

import unittest
from unittest.mock import patch
from pyvcontrol.viControl import viControl, viControlException, control_set, ctrlcode


class MockViSerial:

    def __init__(self):
        self._connected = False
        self._control_set = control_set
        self._serial_port = ''
        self._serial = []
        self.sink = bytearray(0)
        self.source = bytearray(0)
        self.source_cursor = 0

    def connect(self):
        self._connected = True
        self.sink = bytearray(0)

    def disconnect(self):
        self._connected = False

    def send(self, payload):
        self.sink = self.sink + bytearray(payload)
        print(f"received {payload}, in total received {self.sink}")

    def read(self, length):
        answer = self.source[self.source_cursor:self.source_cursor + length]
        self.source_cursor += length
        return answer


class TestViControl(unittest.TestCase):

    @patch('pyvcontrol.viControl.viSerial', return_value=MockViSerial())
    def test_exec_forbidden_write_command(self, mock1):
        mock1.return_value.source = ctrlcode['acknowledge'] + bytes.fromhex('41 07 01 01 01 0d 02 65 00 7e')
        vc = viControl()
        with self.assertRaises(viControlException):
            vc.execute_write_command('Warmwassertemperatur', 5)

    @patch('pyvcontrol.viControl.viSerial', return_value=MockViSerial())
    def test_exec_write_command(self, mock1):
        mock1.return_value.source = ctrlcode['acknowledge'] + bytes.fromhex('41 07 01 01 01 0d 02 19 00 7e')
        vc = viControl()
        vc.execute_write_command('SolltempWarmwasser', 35)

    @patch('pyvcontrol.viControl.viSerial', return_value=MockViSerial())
    def test_exec_read_command(self, mock1):
        mock1.return_value.source = ctrlcode['acknowledge'] + bytes.fromhex('41 07 01 01 01 0d 02 65 00 7e')
        vc = viControl()
        data = vc.execute_read_command('Warmwassertemperatur')
        self.assertEqual(data.value, 10.1)

    @patch('pyvcontrol.viControl.viSerial', return_value=MockViSerial())
    def test_exec_function_call(self, mock1):
        vc = viControl()
        self.assertFalse(True)

    @patch('pyvcontrol.viControl.viSerial', return_value=MockViSerial())
    def test_exec_forbidden_function_call(self, mock1):
        mock1.return_value.source = ctrlcode['acknowledge'] + bytes.fromhex('41 07 01 01 01 0d 02 65 00 7e')
        vc = viControl()
        with self.assertRaises(viControlException):
            vc.execute_function_call('Warmwassertemperatur', 5)
