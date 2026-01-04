# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# Copyright 2021-2025 Jochen Schmähling
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
#  Python package for communication with Viessmann heatings using the serial Optolink interface
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

from __future__ import annotations

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

    def hex(self):
        return self.as_bytearray().hex()

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

    def __hash__(self):
        return int.from_bytes(self.address, byteorder="little")


@define
class ViCommandSet:
    """List of ViCommands."""

    commands: set[ViCommand]

    def __getitem__(self, key: str | bytearray):
        lookup = ("command_name", key) if isinstance(key, str) else ("address", key[0:2])
        try:
            logger.debug("Convert %s to command.", lookup[1])
            return next(command for command in self.commands if getattr(command, lookup[0]) == lookup[1])
        except Exception as error:
            raise KeyError(f"No Command matching {lookup[1]}") from error


COMMAND_SETS = {
    "WO1C": ViCommandSet(
        commands={
            # All Parameters are tested and working on Vitocal 200S WO1C (Baujahr 2019)
            # ------ Statusinfos (read only) ------
            # Warmwasser: Warmwassertemperatur oben (0..95)
            ViCommand(command_name="Warmwassertemperatur", address="010d", value_bytes=2, unit="IS10"),
            # Aussentemperatur (-40..70)
            ViCommand(command_name="Aussentemperatur", address="0101", value_bytes=2, unit="IS10"),
            # Heizkreis HK1: Vorlauftemperatur Sekundaer 1 (0..95)
            ViCommand(command_name="VorlauftempSek", address="0105", value_bytes=2, unit="IS10"),
            # Ruecklauftemperatur Sekundaer 1 (0..95)
            ViCommand(command_name="RuecklauftempSek", address="0106", value_bytes=2, unit="IS10"),
            # Sekundaerpumpe [%] (including one status byte)
            ViCommand(command_name="Sekundaerpumpe", address="B421", value_bytes=2, unit="IUNON"),
            # Faktor Energiebilanz(1 = 0.1kWh, 10 = 1kWh, 100 = 10kWh)
            ViCommand(command_name="FaktorEnergiebilanz", address="163F", value_bytes=1, unit="IUNON"),
            # Heizwärme  "Heizbetrieb", Verdichter 1
            ViCommand(command_name="Heizwaerme", address="1640", value_bytes=4, unit="IUNON"),
            # Elektroenergie "Heizbetrieb", Verdichter 1
            ViCommand(command_name="Heizenergie", address="1660", value_bytes=4, unit="IUNON"),
            # Heizwärme  "WW-Betrieb", Verdichter 1
            ViCommand(command_name="WWwaerme", address="1650", value_bytes=4, unit="IUNON"),
            # Elektroenergie "WW-Betrieb", Verdichter 1
            ViCommand(command_name="WWenergie", address="1670", value_bytes=4, unit="IUNON"),
            # Verdichter [%] (including one status byte)
            ViCommand(command_name="Verdichter", address="B423", value_bytes=4, unit="IUNON"),
            # Druck Sauggas [bar] (including one status byte) - Kühlmittel
            ViCommand(command_name="DruckSauggas", address="B410", value_bytes=3, unit="IS10"),
            # Druck Heissgas [bar] (including one status byte)- Kühlmittel
            ViCommand(command_name="DruckHeissgas", address="B411", value_bytes=3, unit="IS10"),
            # Temperatur Sauggas [bar] (including one status byte)- Kühlmittel
            ViCommand(command_name="TempSauggas", address="B409", value_bytes=3, unit="IS10"),
            # Temperatur Heissgas [bar] (including one status byte)- Kühlmittel
            ViCommand(command_name="TempHeissgas", address="B40A", value_bytes=3, unit="IS10"),
            # Anlagentyp (muss 204D sein)
            ViCommand(command_name="Anlagentyp", address="00F8", value_bytes=4, unit="DT"),
            # --------- Menüebene -------
            # Betriebsmodus
            ViCommand(
                command_name="Betriebsmodus", address="B000", value_bytes=1, unit="BA", access_mode=AccessMode.WRITE
            ),
            # getManuell / setManuell -- 0 = normal, 1 = manueller Heizbetrieb, 2 = 1x Warmwasser auf Temp2
            ViCommand(command_name="WWeinmal", address="B020", value_bytes=1, unit="OO", access_mode=AccessMode.WRITE),
            # Warmwassersolltemperatur (10..60 (95))
            ViCommand(
                command_name="SolltempWarmwasser",
                address="6000",
                value_bytes=2,
                unit="IS10",
                access_mode=AccessMode.WRITE,
                min_value=10,
                max_value=60,
            ),
            ViCommand(
                command_name="RaumSollTempParty",
                address="2022",
                value_bytes=2,
                unit="IS10",
                access_mode=AccessMode.WRITE,
            ),
            # --------- Codierebene 2 ---------
            # Hysterese Vorlauf ein: Verdichter schaltet im Heizbetrieb ein
            ViCommand(
                command_name="Hysterese_Vorlauf_ein",
                address="7304",
                value_bytes=2,
                unit="IU10",
                access_mode=AccessMode.WRITE,
            ),
            # Hysterese Vorlauf aus: Verdichter schaltet im Heizbetrieb ab
            ViCommand(
                command_name="Hysterese_Vorlauf_aus",
                address="7313",
                value_bytes=2,
                unit="IU10",
                access_mode=AccessMode.WRITE,
            ),
            # --------- Function Call --------
            ViCommand(
                command_name="Energiebilanz", address="B800", value_bytes=16, unit="F_E", access_mode=AccessMode.CALL
            ),
        }
    )
}
