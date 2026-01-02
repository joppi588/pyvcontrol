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
from abc import abstractmethod, abstractproperty
from struct import unpack

logger = logging.getLogger(name="pyvcontrol")

UNITS_NOT_IMPLEMENTED_YET = {
    "CT": {"description": "CycleTime", "type": "timer", "signed": False, "read_value_transform": "non"},
    # vito unit: CT
    "IU2": {"description": "INT unsigned 2", "type": "integer", "signed": False, "read_value_transform": "2"},
    # vito unit: UT1U, PR1
    "IUBOOL": {
        "description": "INT unsigned bool",
        "type": "integer",
        "signed": False,
        "read_value_transform": "bool",
    },  # vito unit:
    "IUINT": {"description": "INT unsigned int", "type": "integer", "signed": False, "read_value_transform": "int"},
    # vito unit:
    "IS2": {"description": "INT signed 2", "type": "integer", "signed": True, "read_value_transform": "2"},
    # vito unit: UT1, PR
    "IS100": {"description": "INT signed 100", "type": "integer", "signed": True, "read_value_transform": "100"},
    # vito unit:
    "IS1000": {"description": "INT signed 1000", "type": "integer", "signed": True, "read_value_transform": "1000"},
    # vito unit:
    "ISNON": {"description": "INT signed non", "type": "integer", "signed": True, "read_value_transform": "non"},
    # vito unit:
    "SC": {"description": "SystemScheme", "type": "list", "signed": False, "read_value_transform": "non"},
    # vito unit:
    "SN": {"description": "Sachnummer", "type": "serial", "signed": False, "read_value_transform": "non"},
    # vito unit:
    "SR": {"description": "SetReturnStatus", "type": "list", "signed": False, "read_value_transform": "non"},
    # vito unit:
    "TI": {"description": "SystemTime", "type": "datetime", "signed": False, "read_value_transform": "non"},
    # vito unit: TI
    "DA": {"description": "Date", "type": "date", "signed": False, "read_value_transform": "non"},  # vito unit:
}


class ViDataError(Exception):
    """Indicates an Error with ViData."""


class ViData(bytearray):
    """Implements representations of ViControl data types.

    erzeugen eines Datentypes über benannte Klasse -> setze code und codiere Parameter als bytes

    constructor __init__ accepts byte-encoded input or real data
    property value returns the decoded value (str,int,fixed-point,...)
    method _create_from_raw initializes the object with raw byte data
    method _create_from_value initializes the object with a typed value
    """

    unit = ""
    length = 1

    def __init__(self, value=b"\x00", length=1):
        """Create ViData.

        To set a different default value, override subclass constructors.
        """
        super().__init__()
        self.length = length
        if isinstance(value, (bytes, bytearray)):
            self._create_from_raw(value)
        else:
            self._create_from_value(value)

    def _create_from_raw(self, value):
        """Fill using byte values."""
        super().extend(value)

    @abstractmethod
    def _create_from_value(self, value):
        """Fill using type and value."""

    @abstractproperty
    def value(self):
        """Empty declaration, must be overriden by subclass."""

    @classmethod
    def create(cls, datatype, *args):
        """Select data type object based on type."""
        # args are passed as such to the constructor of the function
        logger.debug("Data factory: request to produce Data type %s with args {args}", datatype)
        datatype_object = {
            "BA": ViDataBA,
            "DT": ViDataDT,
            "IS10": ViDataIS10,
            "IU10": ViDataIU10,
            "IU3600": ViDataIU3600,
            "IUNON": ViDataIUNON,
            "RT": ViDataRT,
            "OO": ViDataOO,
            "ES": ViDataES,
            "F_E": ViDataEnergy,
        }
        if datatype in datatype_object:
            return datatype_object[datatype](*args)
        # if unit type is not implemented
        raise ViDataError(f"Unit {datatype} not known")

    def __str__(self):
        return str(self.value) + self.unit


class ViDataBA(ViData):
    """Betriebsart."""

    operating_modes = {
        0x00: "OFF",
        0x01: "WW",
        0x02: "HEATING_WW",
    }

    def _create_from_value(self, opmode: str):
        if opmode in self.operating_modes.values():
            opcode = next(key for key, value in self.operating_modes.items() if value == opmode)
            super().extend(opcode.to_bytes(1, "little"))
        else:
            raise ViDataError(f"Unknown operating mode {opmode}. Options are {self.operating_modes.values()}")

    def _create_from_raw(self, value):
        """Set raw value directly."""
        if int.from_bytes(value, "little") in self.operating_modes:
            super().extend(value)
        else:
            raise ViDataError(f"Unknown operating mode {value.hex()}")

    @property
    def value(self):
        """Returns decoded value."""
        return self.operating_modes[int.from_bytes(self, "little")]


