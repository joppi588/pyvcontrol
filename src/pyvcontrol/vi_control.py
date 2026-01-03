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


import contextlib
import logging
from enum import Enum
from threading import Lock

from serial import Serial

from pyvcontrol.vi_command import ViCommand, ViCommandError
from pyvcontrol.vi_data import ViData
from pyvcontrol.vi_telegram import ViTelegram

logger = logging.getLogger(name="pyvcontrol")


class CtrlCode(bytes, Enum):
    """Control codes for serial communication."""

    RESET_CMD = b"\x04"
    SYNC_CMD = b"\x16\x00\x00"
    ACKNOWLEDGE = b"\x06"
    NOT_INIT = b"\x05"
    ERROR = b"\x15"


class ViConnectionError(Exception):
    """Indicates a failure setting up the connection."""


class ViControl:
    """Class to connect to ViControl heating directly via Optolink.

    Only supports WO1C with protocol P300.
    """

    _viessmann_lock = Lock()

    def __init__(self, port="/dev/ttyUSB0", baudrate=4800, bytesize=8, parity="E", stopbits=2):
        self._serial = Serial(
            port=port,
            baudrate=baudrate,
            parity=parity,
            bytesize=bytesize,
            stopbits=stopbits,
            timeout=1,  # read method will try 10 times -> 10s max waiting time for initialization
        )

    def execute_read_command(self, command_name) -> ViData:
        """Sends a read command and gets the response."""
        vc = ViCommand(command_name)
        return self.__execute_command(vc, "read")

    def execute_write_command(self, command_name, value) -> ViData:
        """Sends a write command and gets the response."""
        vc = ViCommand(command_name)
        vd = ViData.create(vc.unit, value)
        return self.__execute_command(vc, "write", payload=vd)

    def execute_function_call(self, command_name, *function_args) -> ViData:
        """Sends a function call command and gets response."""
        payload = bytearray((len(function_args), *function_args))
        vc = ViCommand(command_name)
        return self._execute_command(vc, "call", payload=payload)

    def _execute_command(self, vc, access_mode, payload=bytes(0)) -> ViData:
        vc.check_access_mode(access_mode)

        # send Telegram
        vt = ViTelegram(vc, access_mode, payload=payload)
        logger.debug("Send telegram %s", vt.hex())
        self.vs.send(vt)

        # Check if sending was successful
        ack = self.vs.read(1)
        logger.debug("Received %s", ack.hex())
        if ack != CtrlCode.ACKNOWLEDGE:
            raise ViCommandError(f"Expected acknowledge byte, received {ack}")

        # Receive response and evaluate data
        vr = self.vs.read(vt.response_length)  # receive response
        vt = ViTelegram.from_bytes(vr)
        logger.debug("Requested %s bytes. Received telegram {vr.hex()}", vt.response_length)
        if vt.tType == ViTelegram.tTypes["error"]:
            raise ViCommandError(f"{access_mode} command returned an error")
        self.vs.send(CtrlCode.ACKNOWLEDGE)  # send acknowledge

        # return ViData object from payload
        return ViData.create(vt.vicmd.unit, vt.payload)

    def __enter__(self):
        logger.debug("Init Communication to ViControl....")
        if not self._viessmann_lock.acquire(timeout=10):
            raise ViConnectionError("Could not acquire lock, aborting.")

        try:
            self._serial.open()
        except Exception as error:
            raise ViConnectionError("Could not open serial port, aborting.") from error

        # loop cases
        # 1 - ii=0: read timeout -> send reset / ii=1: not_init, send sync / ii=2:  Initialization successful
        # 1 - ii=0: error -> send reset / ii=1: not_init, send sync / ii=2:  Initialization successful
        # 2 - ... ii=10: exit loop, give up

        for ii in range(10):
            # loop until interface is initialized
            read_byte = self._serial.read(1)
            if read_byte == CtrlCode.ACKNOWLEDGE:
                # Schnittstelle hat auf den Initialisierungsstring mit OK geantwortet.
                # Die Abfrage von Werten kann beginnen.
                logger.debug("Step %s: Initialization successful", ii)
                return
            if read_byte == CtrlCode.NOT_INIT:
                # Schnittstelle ist zurückgesetzt und wartet auf Daten;
                # Antwort b'\x05' = Warten auf Initialisierungsstring
                logger.debug("Step %s: Viessmann ready, not initialized, send sync", ii)
                self._serial.write(CtrlCode.SYNC_CMD)
            elif read_byte == CtrlCode.ERROR:
                # in case of error try to reset
                logger.warning("The interface has reported an error, loop increment %s", ii)
                logger.debug("Step %s: Send reset", ii)
                self._serial.write(CtrlCode.RESET_CMD)
            else:
                # send reset
                logger.debug("Received [%s]. Step {ii}: Send reset", read_byte)
                self._serial.write(CtrlCode.RESET_CMD)

        raise ViConnectionError("Could not initialize communication.")

    def __exit__(self, exc_type, exc_value, traceback):
        with contextlib.suppress(Exception):
            self._serial.close()
        self._viessmann_lock.release()
