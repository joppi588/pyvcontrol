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


import unittest

from pyvcontrol import viCommand as c
from pyvcontrol import viControl as v
from pyvcontrol.viData import viData as d
from pyvcontrol.viTelegram import viTelegramException


class testviTelegram(unittest.TestCase):
    def test_readTelegram(self):
        vc = c.viCommand("Anlagentyp")
        vt = v.viTelegram(vc, "read")
        self.assertEqual("4105000100f80402", vt.hex())
        vc = c.viCommand("Warmwassertemperatur")
        vt = v.viTelegram(vc, "read")
        self.assertEqual("41050001010d0216", vt.hex())

    def test_checksumEmpty(self):
        # raise error
        b = bytes(0)
        c = v.viTelegram._checksum_byte(b)
        self.assertEqual(b"\x00", c)

    def test_checksumStartbyte(self):
        # raise error
        c = v.viTelegram._checksum_byte(b"\x42\x41")
        self.assertEqual(b"\x00", c)


class testviTelegram_resp(unittest.TestCase):
    def test_wrongchecksum(self):
        b = bytes.fromhex("4105000100f80201")
        with self.assertRaises(viTelegramException):
            vt = v.viTelegram.from_bytes(b)

    def test_telegramtype(self):
        b = bytes.fromhex("41 05 00 01 01 0d 02 00 00 16")
        vt = v.viTelegram.from_bytes(b)
        self.assertEqual(vt.telegram_mode, "read")
        b = bytes.fromhex("41 05 00 02 01 0d 02 00 00 17")
        vt = v.viTelegram.from_bytes(b)
        self.assertEqual(vt.telegram_mode, "write")
        b = bytes.fromhex("41 05 00 07 01 0d 02 00 00 1c")
        vt = v.viTelegram.from_bytes(b)
        self.assertEqual(vt.telegram_mode, "call")

    def test_telegramtype(self):
        b = bytes.fromhex("41 05 00 01 01 0d 02 00 00 16")
        vt = v.viTelegram.from_bytes(b)
        self.assertEqual(vt.telegram_type, "request")
        b = bytes.fromhex("41 05 01 02 01 0d 02 00 00 18")
        vt = v.viTelegram.from_bytes(b)
        self.assertEqual(vt.telegram_type, "response")
        b = bytes.fromhex("41 05 03 07 01 0d 02 00 00 1f")
        vt = v.viTelegram.from_bytes(b)
        self.assertEqual(vt.telegram_type, "error")

    def test_telegramdata1(self):
        b = bytes.fromhex("41 07 01 01 01 0d 02 65 00 7e")
        vt = v.viTelegram.from_bytes(b)
        vd = d.create(vt.vicmd.unit, vt.payload)
        self.assertEqual(vt.vicmd.unit, "IS10")
        self.assertEqual(vd.value, 10.1)

    def test_telegramdata2(self):
        # 'Read' telegram
        b = bytes.fromhex("41 09 01 01 16 50 04 e4 29 00 00 82")
        vt = v.viTelegram.from_bytes(b)
        vd = d.create(vt.vicmd.unit, vt.payload)
        self.assertEqual("read", vt.telegram_mode)
        self.assertEqual(12, vt.response_length)
        self.assertEqual(vt.vicmd.command_name, "WWwaerme")
        self.assertEqual(vt.vicmd.unit, "IUNON")
        self.assertEqual(vd.value, 10724)

    def test_telegramdata3(self):
        # 'write' telegram
        b = bytes.fromhex("41 09 01 02 16 50 04 76")
        vt = v.viTelegram.from_bytes(b)
        vd = d.create(vt.vicmd.unit, vt.payload)
        self.assertEqual("write", vt.telegram_mode)
        self.assertEqual(8, vt.response_length)
        self.assertEqual(vt.vicmd.command_name, "WWwaerme")
        self.assertEqual(vt.vicmd.unit, "IUNON")


if __name__ == "__main__":
    unittest.main()
