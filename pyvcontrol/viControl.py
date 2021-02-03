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

# implements classes
# viControl: High-Level interface (API)
# - initComm: initialize Communication
# - execReadCmd: execute read Command
# - execWriteCmd: execute write Command
# viSerial: Low-level interface

from pyvcontrol.viCommand import viCommand
from pyvcontrol.viTelegram import viTelegram
from pyvcontrol.viData import viData
import logging
import serial
from threading import Lock
import time

controlset = {
    'Baudrate': 4800,
    'Bytesize': 8,  # 'EIGHTBITS'
    'Parity': 'E',  # 'PARITY_EVEN',
    'Stopbits': 2,  # 'STOPBITS_TWO',
}

ctrlcode = {
    'reset_cmd':    b'\x04',
    'sync_cmd':     b'\x16\x00\x00',
    'acknowledge':  b'\x06',
    'not_init':     b'\x05',
    'error':        b'\x15',
}


class viControlException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class viControl:
    # class to connect to viControl heating directly via Optolink
    # only supports WO1C with protocol P300
    def __init__(self, port='/dev/ttyUSB0'):
        self.vs = viSerial(controlset, port)
        self.vs.connect()
        self.isInitialized = False

    def __del__(self):
        # destructor, releases serial port
        self.vs.disconnect()

    def execReadCmd(self, cmdname):
        # sends a read command and gets the response.
        vc = viCommand(cmdname)  # create command
        vt = viTelegram(vc, 'read')  # create read Telegram

        logging.debug(f'Send telegram {vt.hex()}')
        self.vs.send(vt)  # send Telegram

        # Check if sending was successfull
        ack = self.vs.read(1)
        logging.debug(f'Received  {ack.hex()}')
        if ack != ctrlcode['acknowledge']:
            raise viControlException(f'Expected acknowledge byte, received {ack}')

        # Receive response and evaluate data
        vr = self.vs.read(vt.__responselen__)  # receive response
        logging.debug(f'Requested {vt.__responselen__} bytes. Received telegram {vr.hex()}')

        self.vs.send(ctrlcode['acknowledge'])  # send acknowledge

        vt = viTelegram.frombytes(vr)  # create response Telegram
        if vt.tType == viTelegram.tTypes['error']:
            raise viControlException('Read command returned an error')
        return viData.create(vt.vicmd.unit, vt.payload)  # return viData object from payload

    def execWriteCmd(self, cmdname, value) -> viData:
        # sends a read command and gets the response.

        vc = viCommand(cmdname)
        if not vc.write:
            raise viControlException(f'command {cmdname} cannot be written')

        # create viData object
        vd = viData.create(vc.unit, value)
        # create write Telegram
        vt = viTelegram(vc, 'Write', 'Request', vd)
        # send Telegram
        self.vs.send(vt)

        # Check if sending was successfull
        ack = self.vs.read(1)
        logging.debug(f'Received  {ack.hex()}')
        if ack != ctrlcode['acknowledge']:
            raise viControlException(f'Expected acknowledge byte, received {ack}')

        # Receive response and evaluate data
        vr = self.vs.read(vt.__responselen__)  # receive response
        logging.debug(f'Requested {vt.__responselen__} bytes. Received telegram {vr.hex()}')

        self.vs.send(ctrlcode['acknowledge'])  # send acknowledge

        vt = viTelegram.frombytes(vr)  # create response Telegram
        if vt.tType == viTelegram.tTypes['error']:
            raise viControlException('Write command returned an error')

        return viData.create(vt.vicmd.unit, vt.payload)  # return viData object from payload

    def initComm(self):
        logging.debug('Init Communication to viControl....')
        self.isInitialized = False

        # loop cases
        # 1 - ii=0: read timeout -> send reset / ii=1: not_init, send sync / ii=2:  Initialization successful
        # 1 - ii=0: error -> send reset / ii=1: not_init, send sync / ii=2:  Initialization successful
        # 2 - ... ii=10: exit loop, give up

        for ii in range(0, 10):
            # loop until interface is initialized
            readbyte = self.vs.read(1)
            if readbyte == ctrlcode['acknowledge']:
                # Schnittstelle hat auf den Initialisierungsstring mit OK geantwortet. Die Abfrage von Werten kann beginnen.
                logging.debug(f'Step {ii}: Initialization successful')
                self.isInitialized = True
                break
            elif readbyte == ctrlcode['not_init']:
                # Schnittstelle ist zurückgesetzt und wartet auf Daten; Antwort b'\x05' = Warten auf Initialisierungsstring
                logging.debug(f'Step {ii}: Viessmann ready, not initialized, send sync')
                self.vs.send(ctrlcode['sync_cmd'])
            elif readbyte == ctrlcode['error']:
                # in case of error try to reset
                logging.error(f'The interface has reported an error (\x15), loop increment {ii}')
                logging.debug(f'Step {ii}: Send reset')
                self.vs.send(ctrlcode['reset_cmd'])
            else:
                # send reset
                logging.debug(f'Received [{readbyte}]. Step {ii}: Send reset')
                self.vs.send(ctrlcode['reset_cmd'])

        if not self.isInitialized:
            # initialisation not successful
            raise viControlException('Could not initialize communication')

        logging.debug('Communication initialized')
        return True


class viSerial():
    # low-level communication interface
    # FIXME: control sets nicht übernommen
    __vlock__ = Lock()

    # viControl socket: implement raw communication
    def __init__(self, ctrlset, port):
        self.__connected__ = False
        self.__controlset__ = ctrlset
        self.__serialport__ = port

    def connect(self):
        # setup serial connection
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
                self._serial.timeout = 0.25 # read method will try 10 times -> 2.5s max waiting time
                self._serial.open()
                self.__connected__ = True
                logging.debug('Connected to {}'.format(self.__serialport__))
            except Exception as e:
                logging.error('Could not connect to {}; Error: {}'.format(self.__serialport__, e))
                self.__vlock__.release()
                self.__connected__ = False
        else:
            logging.error('Could not acquire lock')

    def disconnect(self):
        # release serial line and lock
        self._serial.close()
        self._serial = None
        self.__vlock__.release()
        self.__connected__ = False
        logging.debug('Disconnected from viControl')

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
        failed_count = 0
        # FIXME: read length bytes and try ten times if nothing received
        while failed_count < 10:
            # try to get one or more bytes
            readbyte = self._serial.read()
            totalreadbytes += readbyte
            if len(totalreadbytes) >= length:
                # exit loop if all bytes are received
                break
            if len(readbyte) == 0:
                # if nothing received, wait and retry
                failed_count += 1
                logging.debug(f'Serial read: retry ({failed_count})')
        logging.debug(f'Received {len(totalreadbytes)}/{length} bytes')
        return bytes(totalreadbytes)
