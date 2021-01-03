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
    # BT, DT, IS10, IUNON, OO, RT
    # units not implemented so far:
    # FIXME: implemented units -> create own classes
    unitset = {
        'CT': {'description': 'CycleTime', 'type': 'timer', 'signed': False, 'read_value_transform': 'non'},        # vito unit: CT
        'ES': {'description': 'ErrorState', 'type': 'list', 'signed': False, 'read_value_transform': 'non'},        # vito unit: ES
        'IU2': {'description': 'INT unsigned 2', 'type': 'integer', 'signed': False, 'read_value_transform': '2'},        # vito unit: UT1U, PR1
        'IU10': {'description': 'INT unsigned 10', 'type': 'integer', 'signed': False, 'read_value_transform': '10'},        # vito unit:
        'IU3600': {'description': 'INT unsigned 3600', 'type': 'integer', 'signed': False, 'read_value_transform': '3600'},        # vito unit: CS
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


def viDataFactory(type,*args):
    # select data type object based on type
    # args are passed as such to the constructor of the function
    logging.debug(f'Data factory: request to produce Data type {type} with args {args}')
    datatype_object={'BA':viDataBA, 'DT':viDataDT, 'IS10':viDataIS10,'IU10':viDataIU10, 'IU3600':viDataIU3600,'IUNON':viDataIUNON, 'RT':viDataRT, 'OO':viDataOO}
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
        self.len=len  #length in bytes
        super().__init__(value)

    def __fromtype__(self,value):
        #fixed-point number given
        #FIXME reference to self.len is a side effect, better pass as parameter but how?
        super().extend(int(value * 10).to_bytes(self.len,'little',signed=True))

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

