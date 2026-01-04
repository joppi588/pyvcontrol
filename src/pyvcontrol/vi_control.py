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

from pyvcontrol.vi_command import COMMAND_SETS, AccessMode
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


class ViCommunicationError(Exception):
    """Indicates a failure during communication."""


class ViControl:
    """Class to connect to ViControl heating directly via Optolink.

    Only supports WO1C with protocol P300.
    """

    _viessmann_lock = Lock()

    def __init__(  # noqa: PLR0913
        self,
        port="/dev/ttyUSB0",
        baudrate=4800,
        bytesize=8,
        parity="E",
        stopbits=2,
        timeout=1,
        lock_timeout=10,
        init_retries=10,
        heating_system="WO1C",
    ):
        """Read method will try init_retries times -> init_retries*timeout max waiting time for initialization."""
        self._serial = Serial(
            port=port,
            baudrate=baudrate,
            parity=parity,
            bytesize=bytesize,
            stopbits=stopbits,
            timeout=timeout,
        )
        self._lock_timeout = lock_timeout
        self._init_retries = init_retries
        self._is_initialized = False
        self._command_set = COMMAND_SETS[heating_system]

    def execute_read_command(self, command_name) -> ViData:
        """Sends a read command and gets the response."""
        vc = self._command_set[command_name]
        return self._execute_command(vc, AccessMode.READ)

    def execute_write_command(self, command_name, value) -> ViData:
        """Sends a write command and gets the response."""
        vc = self._command_set[command_name]
        vd = ViData.create(vc.unit, value)
        return self._execute_command(vc, AccessMode.WRITE, payload=vd)

    def execute_function_call(self, command_name, *function_args) -> ViData:
        """Sends a function call command and gets response."""
        payload = bytearray((len(function_args), *function_args))
        vc = self._command_set[command_name]
        return self._execute_command(vc, AccessMode.CALL, payload=payload)

    def _execute_command(self, vc, access_mode, payload=bytes(0)) -> ViData:
        vc.check_access_mode(access_mode)

        if not self._is_initialized:
            self._initialize_communication()

        # send Telegram
        vt = ViTelegram(vc, access_mode, payload=payload)
        logger.debug("Send telegram %s", vt.hex())
        self._serial.write(vt)

        # Check if sending was successful
        ack = self._serial.read(1)
        logger.debug("Received %s", ack.hex())
        if ack != CtrlCode.ACKNOWLEDGE:
            raise ViCommunicationError(f"Expected acknowledge byte, received {ack}")

        # Receive response and evaluate data
        vr = self._serial.read(vt.response_length)
        vt = ViTelegram.from_bytes(vr, self._command_set)
        logger.debug("Requested %s bytes. Received telegram %s", vt.response_length, vr.hex())
        if vt.tType == ViTelegram.tTypes["error"]:
            raise ViCommunicationError(f"{access_mode} command returned an error")
        self._serial.write(CtrlCode.ACKNOWLEDGE)

        # return ViData object from payload
        return ViData.create(vt.vicmd.unit, vt.payload)

    def _initialize_communication(self):
        # loop cases
        # 1 - ii=0: read timeout -> send reset / ii=1: not_init, send sync / ii=2:  Initialization successful
        # 1 - ii=0: error -> send reset / ii=1: not_init, send sync / ii=2:  Initialization successful
        # 2 - ... ii=_retry_init: exit loop, give up

        for ii in range(self._init_retries):
            # loop until interface is initialized
            read_byte = self._serial.read(1)
            if read_byte == CtrlCode.ACKNOWLEDGE:
                # Schnittstelle hat auf den Initialisierungsstring mit OK geantwortet.
                # Die Abfrage von Werten kann beginnen.
                logger.debug("Step %s: Initialization successful", ii)
                return self
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
                logger.debug("Received [%s]. Step %s: Send reset", read_byte, ii)
                self._serial.write(CtrlCode.RESET_CMD)

        raise ViConnectionError("Could not initialize communication.")

    def __enter__(self):
        logger.debug("Init Communication to ViControl....")
        if not self._viessmann_lock.acquire(timeout=self._lock_timeout):
            raise ViConnectionError("Could not acquire lock, aborting.")

        try:
            if not self._serial.is_open:
                self._serial.open()
        except Exception as error:
            self._viessmann_lock.release()
            raise ViConnectionError("Could not open serial port, aborting.") from error
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value is not None:
            logger.exception("Error communicating with device.")
        with contextlib.suppress(Exception):
            self._serial.close()
        self._viessmann_lock.release()
