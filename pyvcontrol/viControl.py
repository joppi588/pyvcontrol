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



from pyvcontrol.viCommand import viCommand,controlset
from pyvcontrol.viTelegram import viTelegram
from pyvcontrol.viData import viDataFactory,viData
import logging
import serial
from threading import Lock
import time

class viControlException(Exception):
    def __init__(self,msg):
        super().__init__(msg)

class viControl:
# class to connect to viControl heating directly via Optolink
# only supports WO1C with protocol P300
    def __init__(self):
        self.vs=viSerial(controlset, '/dev/ttyUSB0')
        self.vs.connect()
        self.isSync = False

    def __del__(self):
        #destructor, releases serial port
        self.vs.disconnect()

    def execReadCmd(self,cmdname):
        # sends a read command and gets the response.
        vc = viCommand(cmdname)           # create command
        vt = viTelegram(vc, 'read')  # create read Telegram

        logging.debug(f'Send telegram {vt.hex()}')
        self.vs.send(vt)                    # send Telegram

        # Check if sending was successfull
        ack=self.vs.read(1)
        logging.debug(f'Received  {ack.hex()}')
        if ack!=viControlCode('Acknowledge'):
            raise viControlException(f'Expected acknoledge byte, received {ack}')

        # Receive response and evaluate data
        vr = self.vs.read(vt.__responselen__)  # receive response
        if vt.mode==viTelegram.tModes['error']:
            raise viControlException('Write command returned an error')
        logging.debug(f'Requested {vt.__responselen__} bytes. Received telegram {vr.hex()}')

        self.vs.send(viControlCode('Acknowledge')) #send acknowledge

        vt = viTelegram.frombytes(vr)   #create response Telegram
        return viDataFactory(vt.vicmd.unit,vt.payload)     # return viData object from payload

    def execWriteCmd(self,cmdname,value) -> viData:
        # sends a read command and gets the response.

        vc=viCommand(cmdname)
        if not vc.write:
            raise viControlException(f'command {cmdname} cannot be written')

        # create viData object
        vd=viDataFactory(vc.unit,value)
        # create write Telegram
        vt=viTelegram(vc,'Write','Request',vd)
        # send Telegram
        self.vs.send(vt)

        # Check if sending was successfull
        ack = self.vs.read(1)
        logging.debug(f'Received  {ack.hex()}')
        if ack != viControlCode('Acknowledge'):
            raise viControlException(f'Expected acknowledge byte, received {ack}')

        # Receive response and evaluate data
        vr = self.vs.read(vt.__responselen__)  # receive response
        logging.debug(f'Requested {vc.__responselen__} bytes. Received telegram {vr.hex()}')

        # FIXME send ACK

        vt = viTelegram.frombytes(vr)  # create response Telegram
        if vt.mode==viTelegram.tModes['error']:
            raise viControlException('Write command returned an error')

        return viDataFactory(vt.vicmd.unit, vt.payload)  # return viData object from payload


    def initComm(self):
        # define subfunctions
        def __reset():
            #send reset proto viCommand
            self.vs.send(viControlCode('Reset_Command'))
            logging.debug('Send reset command {}'.format(viControlCode('Reset_Command')))

        def __sync():
            # Schnittstelle ist zurückgesetzt und wartet auf Daten; Antwort b'\x05' = Warten auf Initialisierungsstring oder Antwort b'\x06' = Schnittstelle initialisiert
            self.vs.send(viControlCode('Sync_Command'))
            logging.debug('Send sync command {}'.format(viControlCode('Sync_Command')))

        def __read_one_byte():
            readbyte = self.vs.read(1)
            logging.debug('Read {}'.format(readbyte))
            return readbyte

        #FIXME: wenn syncronisiert, sende sync string, entsprechend antwort weitermachen
        #sonst starte mit reset command
        for ii in range(0, 10):
            readbyte = __read_one_byte()
            logging.debug('Init Communication to viControl....')
            if readbyte == viControlCode('Acknowledge'):
                # Schnittstelle hat auf den Initialisierungsstring mit OK geantwortet. Die Abfrage von Werten kann beginnen. Diese Funktion meldet hierzu True zurück.
                self.isSync = True
                break
            elif readbyte == viControlCode('Not_initiated'):
                # Send sync command
                __sync()
            elif readbyte==viControlCode('Error'):
                logging.error(f'The interface has reported an error (\x15), loop increment {ii}')
                self.isSync=False
                __reset()
            else:
                self.isSync=False
                __reset()

        if not self.isSync:
            # initialisation not successful
            raise viControlException('Could not initialize communication')

        logging.info('Communication initialized')
        return True


