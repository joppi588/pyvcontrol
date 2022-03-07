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

from email import header
import logging
from collections import namedtuple
from struct import unpack

class viDataException(Exception):
    def __init__(self,msg):
        super().__init__(msg)

class viData(bytearray):
    # implements representations of viControl data types
    # erzeugen eines Datentypes über benannte Klasse -> setze code und codiere Parameter als bytes

    # konstruktor __init__ accepts byte-encoded input or real data
    # method __value__ returns the decoded value (str,int,fixed-point,...)
    # method __fromraw__ initializes the object with raw byte data
    # method __fromvalue__ initalizes the object with a typed value

    # Implemented units:
    # BA    : Betriebsart
    # ES    : Errorset
    # DT    : Devicetype
    # IS10  : Int signed, base 10 (i.e. 1 digit fixed point)
    # IU10  : Int unsigned, base 10 (i.e. 1 digit fixed point)
    # IUNON : Int unsigned, no base
    # IU3600: Int unsigned, base 3600 (i.e. hours & seconds)
    # OO    : On Off,
    # RT    : Return Type
    # FIXME: implemented all units -> create own classes
    # FIXME: Units für Temperatur, h, etc. erzeugen

    # units not implemented so far:
    unitset = {
        'CT': {'description': 'CycleTime', 'type': 'timer', 'signed': False, 'read_value_transform': 'non'},        # vito unit: CT
        'IU2': {'description': 'INT unsigned 2', 'type': 'integer', 'signed': False, 'read_value_transform': '2'},        # vito unit: UT1U, PR1
        'IUBOOL': {'description': 'INT unsigned bool', 'type': 'integer', 'signed': False, 'read_value_transform': 'bool'},        # vito unit:
        'IUINT': {'description': 'INT unsigned int', 'type': 'integer', 'signed': False, 'read_value_transform': 'int'},        # vito unit:
        'IS2': {'description': 'INT signed 2', 'type': 'integer', 'signed': True, 'read_value_transform': '2'},        # vito unit: UT1, PR
        'IS100': {'description': 'INT signed 100', 'type': 'integer', 'signed': True, 'read_value_transform': '100'},        # vito unit:
        'IS1000': {'description': 'INT signed 1000', 'type': 'integer', 'signed': True, 'read_value_transform': '1000'},        # vito unit:
        'ISNON': {'description': 'INT signed non', 'type': 'integer', 'signed': True, 'read_value_transform': 'non'},        # vito unit:
        'SC': {'description': 'SystemScheme', 'type': 'list', 'signed': False, 'read_value_transform': 'non'},  # vito unit:
        'SN': {'description': 'Sachnummer', 'type': 'serial', 'signed': False, 'read_value_transform': 'non'},  # vito unit:
        'SR': {'description': 'SetReturnStatus', 'type': 'list', 'signed': False, 'read_value_transform': 'non'},        # vito unit:
        'TI': {'description': 'SystemTime', 'type': 'datetime', 'signed': False, 'read_value_transform': 'non'},        # vito unit: TI
        'DA': {'description': 'Date', 'type': 'date', 'signed': False, 'read_value_transform': 'non'},  # vito unit:
    }

    def __init__(self,value):
        # to be overridden by subclass. subclass __init__ shall set default value for value and handle any extra parameters
        super().__init__()
        if type(value) == bytes or type(value) == bytearray:
            # choose the way of initialization
            self.__fromraw__(value)
        else:
            self.__fromtype__(value)

    def __fromraw__(self,value):
        #fill using byte values
        super().extend(value)
        self.len=len(value)

    def __fromtype__(self,value):
        # fill using type and value
        # empty declaration, must be overridden by subclass
        raise NotImplementedError

    @property
    def value(self):
        # empty declaration, must be overriden by subclass
        # returns value converted from raw data
        raise NotImplementedError

    @classmethod
    def create(cls,type,*args):
        # select data type object based on type
        # args are passed as such to the constructor of the function
        logging.debug(f'Data factory: request to produce Data type {type} with args {args}')
        datatype_object={'BA':viDataBA, 'DT':viDataDT, 'IS10':viDataIS10,'IU10':viDataIU10,
                         'IU3600':viDataIU3600,'IUNON':viDataIUNON, 'RT':viDataRT, 'OO':viDataOO,
                         'ES':viDataES, 'F_E': viDataEnergy,
                         }
        if type in datatype_object.keys():
            return datatype_object[type](*args)
        else:
            #if unit type is not implemented
            raise viDataException(f'Unit {type} not known')