class ViDataES(ViData):
    """Error states."""

    errorset = {
        0x00: "Regelbetrieb (kein Fehler)",
        0x0F: "Wartung (fuer Reset Codieradresse 24 auf 0 stellen)",
        0x10: "Kurzschluss Aussentemperatursensor",
        0x18: "Unterbrechung Aussentemperatursensor",
        0x20: "Kurzschluss Vorlauftemperatursensor",
        0x21: "Kurzschluss Ruecklauftemperatursensor",
        0x28: "Unterbrechung Aussentemperatursensor",
        0x29: "Unterbrechung Ruecklauftemperatursensor",
        0x30: "Kurzschluss Kesseltemperatursensor",
        0x38: "Unterbrechung Kesseltemperatursensor",
        0x40: "Kurzschluss Vorlauftemperatursensor M2",
        0x42: "Unterbrechung Vorlauftemperatursensor M2",
        0x50: "Kurzschluss Speichertemperatursensor",
        0x58: "Unterbrechung Speichertemperatursensor",
        0x92: "Solar: Kurzschluss Kollektortemperatursensor",
        0x93: "Solar: Kurzschluss Sensor S3",
        0x94: "Solar: Kurzschluss Speichertemperatursensor",
        0x9A: "Solar: Unterbrechung Kollektortemperatursensor",
        0x9B: "Solar: Unterbrechung Sensor S3",
        0x9C: "Solar: Unterbrechung Speichertemperatursensor",
        0x9E: "Solar: Zu geringer bzw. kein Volumenstrom oder Temperaturwächter ausgeloest",
        0x9F: "Solar: Fehlermeldung Solarteil (siehe Solarregler)",
        0xA7: "Bedienteil defekt",
        0xB0: "Kurzschluss Abgastemperatursensor",
        0xB1: "Kommunikationsfehler Bedieneinheit",
        0xB4: "Interner Fehler (Elektronik)",
        0xB5: "Interner Fehler (Elektronik)",
        0xB6: "Ungueltige Hardwarekennung (Elektronik)",
        0xB7: "Interner Fehler (Kesselkodierstecker)",
        0xB8: "Unterbrechung Abgastemperatursensor",
        0xB9: "Interner Fehler (Dateneingabe wiederholen)",
        0xBA: "Kommunikationsfehler Erweiterungssatz fuer Mischerkreis M2",
        0xBC: "Kommunikationsfehler Fernbedienung Vitorol, Heizkreis M1",
        0xBD: "Kommunikationsfehler Fernbedienung Vitorol, Heizkreis M2",
        0xBE: "Falsche Codierung Fernbedienung Vitorol",
        0xC1: "Externe Sicherheitseinrichtung (Kessel kuehlt aus)",
        0xC2: "Kommunikationsfehler Solarregelung",
        0xC5: "Kommunikationsfehler drehzahlgeregelte Heizkreispumpe, Heizkreis M1",
        0xC6: "Kommunikationsfehler drehzahlgeregelte Heizkreispumpe, Heizkreis M2",
        0xC7: "Falsche Codierung der Heizkreispumpe",
        0xC9: "Stoermeldeeingang am Schaltmodul-V aktiv",
        0xCD: "Kommunikationsfehler Vitocom 100 (KM-BUS)",
        0xCE: "Kommunikationsfehler Schaltmodul-V",
        0xCF: "Kommunikationsfehler LON Modul",
        0xD1: "Brennerstoerung",
        0xD4: "Sicherheitstemperaturbegrenzer hat ausgeloest oder Stoermeldemodul nicht richtig gesteckt",
        0xDA: "Kurzschluss Raumtemperatursensor, Heizkreis M1",
        0xDB: "Kurzschluss Raumtemperatursensor, Heizkreis M2",
        0xDD: "Unterbrechung Raumtemperatursensor, Heizkreis M1",
        0xDE: "Unterbrechung Raumtemperatursensor, Heizkreis M2",
        0xE4: "Fehler Versorgungsspannung",
        0xE5: "Interner Fehler (Ionisationselektrode)",
        0xE6: "Abgas- / Zuluftsystem verstopft",
        0xF0: "Interner Fehler (Regelung tauschen)",
        0xF1: "Abgastemperaturbegrenzer ausgeloest",
        0xF2: "Temperaturbegrenzer ausgeloest",
        0xF3: "Flammensigal beim Brennerstart bereits vorhanden",
        0xF4: "Flammensigal nicht vorhanden",
        0xF7: "Differenzdrucksensor defekt",
        0xF8: "Brennstoffventil schliesst zu spaet",
        0xF9: "Geblaesedrehzahl beim Brennerstart zu niedrig",
        0xFA: "Geblaesestillstand nicht erreicht",
        0xFD: "Fehler Gasfeuerungsautomat",
        0xFE: "Starkes Stoerfeld (EMV) in der Naehe oder Elektronik defekt",
        0xFF: "Starkes Stoerfeld (EMV) in der Naehe oder interner Fehler",
    }

    def __fromtype__(self, errstr):
        """Only created by the heating system."""
        raise NotImplementedError

    def _create_from_raw(self, value):
        """Set raw value directly."""
        if int.from_bytes(value, "big") in self.errorset:
            super().extend(value)
        else:
            raise ViDataError(f"Unknown error code {value.hex()}")

    @property
    def value(self):
        """Returns decoded value."""
        return self.errorset[int.from_bytes(self, "big")]


