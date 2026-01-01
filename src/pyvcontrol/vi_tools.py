# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# Copyright 2021-2025 Jochen Schmähling
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
#  Tools for communication with ViControl heatings using the serial Optolink interface
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

import curses
import logging
import time

from pyvcontrol.vi_control import ViControl, ViControlError, ctrlcode, viTelegram

logger = logging.getLogger(name="pyvcontrol")


def viscancommands(addressrange):
    # brute force command scanner
    # hilft v.a. um die richtige Payload-Länge für bekannte Kommandos herauszufinden

    logging.basicConfig(filename="scancommands.log", filemode="w", level=logger.debug)

    vo = ViControl()
    vo.initialize_communication()

    for addr in addressrange:
        for kk in range(1, 5):
            # TODO: Inneren Teil ausschneiden und in separate Funktion? ("low level read command")
            logger.debug("---%s-{kk}------------------", hex(addr))
            vc = addr.to_bytes(2, "big") + kk.to_bytes(1, "big")
            vt = viTelegram(vc, "read")  # create read Telegram
            vo.vs.send(vt)  # send Telegram
            logger.debug("Send telegram %s", vt.hex())

            try:
                # Check if sending was successfull
                ack = vo.vs.read(1)
                if ack != ctrlcode["acknowledge"]:
                    logger.debug("Viessmann returned %s", ack.hex())
                    vo.initialize_communication()
                    raise ViControlError(f"Expected acknowledge byte, received {ack}")

                # Receive response and evaluate data
                vr1 = vo.vs.read(2)  # receive response
                vr2 = vo.vs.read(vr1[1] + 1)  # read rest of telegram
                # TODO: create Telegram instead of low-level access (for better readability)
                logger.debug("received telegram %s {vr2.hex()}", vr1.hex())

                if vr2[0].to_bytes(1, "little") == viTelegram.tTypes["response"]:
                    v = int.from_bytes(vr2[-1 - kk : -1], "little")
                    print(f"Found working command 0x{hex(addr)}, payload length {kk}, value {v}")

            except Exception as e:
                logger.exception({e})
                print(f"An exception occurred: {e}")


def vimonitor(command_list, updateinterval=30):
    # repeatedly executes commands
    # commandlist is a list of strings (command names from ViCommand)

    # TODO: accept also addresses & length as commands
    # Option 1) "Generic command" based on addr and length 2) add command to command set first
    if not isinstance(command_list, list):
        # wrap single commands into a list
        command_list = [command_list]

    logging.basicConfig(filename="Monitor.log", filemode="w", level=logger.debug)
    vo = ViControl()

    standard_screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    standard_screen.nodelay(True)

    loop_monitor = True
    while loop_monitor:
        standard_screen.clear()
        standard_screen.addstr(0, 0, "Reading values...")
        standard_screen.refresh()
        standard_screen.addstr(1, 0, "--- Viessmann monitor ---\n")
        try:
            vo.initialize_communication()
            for c in command_list:
                v = vo.execReadCmd(c).value
                standard_screen.addstr(f"{c}: ", curses.A_BOLD)
                standard_screen.addstr(f"{v}\n")
        except Exception as e:  # noqa: BLE001
            standard_screen.addstr(f"Error: {e}")

        standard_screen.addstr("\n-----------------------\nPress any key to abort")
        for k in range(updateinterval):
            time.sleep(1)
            standard_screen.addstr(0, 0, f"[Update in {updateinterval - k}s]       ")
            standard_screen.refresh()
            if standard_screen.getch() > 0:
                loop_monitor = False
                break

    curses.nocbreak()
    curses.echo()
    curses.endwin()


def vi_scan_function_call(commandname, functionrange):
    # scans the function call with all parameters and print HEX and decoded OUTPUT in terminal

    vo = ViControl()
    vo.initialize_communication()

    for func in functionrange:  # First Parameter is Byte
        print(f"==========Function # {func}===========")
        for day in range(6):
            try:
                print(vo.execFunctionCall(commandname, func, day).valueScan)
            except Exception:  # noqa: PERF203
                logger.exception("Exception on day %s.", day)