# ----------------------------------------
# Below are the class definitions for each unit

class viDataBA(viData):
    #Betriebsart
    unit={'code':'BA','description': 'Betriebsart','unit':''}
    # operating mode codes are hex numbers
    operatingmodes = {
        0x00: 'Abschaltbetrieb',
        0x01: 'Warmwasser',
        0x02: 'Heizen und Warmwasser',
        0x03: 'undefiniert',
        0x04: 'dauernd reduziert',
        0x05: 'dauernd normal',
        0x06: 'normal Abschalt',
        0x07: 'nur kühlen'
    }

    def __init__(self,value=b'\x03'):
        # sets operating mode (hex) based on string opmode
        # if opmode is skipped defaults to 'undefiniert'
        super().__init__(value)

    def __fromtype__(self,opmode):
        if opmode in self.operatingmodes.values():
            opcode=next(key for key, value in self.operatingmodes.items() if value==opmode)
            super().extend(opcode.to_bytes(1,'big'))
        else:
            raise viDataException(f'Unknown operating mode {opmode}. Options are {self.operatingmodes.values()}')

    def __fromraw__(self,value):
        # set raw value directly
        if int.from_bytes(value, 'big') in self.operatingmodes.keys():
            super().extend(value)
        else:
            raise viDataException(f'Unknown operating mode {value.hex()}')

    @property
    def value(self):
        # returns decoded value
        return self.operatingmodes[int.from_bytes(self,'big')]

