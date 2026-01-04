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

import logging
from abc import ABC, abstractmethod, abstractproperty
from struct import unpack

logger = logging.getLogger(name="pyvcontrol")

UNITS_NOT_IMPLEMENTED_YET = {
    "CT": {"description": "CycleTime", "type": "timer", "signed": False, "read_value_transform": "non"},
    "IU2": {"description": "INT unsigned 2", "type": "integer", "signed": False, "read_value_transform": "2"},
    "IUBOOL": {
        "description": "INT unsigned bool",
        "type": "integer",
        "signed": False,
        "read_value_transform": "bool",
    },
    "IUINT": {"description": "INT unsigned int", "type": "integer", "signed": False, "read_value_transform": "int"},
    "IS2": {"description": "INT signed 2", "type": "integer", "signed": True, "read_value_transform": "2"},
    "IS100": {"description": "INT signed 100", "type": "integer", "signed": True, "read_value_transform": "100"},
    "IS1000": {"description": "INT signed 1000", "type": "integer", "signed": True, "read_value_transform": "1000"},
    "ISNON": {"description": "INT signed non", "type": "integer", "signed": True, "read_value_transform": "non"},
    "SC": {"description": "SystemScheme", "type": "list", "signed": False, "read_value_transform": "non"},
    "SN": {"description": "Sachnummer", "type": "serial", "signed": False, "read_value_transform": "non"},
    "SR": {"description": "SetReturnStatus", "type": "list", "signed": False, "read_value_transform": "non"},
    "TI": {"description": "SystemTime", "type": "datetime", "signed": False, "read_value_transform": "non"},
    "DA": {"description": "Date", "type": "date", "signed": False, "read_value_transform": "non"},
}


class ViDataError(Exception):
    """Indicates an Error with ViData."""


class ViData(bytes, ABC):
    """Implements representations of ViControl data types.

    erzeugen eines Datentypes über benannte Klasse -> setze code und codiere Parameter als bytes

    constructor __init__ accepts byte-encoded input or real data
    property value returns the decoded value (str,int,fixed-point,...)
    method from_raw initializes the object with raw byte data
    method from_value initializes the object with a typed value
    """

    length: int = 1

    @classmethod
    def from_raw(cls, value):
        """Fill using byte values."""
        return cls(value)

    @classmethod
    @abstractmethod
    def from_value(cls, value):
        """Fill using type and value."""

    @abstractproperty
    def value(self):
        """Empty declaration, must be overriden by subclass."""

    @classmethod
    def create(cls, datatype, value):
        """Select data type object based on type."""
        logger.debug("Data factory: request to produce Data type %s with value %s", datatype, value)
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
            if isinstance(value, (bytes, bytearray)):
                return datatype_object[datatype].from_raw(value)
            return datatype_object[datatype].from_value(value)
        raise ViDataError(f"Unit {datatype} not known")

    def __str__(self):
        return str(self.value)


class ViDataBA(ViData):
    """Betriebsart."""

    operating_modes = {
        0x00: "OFF",
        0x01: "WW",
        0x02: "HEATING_WW",
    }

    @classmethod
    def from_value(cls, opmode: str):
        if opmode in cls.operating_modes.values():
            opcode = next(key for key, value in cls.operating_modes.items() if value == opmode)
            return cls(opcode.to_bytes(cls.length, "little"))
        raise ViDataError(f"Unknown operating mode {opmode}. Options are {cls.operating_modes.values()}")

    @classmethod
    def from_raw(cls, value):
        """Set raw value directly."""
        if int.from_bytes(value, "little") in cls.operating_modes:
            return cls(value)
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

    @classmethod
    def from_raw(cls, value):
        """Set raw value directly."""
        if int.from_bytes(value, "big") in cls.errorset:
            return cls(value)
        raise ViDataError(f"Unknown error code {value.hex()}")

    @property
    def value(self):
        """Returns decoded value."""
        return self.errorset[int.from_bytes(self, "big")]


class ViDataDT(ViData):
    """Device types."""

    length = 2

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

    @classmethod
    def from_raw(cls, value):
        """Set raw value directly."""
        if int.from_bytes(value, "big") in cls.device_types:
            return cls(value)
        raise ViDataError(f"Unknown device code {value.hex()}")

    @classmethod
    def from_value(cls, device_name):
        """Devicename given as string."""
        if device_name in cls.device_types.values():
            devcode = next(key for key, value in cls.device_types.items() if value == device_name)
            return cls(devcode.to_bytes(cls.length, "big"))
        raise ViDataError(f"Unknown device name {device_name}")

    @property
    def value(self):
        """Return device type as string."""
        return self.device_types[int.from_bytes(self, "big")]


