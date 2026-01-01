# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# Copyright 2021-2025 Jochen Schmähling
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
#  Python Module for communication with ViControl heatings using the serial Optolink interface
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
from pyvcontrol.vi_data import viData
from pyvcontrol.vi_telegram import viTelegram, viTelegramError


def test_read_telegram():
    vc = ViCommand("Anlagentyp")
    vt = viTelegram(vc, "read")
    assert vt.hex() == "4105000100f80402"
    vc = ViCommand("Warmwassertemperatur")
    vt = viTelegram(vc, "read")
    assert vt.hex() == "41050001010d0216"


def test_checksum_empty():
    # raise error
    b = bytes(0)
    c = viTelegram._checksum_byte(b)
    assert c == b"\x00"


def test_checksum_startbyte():
    # raise error
    c = viTelegram._checksum_byte(b"\x42\x41")
    assert c == b"\x00"


def test_wrongchecksum():
    b = bytes.fromhex("4105000100f80201")
    with pytest.raises(viTelegramError):
        _ = viTelegram.from_bytes(b)


def test_telegram_mode():
    b = bytes.fromhex("41 05 00 01 01 0d 02 00 00 16")
    vt = viTelegram.from_bytes(b)
    assert vt.telegram_mode == "read"

    b = bytes.fromhex("41 05 00 02 01 0d 02 00 00 17")
    vt = viTelegram.from_bytes(b)
    assert vt.telegram_mode == "write"

    b = bytes.fromhex("41 05 00 07 01 0d 02 00 00 1c")
    vt = viTelegram.from_bytes(b)
    assert vt.telegram_mode == "call"


def test_telegram_type():
    b = bytes.fromhex("41 05 00 01 01 0d 02 00 00 16")
    vt = viTelegram.from_bytes(b)
    assert vt.telegram_type == "request"

    b = bytes.fromhex("41 05 01 02 01 0d 02 00 00 18")
    vt = viTelegram.from_bytes(b)
    assert vt.telegram_type == "response"

    b = bytes.fromhex("41 05 03 07 01 0d 02 00 00 1f")
    vt = viTelegram.from_bytes(b)
    assert vt.telegram_type == "error"


def test_telegramdata1():
    b = bytes.fromhex("41 07 01 01 01 0d 02 65 00 7e")
    vt = viTelegram.from_bytes(b)
    vd = viData.create(vt.vicmd.unit, vt.payload)
    assert vt.vicmd.unit == "IS10"
    assert vd.value == 10.1


def test_telegramdata2():
    # 'Read' telegram
    b = bytes.fromhex("41 09 01 01 16 50 04 e4 29 00 00 82")
    vt = viTelegram.from_bytes(b)
    vd = viData.create(vt.vicmd.unit, vt.payload)
    assert vt.telegram_mode == "read"
    assert vt.response_length == 12
    assert vt.vicmd.command_name == "WWwaerme"
    assert vt.vicmd.unit == "IUNON"
    assert vd.value == 10724


def test_telegramdata3():
    # 'write' telegram
    b = bytes.fromhex("41 09 01 02 16 50 04 76")
    vt = viTelegram.from_bytes(b)
    _ = viData.create(vt.vicmd.unit, vt.payload)
    assert vt.telegram_mode == "write"
    assert vt.response_length == 8
    assert vt.vicmd.command_name == "WWwaerme"
    assert vt.vicmd.unit == "IUNON"