class viDataES(viData):
    #ERROR states
    unit={'code':'ES','description': 'Error','unit':''}
    # error codes are hex numbers
    errorset = {
        0x00: 'Regelbetrieb (kein Fehler)',
        0x0F: 'Wartung (fuer Reset Codieradresse 24 auf 0 stellen)',
        0x10: 'Kurzschluss Aussentemperatursensor',
        0x18: 'Unterbrechung Aussentemperatursensor',
        0x20: 'Kurzschluss Vorlauftemperatursensor',
        0x21: 'Kurzschluss Ruecklauftemperatursensor',
        0x28: 'Unterbrechung Aussentemperatursensor',
        0x29: 'Unterbrechung Ruecklauftemperatursensor',
        0x30: 'Kurzschluss Kesseltemperatursensor',
        0x38: 'Unterbrechung Kesseltemperatursensor',
        0x40: 'Kurzschluss Vorlauftemperatursensor M2',
        0x42: 'Unterbrechung Vorlauftemperatursensor M2',
        0x50: 'Kurzschluss Speichertemperatursensor',
        0x58: 'Unterbrechung Speichertemperatursensor',
        0x92: 'Solar: Kurzschluss Kollektortemperatursensor',
        0x93: 'Solar: Kurzschluss Sensor S3',
        0x94: 'Solar: Kurzschluss Speichertemperatursensor',
        0x9A: 'Solar: Unterbrechung Kollektortemperatursensor',
        0x9B: 'Solar: Unterbrechung Sensor S3',
        0x9C: 'Solar: Unterbrechung Speichertemperatursensor',
        0x9E: 'Solar: Zu geringer bzw. kein Volumenstrom oder Temperaturwächter ausgeloest',
        0x9F: 'Solar: Fehlermeldung Solarteil (siehe Solarregler)',
        0xA7: 'Bedienteil defekt',
        0xB0: 'Kurzschluss Abgastemperatursensor',
        0xB1: 'Kommunikationsfehler Bedieneinheit',
        0xB4: 'Interner Fehler (Elektronik)',
        0xB5: 'Interner Fehler (Elektronik)',
        0xB6: 'Ungueltige Hardwarekennung (Elektronik)',
        0xB7: 'Interner Fehler (Kesselkodierstecker)',
        0xB8: 'Unterbrechung Abgastemperatursensor',
        0xB9: 'Interner Fehler (Dateneingabe wiederholen)',
        0xBA: 'Kommunikationsfehler Erweiterungssatz fuer Mischerkreis M2',
        0xBC: 'Kommunikationsfehler Fernbedienung Vitorol, Heizkreis M1',
        0xBD: 'Kommunikationsfehler Fernbedienung Vitorol, Heizkreis M2',
        0xBE: 'Falsche Codierung Fernbedienung Vitorol',
        0xC1: 'Externe Sicherheitseinrichtung (Kessel kuehlt aus)',
        0xC2: 'Kommunikationsfehler Solarregelung',
        0xC5: 'Kommunikationsfehler drehzahlgeregelte Heizkreispumpe, Heizkreis M1',
        0xC6: 'Kommunikationsfehler drehzahlgeregelte Heizkreispumpe, Heizkreis M2',
        0xC7: 'Falsche Codierung der Heizkreispumpe',
        0xC9: 'Stoermeldeeingang am Schaltmodul-V aktiv',
        0xCD: 'Kommunikationsfehler Vitocom 100 (KM-BUS)',
        0xCE: 'Kommunikationsfehler Schaltmodul-V',
        0xCF: 'Kommunikationsfehler LON Modul',
        0xD1: 'Brennerstoerung',
        0xD4: 'Sicherheitstemperaturbegrenzer hat ausgeloest oder Stoermeldemodul nicht richtig gesteckt',
        0xDA: 'Kurzschluss Raumtemperatursensor, Heizkreis M1',
        0xDB: 'Kurzschluss Raumtemperatursensor, Heizkreis M2',
        0xDD: 'Unterbrechung Raumtemperatursensor, Heizkreis M1',
        0xDE: 'Unterbrechung Raumtemperatursensor, Heizkreis M2',
        0xE4: 'Fehler Versorgungsspannung',
        0xE5: 'Interner Fehler (Ionisationselektrode)',
        0xE6: 'Abgas- / Zuluftsystem verstopft',
        0xF0: 'Interner Fehler (Regelung tauschen)',
        0xF1: 'Abgastemperaturbegrenzer ausgeloest',
        0xF2: 'Temperaturbegrenzer ausgeloest',
        0xF3: 'Flammensigal beim Brennerstart bereits vorhanden',
        0xF4: 'Flammensigal nicht vorhanden',
        0xF7: 'Differenzdrucksensor defekt',
        0xF8: 'Brennstoffventil schliesst zu spaet',
        0xF9: 'Geblaesedrehzahl beim Brennerstart zu niedrig',
        0xFA: 'Geblaesestillstand nicht erreicht',
        0xFD: 'Fehler Gasfeuerungsautomat',
        0xFE: 'Starkes Stoerfeld (EMV) in der Naehe oder Elektronik defekt',
        0xFF: 'Starkes Stoerfeld (EMV) in der Naehe oder interner Fehler',
    }

    def __init__(self,value=b'\x00'):
        # default is no error
        super().__init__(value)

    #def __fromtype__(self,errstr):
        # Implementation does not make sense, an error will always be raised by the Viessmann unit

    def __fromraw__(self,value):
        # set raw value directly
        if int.from_bytes(value, 'big') in self.errorset.keys():
            super().extend(value)
        else:
            raise viDataException(f'Unknown error code {value.hex()}')

    @property
    def value(self):
        # returns decoded value
        return self.errorset[int.from_bytes(self,'big')]