class ViDataIS10(ViData):
    """IS10 - signed fixed-point integer, 1 decimal."""

    length = 2

    @classmethod
    def from_value(cls, value):
        """fixed-point number given."""
        return cls(int(value * 10).to_bytes(cls.length, "little", signed=True))

    @property
    def value(self):
        return int.from_bytes(self, "little", signed=True) / 10


class ViDataIU10(ViData):
    """IS10 - unsigned fixed-point integer, 1 decimal."""

    length = 2

    @classmethod
    def from_value(cls, value):
        """fixed-point number given."""
        return cls(int(value * 10).to_bytes(cls.length, "little", signed=False))

    @property
    def value(self):
        return int.from_bytes(self, "little", signed=False) / 10


class ViDataIU3600(ViData):
    """IU3600 - Unsigned int 3600 base (hours)."""

    length = 2

    @classmethod
    def from_value(cls, value):
        """fixed-point number given."""
        return cls(int(value * 3600).to_bytes(cls.length, "little", signed=False))

    @property
    def value(self):
        """TODO: round to two digits."""
        return int.from_bytes(self, "little", signed=False) / 3600


class ViDataIUNON(ViData):
    """IUNON - unsigned int."""

    length = 2

    @classmethod
    def from_value(cls, value):
        """fixed-point number given."""
        return cls(int(value).to_bytes(cls.length, "little", signed=False))

    @property
    def value(self):
        return int.from_bytes(self, "little", signed=False)


class ViDataRT(ViData):
    """Return type."""

    returnstatus = {0x00: "0", 0x01: "1", 0x03: "2", 0xAA: "Not OK"}

    @classmethod
    def from_value(cls, status):
        if status in cls.returnstatus.values():
            opcode = next(key for key, value in cls.returnstatus.items() if value == status)
            return cls(opcode.to_bytes(cls.length, "big"))
        raise ViDataError(f"Unknown return status {status}. Options are {cls.returnstatus.values()}")

    @classmethod
    def from_raw(cls, value):
        """Set raw value directly."""
        if int.from_bytes(value, "big") in cls.returnstatus:
            return cls(value)
        raise ViDataError(f"Unknown return status {value.hex()}")

    @property
    def value(self):
        return self.returnstatus[int.from_bytes(self, "big")]


class ViDataOO(ViData):
    """On-Off."""

    OnOff = {
        0x00: "Off",
        0x01: "Manual",
        0x02: "On",
    }

    @classmethod
    def from_value(cls, onoff):
        if onoff in cls.OnOff.values():
            opcode = next(key for key, value in cls.OnOff.items() if value == onoff)
            return cls(opcode.to_bytes(cls.length, "big"))
        raise ViDataError(f"Unknown value {onoff}. Options are {cls.OnOff.values()}")

    @classmethod
    def from_raw(cls, value):
        """Set raw value directly."""
        if int.from_bytes(value, "big") in cls.OnOff:
            return cls(value)
        raise ViDataError(f"Unknown value {value.hex()}")

    @property
    def value(self):
        return self.OnOff[int.from_bytes(self, "big")]


LITTLE_ENDIAN_4_CHAR_6_SHORT = "<4B6H"
MILLENIUM = 2000
HEATING_ENERGY_FACTOR = 0.1


class ViDataEnergy(ViData):
    """Energy-Type ... Return from Function-Call B800."""

    length = 16

    @classmethod
    def from_raw(cls, value):
        vi_data_energy = cls(value or bytes(16))
        raw_data = unpack(LITTLE_ENDIAN_4_CHAR_6_SHORT, value)
        vi_data_energy.day = raw_data[1]
        vi_data_energy.year = MILLENIUM + raw_data[2]
        vi_data_energy.week = raw_data[3]
        vi_data_energy.heating_energy = raw_data[4] * HEATING_ENERGY_FACTOR
        vi_data_energy.heating_electrical_energy = raw_data[5] * HEATING_ENERGY_FACTOR
        vi_data_energy.water_energy = raw_data[6] * HEATING_ENERGY_FACTOR
        vi_data_energy.water_electrical_energy = raw_data[7] * HEATING_ENERGY_FACTOR
        vi_data_energy.cooling_energy = raw_data[4] * HEATING_ENERGY_FACTOR
        vi_data_energy.cooling_electrical_energy = raw_data[5] * HEATING_ENERGY_FACTOR
        return vi_data_energy

    @classmethod
    def from_value(cls, value):
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
