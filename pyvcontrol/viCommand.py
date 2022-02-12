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


import logging


class viCommandException(Exception):
    pass


class viCommand(bytearray):
    # the commands
    # viCommand object value is a bytearray of addr and len

    # TODO: statt 'write':False besser mode:rw/w verwenden

    commandset = {
        # All Parameters are tested and working on Vitocal 200S WO1C (Baujahr 2019)

        # ------ Statusinfos (read only) ------

        # Warmwasser: Warmwassertemperatur oben (0..95)
        'Warmwassertemperatur': {'addr': '010d', 'len': 2, 'unit': 'IS10', 'write': False},

        # Aussentemperatur (-40..70)
        'Aussentemperatur': {'addr': '0101', 'len': 2, 'unit': 'IS10', 'write': False},

        # Heizkreis HK1: Vorlauftemperatur Sekundaer 1 (0..95)
        'VorlauftempSek': {'addr': '0105', 'len': 2, 'unit': 'IS10', 'write': False},

        # Ruecklauftemperatur Sekundaer 1 (0..95)
        'RuecklauftempSek': {'addr': '0106', 'len': 2, 'unit': 'IS10', 'write': False},

        # Sekundaerpumpe [%] (including one status byte)
        'Sekundaerpumpe': {'addr': 'B421', 'len': 2, 'unit': 'IUNON', 'write': False},

        # Verdichter [%] (including one status byte)
        'Verdichter': {'addr': 'B423', 'len': 2, 'unit': 'IUNON', 'write': False},

        # Anlagentyp (muss 204D sein)
        'Anlagentyp': {'addr': '00F8', 'len': 2, 'unit': 'DT', 'write': False},

        # --------- Menüebene -------

        # getManuell / setManuell -- 0 = normal, 1 = manueller Heizbetrieb, 2 = 1x Warmwasser auf Temp2
        'WWeinmal': {'addr': 'B020', 'len': 1, 'unit': 'OO', 'write': True},

        # Warmwassersolltemperatur (10..60 (95))
        'SolltempWarmwasser': {'addr': '6000', 'len': 2, 'unit': 'IS10', 'write': True, 'min_value': 10,
                               'max_value': 60},

        # --------- Codierebene 2 ---------

        # Hysterese Vorlauf ein: Verdichter schaltet im Heizbetrieb ein
        'Hysterese_Vorlauf_ein': {'addr': '7304', 'len': 2, 'unit': 'IU10', 'write': True},

        # Hysterese Vorlauf aus: Verdichter schaltet im Heizbetrieb ab
        'Hysterese_Vorlauf_aus': {'addr': '7313', 'len': 2, 'unit': 'IU10', 'write': True}


    }

    def __init__(self, cmdname):
        # FIXME: uniform naming of private and public properties
        # init object using the attributes of the chosen command
        try:
            cs = self.commandset[cmdname]
        except:
            raise viCommandException(f'Unknown command {cmdname}')
        self.__cmdcode__ = cs['addr']
        self.__valuebytes__ = cs['len']
        self.unit = cs['unit']
        self.write = cs['write']
        self.cmdname = cmdname

        # create bytearray representation
        b = bytes.fromhex(self.__cmdcode__) + self.__valuebytes__.to_bytes(1, 'big')
        super().__init__(b)

    @classmethod
    def frombytes(cls, b: bytearray):
        # FIXME Rename the "fromxxx" methods to "from_xxx" similar to int.from_bytes
        # create command from addr given as byte
        # only the first two bytes of b are evaluated
        try:
            logging.debug(f'Convert {b.hex()} to command')
            cmdname = next(key for key, value in cls.commandset.items() if value['addr'].lower() == b[0:2].hex())
        except:
            raise viCommandException(f'No Command matching {b[0:2].hex()}')
        return viCommand(cmdname)

    def __responselen__(self, mode='read'):
        # returns the number of bytes in the response
        # request_response:
        # 2 'addr'
        # 1 'Anzahl der Bytes des Wertes'
        # x 'Wert'
        if mode.lower() == 'read':
            return 3 + self.__valuebytes__
        else:
            # in write mode the written values are not returned
            return 3
