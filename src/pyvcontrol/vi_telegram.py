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


import logging

from pyvcontrol.vi_command import viCommand

logger = logging.getLogger(name="pyvcontrol")


class viTelegramException(Exception):
    pass


class viTelegram(bytearray):
    # represents a telegram (header, viCommand, payload and checksum)

    # P300 Protokoll (thanks to M.Wenzel, SmartHomeNG plugin)
    #
    # Beispiel
    #
    # Senden        41 5 0 1 55 25 2 82
    # Read Request  -- - - - ----- - --
    #                | | | |   |   |  +------- Prüfsumme (Summe über alley Bytes ohne die 41; [hex]5+0+1+55+25+2 = [dez]5+0+1+(5x16)+5+(2x16)+5+2 = 130dez = 82hex
    #                | | | |   |   +---------- XX Anzahl der Bytes, die in der Antwort erwartet werden
    #                | | | |   +-------------- XX XX 2 byte Adresse der Daten oder Prozedur
    #                | | | +------------------ XX 01 = ReadData, 02 = WriteData, 07 = Function Call
    #                | | +-------------------- XX 00 = Anfrage, 01 = Antwort, 03 = Fehler
    #                | +---------------------- Länge der Nutzdaten (Anzahl der Bytes zwischen dem Telegramm-Start-Byte (0x41) und der Prüfsumme)
    #                +------------------------ Telegramm-Start-Byte
    #
    # Empfangen   :  6 ----------------------- OK (Antwort auf 0x16 0x00 0x00 und auf korrekt empfangene Telegramme)
    #                5 ----------------------- Schnittstelle ist aktiv und wartet auf eine Initialisierung
    #               15 ----------------------- Schnittstelle meldet einen Fehler zurück
    #
    #               41 7 1 1 55 25 2 EF 0 74
    #               -- - - - ----- - ---- --
    #                | | | |   |   |   |   +-- Prüfsumme (Summe über alley Bytes ohne die 41; [hex]7+1+1+55+25+2+EF+0 = [dez]7+1+1+(5x16)+5+(2x16)+5+2+(14*16)+(15*16)+0 = [dez]7+1+1+(80)+5+(32)+5+2+(224)+(15)+0 = 372dez = 1.74hex)
    #                | | | |   |   |   +------ Wert
    #                | | | |   |   +---------- XX Anzahl der Bytes, die in der Antwort erwartet werden
    #                | | | |   +-------------- XX XX 2 byte Adresse der Daten oder Prozedur
    #                | | | +------------------ XX 01 = ReadData, 02 = WriteData, 07 = Function Call
    #                | | +-------------------- XX 00 = Anfrage, 01 = Antwort, 03 = Fehler
    #                | +---------------------- Länge der Nutzdaten (Anzahl der Bytes zwischen dem Telegramm-Start-Byte (0x41) und der Prüfsumme)
    #                +------------------------ Telegramm-Start-Byte

    # Kommunikationsbeispiele
    # Information Kessel Außentemperatur read 2-Byte -60..60 0x5525
    # DATA TX: 41 5 0 1 55 25 2 82
    # DATA RX: 41 7 1 1 55 25 2 EF 0 74 --> 00EF = 239 --> 23.9°C (Faktor 0.1)
    # --> Senden   41 5 0 1 55 25 2 82
    #              -- - - - ----- - --
    #               | | | |   |   |  +-- Prüfsumme (Summe über alley Bytes ohne die 41; [hex]5+0+1+55+25+2 = [dez]5+0+1+(5x16)+5+(2x16)+5+2 = 130dez = 82hex
    #               | | | |   |   +----- XX Anzahl der Bytes, die in der Antwort erwartet werden
    #               | | | |   +--------- XX XX 2 byte Adresse der Daten oder Prozedur
    #               | | | +------------- XX 01 = ReadData, 02 = WriteData, 07 = Function Call
    #               | | +--------------- XX 00 = Anfrage, 01 = Antwort, 03 = Fehler
    #               | +----------------- Länge der Nutzdaten (Anzahl der Bytes zwischen dem Telegramm-Start-Byte (0x41) und der Prüfsumme)
    #               +------------------- Telegramm-Start-Byte
    #
    # --> Empfangen 6 41 7 1 1 55 25 2 EF 0 74
    #               - -- - - - ----- - ---- --
    #               |  | | | |   |   |   |   +-- Prüfsumme (Summe über alley Bytes ohne die 41; [hex]7+1+1+55+25+2+EF+0 = [dez]7+1+1+(5x16)+5+(2x16)+5+2+(14*16)+(15*16)+0 = [dez]7+1+1+(80)+5+(32)+5+2+(224)+(15)+0 = 372dez = 1.74hex)
    #               |  | | | |   |   |   +------ Wert
    #               |  | | | |   |   +---------- XX Anzahl der Bytes, die in der Antwort erwartet werden
    #               |  | | | |   +-------------- XX XX 2 byte Adresse der Daten oder Prozedur
    #               |  | | | +------------------ XX 01 = ReadData, 02 = WriteData, 07 = Function Call
    #               |  | | +-------------------- XX 00 = Anfrage, 01 = Antwort, 03 = Fehler
    #               |  | +---------------------- Länge der Nutzdaten (Anzahl der Bytes zwischen dem Telegramm-Start-Byte (0x41) und der Prüfsumme)
    #               |  +------------------------ Telegramm-Start-Byte
    #               +--------------------------- OK (Antwort auf 0x16 0x00 0x00 und auf korrekt empfangene Telegramme)
    #
    # --> Antwort: 0x00EF = 239 = 23.9°

    # Telegram type
    tTypes = {
        "request": b"\x00",
        "response": b"\x01",
        "error": b"\x03",
    }
    # Telegram mode
    tModes = {"read": b"\x01", "write": b"\x02", "call": b"\x07"}
    tStartByte = b"\x41"

    def __init__(self, vc: viCommand, tMode="Read", tType="Request", payload=bytearray(0)):
        # creates a telegram for sending as a combination of header, viCommand, payload and checksum
        # payload is optional, usually of type viData
        # tType and tMode must be strings or bytes. Be careful when extracting from bytearray b - b[x] will be int not byte!
        self.vicmd = vc
        self.tType = (
            self.tTypes[tType.lower()] if isinstance(tType, str) else tType
        )  # translate to byte or use raw value
        self.tMode = (
            self.tModes[tMode.lower()] if isinstance(tMode, str) else tMode
        )  # translate to byte or use raw value
        self.payload = payload  # TODO: payload length not validated against expected length by command unit
        # TODO: no payload for read commands

        # -- create bytearray representation
        b = self._header() + self.vicmd + self.payload
        super().__init__(b + self._checksum_byte(b))

    def _header(self):
        """Create viTelegram header."""
        # 1 byte - type
        # 1 byte - mode
        #
        # Data length (bytes): type (1), mode (1), command code (x), payload viData (x)
        data_length = 2 + len(self.vicmd) + len(self.payload)
        return self.tStartByte + data_length.to_bytes(1, "big") + self.tType + self.tMode

    @property
    def response_length(self):
        # length of response telegram in bytes
        # 1 - Startbyte
        # 1 - length of data from (excluding) startbyte until (excluding) checksum
        # 1 - type
        # 1 - mode
        # x - command
        # 1 - checksum
        return 4 + self.vicmd.response_length(self.telegram_mode) + 1

    @property
    def telegram_mode(self):
        # returns mode (read, write, function call)
        return next(key for key, value in self.tModes.items() if value == self.tMode)

    @property
    def telegram_type(self):
        # Request/response/Error
        return next(key for key, value in self.tTypes.items() if value == self.tType)

    @classmethod
    def from_bytes(cls, b: bytearray):
        # parses a byte array and returns the corresponding telegram with properties vicmd etc.
        # when parsing a response telegram, the first byte (ACK Acknowledge) must be stripped first
        # Telegram bytes are [0:4]->header, [4:6]->command code, [6]->payload length, [7:-2]-> payload, [-1]:-> checksum
        # header bytes are [0]-> Startbyte, [1]:total value byte length,[2]: type, [3] mode

        # validate checksum
        if b[-1:] != viTelegram._checksum_byte(b[0:-1]):
            raise viTelegramException(
                f"Checksum not valid. Expected {b[-1:]}, Calculated {viTelegram._checksum_byte(b[0:-1])}"
            )
        # validate Startbyte
        if b[0:1] != cls.tStartByte:
            raise viTelegramException("Startbyte not found")

        header = b[0:4]
        logger.debug(
            "Header: %s, tType=%s, tMode=%s, payload=%s",
            header.hex(),
            header[2:3].hex(),
            header[3:4].hex(),
            b[7:-1].hex(),
        )
        vicmd = viCommand._from_bytes(b[4:6])
        vt = viTelegram(vicmd, tType=header[2:3], tMode=header[3:4], payload=b[7:-1])
        return vt

    @classmethod
    def _checksum_byte(cls, packet):
        # checksum is the last byte of the sum of all bytes in packet
        checksum = 0
        if len(packet) == 0:
            logger.error("No bytes received to calculate checksum")
        elif packet[0:1] != cls.tStartByte:
            logger.error("bytes to calculate checksum from does not start with start byte")
        else:
            checksum = sum(packet[1:]) % 256
        return checksum.to_bytes(1, "big")