#FIXME ein dictionary würde hier reichen
class viControlCode(bytearray):
    # bytearray representation of proto-commands
    controlcodeset = {
        # the strings are hex numbers and can be converted using bytearray.fromhex(...)
        # length in bytes is then available via 'len' function
        #FIXME keine Strings sondern byte-werte
        #fixme: definition als lower case
        'Acknowledge': '06',
        'Not_initiated': '05',
        'Error': '15',
        'Reset_Command': '04',
        'Reset_Command_Response': '05',
        'Sync_Command': '160000',
        # init:              send'Reset_Command' receive'Reset_Command_Response' send'Sync_Command'
        # request:           send('StartByte' 'Länge der Nutzdaten als Anzahl der Bytes zwischen diesem Byte und der Prüfsumme' 'Request' 'Read' 'addr' 'checksum')
        # request_response:  receive('Acknowledge' 'StartByte' 'Länge der Nutzdaten als Anzahl der Bytes zwischen diesem Byte und der Prüfsumme' 'Response' 'Read' 'addr' 'Anzahl der Bytes des Wertes' 'Wert' 'checksum')
    }

    def __init__(self,cmd):
        #if cmd is a string return protocommand code
        if type(cmd)==str:
            #FIXME das muss auch schöner gehen
            super().__init__(0)
            super().extend(bytes.fromhex(self.controlcodeset[cmd]))
        elif type(cmd)==int:
            # else, convert int to byte representation
            super.__init__(cmd.to_bytes(1,'big'))
        elif type(cmd)==bytes or type(cmd)==bytearray:
            #pass raw data
            super().__init__(cmd)


class viSerial():
    # low-level communication interface
    #FIXME: control sets nicht übernommen
    __vlock__ = Lock()

    #viControl socket: implement raw communication
    def __init__(self,ctrlset,port):
        self.__connected__=False
        self.__controlset__ = ctrlset
        self.__serialport__ = port

    def connect(self):
        # if not connected, try to acquire lock
        if self.__connected__:
            # do nothing
            logging.debug('Connect: Already connected')
            return
        if self.__vlock__.acquire(timeout=10):
            try:
                # initialize serial connection
                logging.debug('Connecting ...')
                self._serial = serial.Serial()
                self._serial.baudrate = self.__controlset__['Baudrate']
                self._serial.parity = self.__controlset__['Parity']
                self._serial.bytesize = self.__controlset__['Bytesize']
                self._serial.stopbits = self.__controlset__['Stopbits']
                self._serial.port = self.__serialport__
                self._serial.timeout = 1
                self._serial.open()
                self.__connected__ = True
                logging.debug('Connected to {}'.format(self.__serialport__))
            except Exception as e:
                logging.error('Could not _connect to {}; Error: {}'.format(self.__serialport__, e))
                self.__vlock__.release()
                self.__connected__=False
        else:
            logging.error('Could not acquire lock')

    def disconnect(self):
        # release serial line and lock
        self._serial.close()
        self._serial = None
        self.__vlock__.release()
        self.__connected__ = False
        logging.info('disconnected from viControl')

    def send(self, packet):
        # if connected send the packet
        if self.__connected__:
            self._serial.write(packet)
            return True
        else:
            return False

    def read(self, length):
        # read bytes from serial connection
        totalreadbytes = bytearray(0)
        failed_count=0
        #FIXME: read length bytes and try ten times if nothing received
        while failed_count<10:
            # try to get one or more bytes
            readbyte = self._serial.read()
            totalreadbytes += readbyte
            if len(totalreadbytes) >= length:
                # exit loop if all bytes are received
                break
            if len(readbyte)==0:
                # if nothing received, wait and retry
                time.sleep(0.2)
                failed_count+=1
                logging.debug(f'Serial read: retry ({failed_count})')
        logging.debug(f'Received {len(totalreadbytes)}/{length} bytes')
        return totalreadbytes