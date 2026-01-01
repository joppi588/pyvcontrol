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

logger = logging.getLogger(name="pyvcontrol")

ACCESS_MODE = "access_mode"
UNIT = "unit"
LENGTH = "length"
ADDRESS = "address"

VITOCAL_WO1C = {
    # All Parameters are tested and working on Vitocal 200S WO1C (Baujahr 2019)
    # ------ Statusinfos (read only) ------
    # Warmwasser: Warmwassertemperatur oben (0..95)
    "Warmwassertemperatur": {ADDRESS: "010d", LENGTH: 2, UNIT: "IS10"},
    # Aussentemperatur (-40..70)
    "Aussentemperatur": {ADDRESS: "0101", LENGTH: 2, UNIT: "IS10"},
    # Heizkreis HK1: Vorlauftemperatur Sekundaer 1 (0..95)
    "VorlauftempSek": {ADDRESS: "0105", LENGTH: 2, UNIT: "IS10"},
    # Ruecklauftemperatur Sekundaer 1 (0..95)
    "RuecklauftempSek": {ADDRESS: "0106", LENGTH: 2, UNIT: "IS10"},
    # Sekundaerpumpe [%] (including one status byte)
    "Sekundaerpumpe": {ADDRESS: "B421", LENGTH: 2, UNIT: "IUNON"},
    # Faktor Energiebilanz(1 = 0.1kWh, 10 = 1kWh, 100 = 10kWh)
    "FaktorEnergiebilanz": {ADDRESS: "163F", LENGTH: 1, UNIT: "IUNON"},
    # Heizwärme  "Heizbetrieb", Verdichter 1
    "Heizwaerme": {ADDRESS: "1640", LENGTH: 4, UNIT: "IUNON"},
    # Elektroenergie "Heizbetrieb", Verdichter 1
    "Heizenergie": {ADDRESS: "1660", LENGTH: 4, UNIT: "IUNON"},
    # Heizwärme  "WW-Betrieb", Verdichter 1
    "WWwaerme": {ADDRESS: "1650", LENGTH: 4, UNIT: "IUNON"},
    # Elektroenergie "WW-Betrieb", Verdichter 1
    "WWenergie": {ADDRESS: "1670", LENGTH: 4, UNIT: "IUNON"},
    # Verdichter [%] (including one status byte)
    "Verdichter": {ADDRESS: "B423", LENGTH: 4, UNIT: "IUNON"},
    # Druck Sauggas [bar] (including one status byte) - Kühlmittel
    "DruckSauggas": {ADDRESS: "B410", LENGTH: 3, UNIT: "IS10"},
    # Druck Heissgas [bar] (including one status byte)- Kühlmittel
    "DruckHeissgas": {ADDRESS: "B411", LENGTH: 3, UNIT: "IS10"},
    # Temperatur Sauggas [bar] (including one status byte)- Kühlmittel
    "TempSauggas": {ADDRESS: "B409", LENGTH: 3, UNIT: "IS10"},
    # Temperatur Heissgas [bar] (including one status byte)- Kühlmittel
    "TempHeissgas": {ADDRESS: "B40A", LENGTH: 3, UNIT: "IS10"},
    # Anlagentyp (muss 204D sein)
    "Anlagentyp": {ADDRESS: "00F8", LENGTH: 4, UNIT: "DT"},
    # --------- Menüebene -------
    # Betriebsmodus
    "Betriebsmodus": {ADDRESS: "B000", LENGTH: 1, UNIT: "BA", ACCESS_MODE: "write"},
    # getManuell / setManuell -- 0 = normal, 1 = manueller Heizbetrieb, 2 = 1x Warmwasser auf Temp2
    "WWeinmal": {ADDRESS: "B020", LENGTH: 1, UNIT: "OO", ACCESS_MODE: "write"},
    # Warmwassersolltemperatur (10..60 (95))
    "SolltempWarmwasser": {
        ADDRESS: "6000",
        LENGTH: 2,
        UNIT: "IS10",
        ACCESS_MODE: "write",
        "min_value": 10,
        "max_value": 60,
    },
    # --------- Codierebene 2 ---------
    # Hysterese Vorlauf ein: Verdichter schaltet im Heizbetrieb ein
    "Hysterese_Vorlauf_ein": {ADDRESS: "7304", LENGTH: 2, UNIT: "IU10", ACCESS_MODE: "write"},
    # Hysterese Vorlauf aus: Verdichter schaltet im Heizbetrieb ab
    "Hysterese_Vorlauf_aus": {ADDRESS: "7313", LENGTH: 2, UNIT: "IU10", ACCESS_MODE: "write"},
    # --------- Function Call --------
    "Energiebilanz": {ADDRESS: "B800", LENGTH: 16, UNIT: "F_E", ACCESS_MODE: "call"},
}


class viCommandException(Exception):
    pass


class viCommand(bytearray):
    """Representation of a command. Object value is a bytearray of address and length."""

    # =============================================================
    # CHANGE YOUR COMMAND SET HERE:
    command_set = VITOCAL_WO1C

    # =============================================================

    def __init__(self, command_name):
        """Initialize object using the attributes of the chosen command."""
        try:
            command = self.command_set[command_name]
        except Exception as error:
            raise viCommandException(f"Unknown command {command_name}") from error
        self._command_code = command[ADDRESS]
        self._value_bytes = command[LENGTH]
        self.unit = command[UNIT]
        self.access_mode = self._get_access_mode(command)
        self.command_name = command_name

        # create bytearray representation
        b = bytes.fromhex(self._command_code) + self._value_bytes.to_bytes(1, "big")
        super().__init__(b)

    def _get_access_mode(self, command):
        if ACCESS_MODE in command:
            return command[ACCESS_MODE]
        return "read"

    @classmethod
    def _from_bytes(cls, b: bytearray):
        """Create command from address b given as byte, only the first two bytes of b are evaluated."""
        try:
            logger.debug("Convert %s to command.", b.hex())
            command_name = next(key for key, value in cls.command_set.items() if value[ADDRESS].lower() == b[0:2].hex())
        except Exception as error:
            raise viCommandException(f"No Command matching {b[0:2].hex()}") from error
        return viCommand(command_name)

    def response_length(self, access_mode="read"):
        """Returns the number of bytes in the response."""
        # request_response:
        # 2 'address'
        # 1 'Anzahl der Bytes des Wertes'
        # x 'Wert'
        if access_mode.lower() == "read":
            return 3 + self._value_bytes
        if access_mode.lower() == "write":
            # in write mode the written values are not returned
            return 3
        return 3 + self._value_bytes
