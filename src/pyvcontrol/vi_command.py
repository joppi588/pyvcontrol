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


import logging

from attrs import define

from pyvcontrol.vi_access_mode import AccessMode

logger = logging.getLogger(name="pyvcontrol")


ACCESS_MODE = "access_mode"
UNIT = "unit"
LENGTH = "length"
ADDRESS = "address"

COMMAND_SET = {
    "WO1C": {
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
        "Betriebsmodus": {ADDRESS: "B000", LENGTH: 1, UNIT: "BA", ACCESS_MODE: AccessMode.WRITE},
        # getManuell / setManuell -- 0 = normal, 1 = manueller Heizbetrieb, 2 = 1x Warmwasser auf Temp2
        "WWeinmal": {ADDRESS: "B020", LENGTH: 1, UNIT: "OO", ACCESS_MODE: AccessMode.WRITE},
        # Warmwassersolltemperatur (10..60 (95))
        "SolltempWarmwasser": {
            ADDRESS: "6000",
            LENGTH: 2,
            UNIT: "IS10",
            ACCESS_MODE: AccessMode.WRITE,
            "min_value": 10,
            "max_value": 60,
        },
        "RaumSollTempParty": {ADDRESS: "2022", LENGTH: 2, UNIT: "IS10", ACCESS_MODE: AccessMode.WRITE},
        # --------- Codierebene 2 ---------
        # Hysterese Vorlauf ein: Verdichter schaltet im Heizbetrieb ein
        "Hysterese_Vorlauf_ein": {ADDRESS: "7304", LENGTH: 2, UNIT: "IU10", ACCESS_MODE: AccessMode.WRITE},
        # Hysterese Vorlauf aus: Verdichter schaltet im Heizbetrieb ab
        "Hysterese_Vorlauf_aus": {ADDRESS: "7313", LENGTH: 2, UNIT: "IU10", ACCESS_MODE: AccessMode.WRITE},
        # --------- Function Call --------
        "Energiebilanz": {ADDRESS: "B800", LENGTH: 16, UNIT: "F_E", ACCESS_MODE: AccessMode.CALL},
    }
}


class ViCommandError(Exception):
    """Indicates an error during command execution."""


@define
class ViCommand(bytearray):
    """Representation of a command. Object value is a bytearray of address and length."""

    address: str
    length: int
    unit: str
    access_mode: AccessMode

    def __init__(self, command_name, heating_system="WO1C"):
        """Initialize object using the attributes of the chosen command."""
        self.command_set = COMMAND_SET[heating_system]
        try:
            command = self.command_set[command_name]
        except Exception as error:
            raise ViCommandError(f"Unknown command {command_name}") from error
        self._command_code = command[ADDRESS]
        self._value_bytes = command[LENGTH]
        self.unit = command[UNIT]
        self.access_mode = command.get(ACCESS_MODE, AccessMode.READ)
        self.command_name = command_name

        # create bytearray representation
        b = bytes.fromhex(self._command_code) + self._value_bytes.to_bytes(1, "big")
        super().__init__(b)

    def check_access_mode(self, access_mode):
        if not self.access_mode.allows(access_mode):
            raise ViCommandError(f"Command {self.command_name} only allows {str(self.access_mode)} access.")

    @classmethod
    def from_name(cls, command_name, heating_system="WO1C"):
        """Create command from name."""
        return COMMAND_SET[heating_system][command_name]

    @classmethod
    def from_bytes(cls, b: bytearray, heating_system="WO1C"):
        """Create command from address b given as byte.

        Only the first two bytes of b are evaluated.
        """
        try:
            logger.debug("Convert %s to command.", b.hex())
            command_set = COMMAND_SET[heating_system]
            command_name = next(key for key, value in command_set.items() if value[ADDRESS].lower() == b[0:2].hex())
        except Exception as error:
            raise ViCommandError(f"No Command matching {b[0:2].hex()}") from error
        return ViCommand.from_name(command_name, heating_system=heating_system)

    def response_length(self, access_mode: AccessMode = AccessMode.READ):
        """Returns the number of bytes in the response.

        request_response:
        2 'address'
        1 'Anzahl der Bytes des Wertes'
        x 'Wert'.
        """
        if access_mode == AccessMode.READ:
            return 3 + self._value_bytes
        if access_mode == AccessMode.WRITE:
            # in write mode the written values are not returned
            return 3
        return 3 + self._value_bytes