class viDataDT(viData):
    # device types
    unit= {'description': 'DeviceType', 'code':'DT','unit':''}  # vito unit: DT
    devicetypes = {
        0x2098: 'V200KW2, Protokoll: KW2',
        0x2053: 'GWG_VBEM, Protokoll: GWG',
        0x20CB: 'VScotHO1, Protokoll: P300',
        0x2094: 'V200KW1, Protokoll: KW2',
        0x209F: 'V200KO1B, Protokoll: P300, KW2',
        0x204D: 'V200WO1C, Protokoll: P300',
        0x204B: 'Vitocal 333G, Protokoll: P300',
        0x20B8: 'V333MW1, Protokoll: ',
        0x20A0: 'V100GC1, Protokoll: ',
        0x20C2: 'VDensHO1, Protokoll: ',
        0x20A4: 'V200GW1, Protokoll: ',
        0x20C8: 'VPlusHO1, Protokoll: ',
        0x2046: 'V200WO1,VBC700, Protokoll: ',
        0x2047: 'V200WO1,VBC700, Protokoll: ',
        0x2049: 'V200WO1,VBC700, Protokoll: ',
        0x2032: 'VBC550, Protokoll: ',
        0x2033: 'VBC550, Protokoll: ',
        0x0000:'unknown'
    }

    def __init__(self, value=b'\x00\x00'):
        # sets device name (hex code). Either give value as bytearray/bytes or as device name string
        # usually this class would be initialized without arguments
        super().__init__(value)

    def __fromraw__(self,value):
        # set raw value directly
        if int.from_bytes(value, 'big') in self.devicetypes.keys():
            super().extend(value)
        else:
            raise viDataException(f'Unknown device code {value.hex()}')

    def __fromtype__(self,devicename):
        # devicename given as string
        if devicename in self.devicetypes.values():
            devcode = next(key for key, value in self.devicetypes.items() if value == devicename)
            super().extend(devcode.to_bytes(2, 'big'))
        else:
            raise viDataException(f'Unknown device name {devicename}')

    @property
    def value(self):
        # return device type as string
        return self.devicetypes[int.from_bytes(self,'big')]

class viDataIS10(viData):
    #IS10 - signed fixed-point integer, 1 decimal
    unit= {'code':'IS10','description': 'INT signed 10','unit':''}

    def __init__(self, value=b'\x00\x00', len=2):
        #sets int representation based on input value
        self.len = len  #length in bytes
        super().__init__(value)

    def __fromtype__(self, value):
        #fixed-point number given
        #FIXME Is it ok to overwrite its own value or should a new object be returned?
        super().extend(int(value * 10).to_bytes(self.len, 'little', signed=True))

    @property
    def value(self):
        return int.from_bytes(self,'little',signed=True)/10

class viDataIU10(viData):
    #IS10 - signed fixed-point integer, 1 decimal
    unit= {'code':'IU10','description': 'INT unsigned 10','unit':''}

    def __init__(self, value=b'\x00\x00', len=2):
        #sets int representation based on input value
        self.len=len  #length in bytes
        super().__init__(value)

    def __fromtype__(self,value):
        #fixed-point number given
        super().extend(int(value * 10).to_bytes(self.len,'little',signed=False))

    @property
    def value(self):
        return int.from_bytes(self,'little',signed=False)/10

class viDataIU3600(viData):
    #IU3600 - signed fixed-point integer, 1 decimal
    unit= {'code':'IS10','description': 'INT signed 10','unit':'h'}

    def __init__(self, value=b'\x00\x00', len=2):
        #sets int representation based on input value
        self.len=len  #length in bytes
        super().__init__(value)

    def __fromtype__(self,value):
        #fixed-point number given
        super().extend(int(value * 3600).to_bytes(self.len,'little',signed=False))

    @property
    def value(self):
        #FIXME round to two digits
        return int.from_bytes(self,'little',signed=True)/3600

class viDataIUNON(viData):
    #IUNON - unsigned int
    unit={'code':'IUNON','description': 'INT unsigned non','unit':''},        # vito unit: UTI, CO

    def __init__(self, value=b'\x00\x00',len=2):
        #sets int representation based on input value
        self.len=len  #length in bytes
        super().__init__(value)

    def __fromtype__(self,value):
        #fixed-point number given
        super().extend(int(value).to_bytes(self.len,'little',signed=False))

    @property
    def value(self):
        return int.from_bytes(self,'little',signed=False)

