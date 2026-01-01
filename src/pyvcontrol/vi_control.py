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
from threading import Lock

import serial

from pyvcontrol.vi_command import ViCommand
from pyvcontrol.vi_data import viData
from pyvcontrol.vi_telegram import viTelegram

logger = logging.getLogger(name="pyvcontrol")

control_set = {
    "Baudrate": 4800,
    "Bytesize": 8,  # 'EIGHTBITS'
    "Parity": "E",  # 'PARITY_EVEN',
    "Stopbits": 2,  # 'STOPBITS_TWO',
}

ctrlcode = {
    "reset_cmd": b"\x04",
    "sync_cmd": b"\x16\x00\x00",
    "acknowledge": b"\x06",
    "not_init": b"\x05",
    "error": b"\x15",
}


class viControlError(Exception):
    """Indicates an error during ViControl."""

    def __init__(self, msg):
        super().__init__(msg)


class viControl:
    # class to connect to viControl heating directly via Optolink
    # only supports WO1C with protocol P300
    def __init__(self, port="/dev/ttyUSB0"):
        self.vs = ViSerial(control_set, port)
        self.vs.connect()
        self.is_initialized = False

    def __del__(self):
        # destructor, releases serial port
        self.vs.disconnect()

    def execute_read_command(self, command_name) -> viData:
        """Sends a read command and gets the response."""
        vc = ViCommand(command_name)
        return self.execute_command(vc, "read")

    def execute_write_command(self, command_name, value) -> viData:
        """Sends a write command and gets the response."""
        vc = ViCommand(command_name)
        vd = viData.create(vc.unit, value)
        return self.execute_command(vc, "write", payload=vd)

    def execute_function_call(self, command_name, *function_args) -> viData:
        """Sends a function call command and gets response."""
        payload = bytearray((len(function_args), *function_args))
        vc = ViCommand(command_name)
        return self.execute_command(vc, "call", payload=payload)

    def execute_command(self, vc, access_mode, payload=bytes(0)) -> viData:
        # prepare command
        allowed_access_mode = {"read": ["read"], "write": ["read", "write"], "call": ["call"]}
        if access_mode not in allowed_access_mode[vc.access_mode]:
            raise viControlError(f"command {vc.command_name} allows only {allowed_access_mode[vc.access_mode]} access")

        # send Telegram
        vt = viTelegram(vc, access_mode, payload=payload)
        logger.debug("Send telegram %s", vt.hex())
        self.vs.send(vt)

        # Check if sending was successful
        ack = self.vs.read(1)
        logger.debug("Received %s", ack.hex())
        if ack != ctrlcode["acknowledge"]:
            raise viControlError(f"Expected acknowledge byte, received {ack}")

        # Receive response and evaluate data
        vr = self.vs.read(vt.response_length)  # receive response
        vt = viTelegram.from_bytes(vr)
        logger.debug("Requested %s bytes. Received telegram {vr.hex()}", vt.response_length)
        if vt.tType == viTelegram.tTypes["error"]:
            raise viControlError(f"{access_mode} command returned an error")
        self.vs.send(ctrlcode["acknowledge"])  # send acknowledge

        # return viData object from payload
        return viData.create(vt.vicmd.unit, vt.payload)

    def initialize_communication(self):
        logger.debug("Init Communication to viControl....")
        self.is_initialized = False

        # loop cases
        # 1 - ii=0: read timeout -> send reset / ii=1: not_init, send sync / ii=2:  Initialization successful
        # 1 - ii=0: error -> send reset / ii=1: not_init, send sync / ii=2:  Initialization successful
        # 2 - ... ii=10: exit loop, give up

        for ii in range(10):
            # loop until interface is initialized
            read_byte = self.vs.read(1)
            if read_byte == ctrlcode["acknowledge"]:
                # Schnittstelle hat auf den Initialisierungsstring mit OK geantwortet. Die Abfrage von Werten kann beginnen.
                logger.debug("Step %s: Initialization successful", ii)
                self.is_initialized = True
                break
            if read_byte == ctrlcode["not_init"]:
                # Schnittstelle ist zurückgesetzt und wartet auf Daten; Antwort b'\x05' = Warten auf Initialisierungsstring
                logger.debug("Step %s: Viessmann ready, not initialized, send sync", ii)
                self.vs.send(ctrlcode["sync_cmd"])
            elif read_byte == ctrlcode["error"]:
                # in case of error try to reset
                logger.error("The interface has reported an error, loop increment %s", ii)
                logger.debug("Step %s: Send reset", ii)
                self.vs.send(ctrlcode["reset_cmd"])
            else:
                # send reset
                logger.debug("Received [%s]. Step {ii}: Send reset", read_byte)
                self.vs.send(ctrlcode["reset_cmd"])

        if not self.is_initialized:
            # initialisation not successful
            raise viControlError("Could not initialize communication")

        logger.debug("Communication initialized")
        return True


class ViSerial:
    # low-level communication interface
    # TODO: control sets nicht übernommen
    _viessmann_lock = Lock()

    # viControl socket: implement raw communication
    def __init__(self, control_set, port):
        self._connected = False
        self._control_set = control_set
        self._serial_port = port
        self._serial = serial.Serial()

    def connect(self):
        # setup serial connection
        # if not connected, try to acquire lock
        if self._connected:
            # do nothing
            logger.debug("Connect: Already connected")
            return
        if self._viessmann_lock.acquire(timeout=10):
            try:
                # initialize serial connection
                logger.debug("Connecting ...")
                self._serial.baudrate = self._control_set["Baudrate"]
                self._serial.parity = self._control_set["Parity"]
                self._serial.bytesize = self._control_set["Bytesize"]
                self._serial.stopbits = self._control_set["Stopbits"]
                self._serial.port = self._serial_port
                self._serial.timeout = 0.25  # read method will try 10 times -> 2.5s max waiting time
                self._serial.open()
                self._connected = True
                logger.debug("Connected to %s", self._serial_port)
            except Exception:
                logger.exception("Could not connect to %s.", self._serial_port)
                self._viessmann_lock.release()
                self._connected = False
        else:
            logger.error("Could not acquire lock")

    def disconnect(self):
        # release serial line and lock
        self._serial.close()
        self._serial = None
        self._viessmann_lock.release()
        self._connected = False
        logger.debug("Disconnected from viControl")

    def send(self, packet):
        # if connected send the packet
        if self._connected:
            self._serial.write(packet)
            return True
        return False

    def read(self, length):
        # read bytes from serial connection
        total_read_bytes = bytearray(0)
        failed_count = 0
        # TODO: read length bytes and try ten times if nothing received
        while failed_count < 10:
            # try to get one or more bytes
            read_byte = self._serial.read()
            total_read_bytes += read_byte
            if len(total_read_bytes) >= length:
                # exit loop if all bytes are received
                break
            if len(read_byte) == 0:
                # if nothing received, wait and retry
                failed_count += 1
                logger.debug("Serial read: retry (%s)", failed_count)
        logger.debug("Received %s/{length} bytes", len(total_read_bytes))
        return bytes(total_read_bytes)