class ViDataDT(ViData):
    """Device types."""

    device_types = {
        0x2098: "V200KW2, Protokoll: KW2",
        0x2053: "GWG_VBEM, Protokoll: GWG",
        0x20CB: "VScotHO1, Protokoll: P300",
        0x2094: "V200KW1, Protokoll: KW2",
        0x209F: "V200KO1B, Protokoll: P300, KW2",
        0x204D: "V200WO1C, Protokoll: P300",
        0x204B: "Vitocal 333G, Protokoll: P300",
        0x20B8: "V333MW1, Protokoll: ",
        0x20A0: "V100GC1, Protokoll: ",
        0x20C2: "VDensHO1, Protokoll: ",
        0x20A4: "V200GW1, Protokoll: ",
        0x20C8: "VPlusHO1, Protokoll: ",
        0x2046: "V200WO1,VBC700, Protokoll: ",
        0x2047: "V200WO1,VBC700, Protokoll: ",
        0x2049: "V200WO1,VBC700, Protokoll: ",
        0x2032: "VBC550, Protokoll: ",
        0x2033: "VBC550, Protokoll: ",
        0x0000: "unknown",
    }

    def _create_from_raw(self, value):
        """Set raw value directly."""
        if int.from_bytes(value, "big") in self.device_types:
            super().extend(value)
        else:
            raise ViDataError(f"Unknown device code {value.hex()}")

    def _create_from_value(self, device_name):
        """Devicename given as string."""
        if device_name in self.device_types.values():
            devcode = next(key for key, value in self.device_types.items() if value == device_name)
            super().extend(devcode.to_bytes(2, "big"))
        else:
            raise ViDataError(f"Unknown device name {device_name}")

    @property
    def value(self):
        """Return device type as string."""
        return self.device_types[int.from_bytes(self, "big")]


class ViDataIS10(ViData):
    """IS10 - signed fixed-point integer, 1 decimal."""

    def __init__(self, value=b"\x00\x00"):
        """Sets int representation based on input value."""
        super().__init__(value, length=2)

    def _create_from_value(self, value):
        """fixed-point number given."""
        # TODO: Is it ok to overwrite its own value or should a new object be returned?
        super().extend(int(value * 10).to_bytes(self.length, "little", signed=True))

    @property
    def value(self):
        return int.from_bytes(self, "little", signed=True) / 10


class ViDataIU10(ViData):
    """IS10 - signed fixed-point integer, 1 decimal."""

    unit = {"code": "IU10", "description": "INT unsigned 10", "unit": ""}

    def __init__(self, value=b"\x00\x00"):
        """Sets int representation based on input value."""
        super().__init__(value, length=2)

    def _create_from_value(self, value):
        """fixed-point number given."""
        super().extend(int(value * 10).to_bytes(self.length, "little", signed=False))

    @property
    def value(self):
        return int.from_bytes(self, "little", signed=False) / 10


class ViDataIU3600(ViData):
    """IU3600 - signed fixed-point integer, 1 decimal."""

    unit = {"code": "IS10", "description": "INT signed 10", "unit": "h"}

    def __init__(self, value=b"\x00\x00"):
        """Sets int representation based on input value."""
        super().__init__(value, length=2)

    def _create_from_value(self, value):
        """fixed-point number given."""
        super().extend(int(value * 3600).to_bytes(self.length, "little", signed=False))

    @property
    def value(self):
        """FIXME round to two digits."""
        return int.from_bytes(self, "little", signed=True) / 3600


