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
from typing import Any

from attrs import define, field

from pyvcontrol.vi_access_mode import AccessMode

logger = logging.getLogger(name="pyvcontrol")


class ViCommandError(Exception):
    """Indicates an error during command execution."""


@define
class ViCommand:
    """Representation of a command. Object value is a bytearray of address and length."""

    address: bytes = field(converter=lambda a: bytes.fromhex(a) if isinstance(a, str) else a)
    unit: str
    value_bytes: int

    access_mode: AccessMode = AccessMode.READ
    command_name: str = ""
    min_value: Any = None
    max_value: Any = None

    def as_bytearray(self) -> bytearray:
        """Bytearray representation."""
        return self.address + self.value_bytes.to_bytes(1, "big")

    def check_access_mode(self, access_mode):
        if not self.access_mode.allows(access_mode):
            raise ViCommandError(f"Command {self.command_name} only allows {str(self.access_mode)} access.")

    @classmethod
    def from_name(cls, command_name, heating_system="WO1C"):
        """Create command from name."""
        try:
            cmd = COMMAND_SET[heating_system][command_name]
            cmd.command_name = command_name
        except KeyError as error:
            raise ViCommandError(f"Unknown system {heating_system} or command {command_name}") from error
        else:
            return cmd

    @classmethod
    def from_bytes(cls, b: bytearray, heating_system="WO1C"):
        """Create command from address b given as byte.

        Only the first two bytes of b are evaluated.
        """
        try:
            logger.debug("Convert %s to command.", b.hex())
            command_set = COMMAND_SET[heating_system]
            command_name = next(key for key, cmd in command_set.items() if cmd.address == b[0:2])
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
            return 3 + self.value_bytes
        if access_mode == AccessMode.WRITE:
            # in write mode the written values are not returned
            return 3
        return 3 + self.value_bytes

    def __len__(self):
        return len(self.as_bytearray())

    def hex(self):
        return self.as_bytearray().hex()


COMMAND_SET = {
    "WO1C": {
        # All Parameters are tested and working on Vitocal 200S WO1C (Baujahr 2019)
        # ------ Statusinfos (read only) ------
        # Warmwasser: Warmwassertemperatur oben (0..95)
        "Warmwassertemperatur": ViCommand(address="010d", value_bytes=2, unit="IS10"),
        # Aussentemperatur (-40..70)
        "Aussentemperatur": ViCommand(address="0101", value_bytes=2, unit="IS10"),
        # Heizkreis HK1: Vorlauftemperatur Sekundaer 1 (0..95)
        "VorlauftempSek": ViCommand(address="0105", value_bytes=2, unit="IS10"),
        # Ruecklauftemperatur Sekundaer 1 (0..95)
        "RuecklauftempSek": ViCommand(address="0106", value_bytes=2, unit="IS10"),
        # Sekundaerpumpe [%] (including one status byte)
        "Sekundaerpumpe": ViCommand(address="B421", value_bytes=2, unit="IUNON"),
        # Faktor Energiebilanz(1 = 0.1kWh, 10 = 1kWh, 100 = 10kWh)
        "FaktorEnergiebilanz": ViCommand(address="163F", value_bytes=1, unit="IUNON"),
        # Heizwärme  "Heizbetrieb", Verdichter 1
        "Heizwaerme": ViCommand(address="1640", value_bytes=4, unit="IUNON"),
        # Elektroenergie "Heizbetrieb", Verdichter 1
        "Heizenergie": ViCommand(address="1660", value_bytes=4, unit="IUNON"),
        # Heizwärme  "WW-Betrieb", Verdichter 1
        "WWwaerme": ViCommand(address="1650", value_bytes=4, unit="IUNON"),
        # Elektroenergie "WW-Betrieb", Verdichter 1
        "WWenergie": ViCommand(address="1670", value_bytes=4, unit="IUNON"),
        # Verdichter [%] (including one status byte)
        "Verdichter": ViCommand(address="B423", value_bytes=4, unit="IUNON"),
        # Druck Sauggas [bar] (including one status byte) - Kühlmittel
        "DruckSauggas": ViCommand(address="B410", value_bytes=3, unit="IS10"),
        # Druck Heissgas [bar] (including one status byte)- Kühlmittel
        "DruckHeissgas": ViCommand(address="B411", value_bytes=3, unit="IS10"),
        # Temperatur Sauggas [bar] (including one status byte)- Kühlmittel
        "TempSauggas": ViCommand(address="B409", value_bytes=3, unit="IS10"),
        # Temperatur Heissgas [bar] (including one status byte)- Kühlmittel
        "TempHeissgas": ViCommand(address="B40A", value_bytes=3, unit="IS10"),
        # Anlagentyp (muss 204D sein)
        "Anlagentyp": ViCommand(address="00F8", value_bytes=4, unit="DT"),
        # --------- Menüebene -------
        # Betriebsmodus
        "Betriebsmodus": ViCommand(address="B000", value_bytes=1, unit="BA", access_mode=AccessMode.WRITE),
        # getManuell / setManuell -- 0 = normal, 1 = manueller Heizbetrieb, 2 = 1x Warmwasser auf Temp2
        "WWeinmal": ViCommand(address="B020", value_bytes=1, unit="OO", access_mode=AccessMode.WRITE),
        # Warmwassersolltemperatur (10..60 (95))
        "SolltempWarmwasser": ViCommand(
            address="6000", value_bytes=2, unit="IS10", access_mode=AccessMode.WRITE, min_value=10, max_value=60
        ),
        "RaumSollTempParty": ViCommand(address="2022", value_bytes=2, unit="IS10", access_mode=AccessMode.WRITE),
        # --------- Codierebene 2 ---------
        # Hysterese Vorlauf ein: Verdichter schaltet im Heizbetrieb ein
        "Hysterese_Vorlauf_ein": ViCommand(address="7304", value_bytes=2, unit="IU10", access_mode=AccessMode.WRITE),
        # Hysterese Vorlauf aus: Verdichter schaltet im Heizbetrieb ab
        "Hysterese_Vorlauf_aus": ViCommand(address="7313", value_bytes=2, unit="IU10", access_mode=AccessMode.WRITE),
        # --------- Function Call --------
        "Energiebilanz": ViCommand(address="B800", value_bytes=16, unit="F_E", access_mode=AccessMode.CALL),
    }
}