class viDataRT(viData):
    unit={'code':'RT','description': 'ReturnStatus','unit':''}
    # operating mode codes are hex numbers
    returnstatus = {
        0x00: '0',
        0x01: '1',
        0x03: '2',
        0xAA: 'Not OK'
    }
    def __init__(self,value=b'\x00'):
        # sets operating mode (hex) based on string opmode
        # if opmode is skipped defaults to 'undefiniert'
        super().__init__(value)

    def __fromtype__(self,status):
        if status in self.returnstatus.values():
            opcode=next(key for key, value in self.returnstatus.items() if value==status)
            super().extend(opcode.to_bytes(1,'big'))
        else:
            raise viDataException(f'Unknown return status {status}. Options are {self.returnstatus.values()}')

    def __fromraw__(self,value):
        # set raw value directly
        if int.from_bytes(value, 'big') in self.returnstatus.keys():
            super().extend(value)
        else:
            raise viDataException(f'Unknown return status {value.hex()}')

    @property
    def value(self):
        return self.returnstatus[int.from_bytes(self,'big')]

class viDataOO(viData):
    unit={'code':'OO','description': 'OnOff','unit':''}
    # operating mode codes are hex numbers
    OnOff = {
        0x00: 'Off',
        0x01: 'Manual',
        0x02: 'On',
    }
    def __init__(self,value=b'\x02'):
        # sets operating mode (hex) based on string opmode
        # if value is skipped defaults to 'off'
        super().__init__(value)

    def __fromtype__(self,onoff):
        if onoff in self.OnOff.values():
            opcode=next(key for key, value in self.OnOff.items() if value == onoff)
            super().extend(opcode.to_bytes(1,'big'))
        else:
            raise viDataException(f'Unknown value {onoff}. Options are {self.OnOff.values()}')

    def __fromraw__(self,value):
        # set raw value directly
        if int.from_bytes(value, 'big') in self.OnOff.keys():
            super().extend(value)
        else:
            raise viDataException(f'Unknown value {value.hex()}')

    @property
    def value(self):
        return self.OnOff[int.from_bytes(self, 'big')]


# holder type for Energy
Energy = namedtuple('Energy', 'byte1 day year week heating_energy heating_electrical_energy water_energy water_electrical_energy, cooling_energy cooling_electrical_energy total_energy total_eletrical_energy')

class viDataEnergy(viData):
    #Energy-Type ... Return from Function-Call B800
    # see https://github.com/openv/openv/issues/480#issuecomment-712235475
    # see https://github.com/openv/openv/wiki/FunctionCalls-WO1C
    unit={'code':'F_E','description': 'returns Named Tuple with enery Data','unit':''},      

    def __init__(self, value=b'\x00\x00',len=16):
        #sets int representation based on input value
        self.len=len  #length in bytes
        super().__init__(value)

    def __fromtype__(self,value):
        raise viDataException(f'Value not setable from Type')

    @property
    def value(self) -> Energy:
        # decode the Result Record an return a named tuple
        # see links above

        # example 02 02 16 09 92 03 aa 00 99 00 2d 00 00 00 00 00
        raw = unpack('<4B6H', self)        
        
        res = Energy(
            raw[0],raw[1],2000+raw[2],raw[3],
            raw[4]*0.1, raw[5]*0.1, #heating
            raw[6]*0.1, raw[7]*0.1, #water
            raw[8]*0.1, raw[9]*0.1, #cooling ??? 
            raw[4]*0.1+raw[6]*0.1+raw[8]*0.1, raw[5]*0.1+raw[7]*0.1+raw[9]*0.1 #total
        )

        return res
        
    @property
    def valueScan(self):
        # special property for scanning a function Call, see viTools
        # for function call B800: it seems that the first for bytes are a header
        # extract the header an try to decode the body as signed short
        header = unpack('<4B', self[0:4]) 
        body = unpack(f'<{len(self[4:])//2}h', self[4:])
        bodyDiv10 = [x*0.1 for x in body]

        return f"{self.hex(' ')} -- {header} - {body} / {bodyDiv10}"


systemschemes = {
    '01': 'WW',
    '02': 'HK + WW',
    '04': 'HK + WW',
    '05': 'HK + WW'
}