class ViDataIUNON(ViData):
    """IUNON - unsigned int."""

    unit = ({"code": "IUNON", "description": "INT unsigned non", "unit": ""},)  # vito unit: UTI, CO

    def __init__(self, value=b"\x00\x00"):
        """Sets int representation based on input value."""
        super().__init__(value, length=2)

    def _create_from_value(self, value):
        """fixed-point number given."""
        super().extend(int(value).to_bytes(self.length, "little", signed=False))

    @property
    def value(self):
        return int.from_bytes(self, "little", signed=False)


class ViDataRT(ViData):
    """Return type."""

    unit = {"code": "RT", "description": "ReturnStatus", "unit": ""}
    # operating mode codes are hex numbers
    returnstatus = {0x00: "0", 0x01: "1", 0x03: "2", 0xAA: "Not OK"}

    def _create_from_value(self, status):
        if status in self.returnstatus.values():
            opcode = next(key for key, value in self.returnstatus.items() if value == status)
            super().extend(opcode.to_bytes(1, "big"))
        else:
            raise ViDataError(f"Unknown return status {status}. Options are {self.returnstatus.values()}")

    def _create_from_raw(self, value):
        """set raw value directly."""  # noqa: D403
        if int.from_bytes(value, "big") in self.returnstatus:
            super().extend(value)
        else:
            raise ViDataError(f"Unknown return status {value.hex()}")

    @property
    def value(self):
        return self.returnstatus[int.from_bytes(self, "big")]


class ViDataOO(ViData):
    """On-Off."""

    unit = {"code": "OO", "description": "OnOff", "unit": ""}
    # operating mode codes are hex numbers
    OnOff = {
        0x00: "Off",
        0x01: "Manual",
        0x02: "On",
    }

    def _create_from_value(self, onoff):
        if onoff in self.OnOff.values():
            opcode = next(key for key, value in self.OnOff.items() if value == onoff)
            super().extend(opcode.to_bytes(1, "big"))
        else:
            raise ViDataError(f"Unknown value {onoff}. Options are {self.OnOff.values()}")

    def _create_from_raw(self, value):
        """set raw value directly."""  # noqa: D403
        if int.from_bytes(value, "big") in self.OnOff:
            super().extend(value)
        else:
            raise ViDataError(f"Unknown value {value.hex()}")

    @property
    def value(self):
        return self.OnOff[int.from_bytes(self, "big")]


LITTLE_ENDIAN_4_CHAR_6_SHORT = "<4B6H"
MILLENIUM = 2000
HEATING_ENERGY_FACTOR = 0.1


class ViDataEnergy(ViData):
    """Energy-Type ... Return from Function-Call B800."""

    def __init__(self, value=bytes(16)):
        super().__init__(value, length=16)

    def _create_from_raw(self, value):
        super().extend(value)
        raw_data = unpack(LITTLE_ENDIAN_4_CHAR_6_SHORT, value)
        self.day = raw_data[1]
        self.year = MILLENIUM + raw_data[2]
        self.week = raw_data[3]
        self.heating_energy = raw_data[4] * HEATING_ENERGY_FACTOR
        self.heating_electrical_energy = raw_data[5] * HEATING_ENERGY_FACTOR
        self.water_energy = raw_data[6] * HEATING_ENERGY_FACTOR
        self.water_electrical_energy = raw_data[7] * HEATING_ENERGY_FACTOR
        self.cooling_energy = raw_data[4] * HEATING_ENERGY_FACTOR
        self.cooling_electrical_energy = raw_data[5] * HEATING_ENERGY_FACTOR

    def _create_from_value(self, value):  # noqa: ARG002
        raise ViDataError("ViDataEnergy can only be created from bytes.")

    @property
    def value(self):
        """Decode the Result Record and return a dictionary."""
        total_energy = self.heating_energy + self.water_energy + self.cooling_energy
        total_electrical_energy = (
            self.heating_electrical_energy + self.water_electrical_energy + self.cooling_electrical_energy
        )

        value_dictionary = {
            "day": self.day,
            "week": self.week,
            "year": self.year,
            "heating_energy": self.heating_energy,
            "heating_electrical_energy": self.heating_electrical_energy,
            "water_energy": self.water_energy,
            "water_electrical_energy": self.water_electrical_energy,
            "cooling_energy": self.cooling_energy,
            "cooling_electrical_energy": self.cooling_electrical_energy,
            "total_energy": total_energy,
            "total_electrical_energy": total_electrical_energy,
        }

        return value_dictionary


system_schemes = {"01": "WW", "02": "HK + WW", "04": "HK + WW", "05": "HK + WW"}
