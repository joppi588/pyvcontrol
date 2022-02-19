# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
# Copyright 2021 Jochen Schmähling
# ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ## ##
#  Tools for communication with viControl heatings using the serial Optolink interface
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

from pyvcontrol.viControl import viControl, viTelegram, ctrlcode, viControlException
import logging
import curses
import time



def viscancommands(addressrange):
    # brute force command scanner
    # hilft v.a. um die richtige Payload-Länge für bekannte Kommandos herauszufinden

    logging.basicConfig(filename='scancommands.log', filemode='w', level=logging.DEBUG)

    vo = viControl()
    vo.initComm()

    for addr in addressrange:
        for kk in range(1,5):
            # TODO: Inneren Teil ausschneiden und in separate Funktion? ("low level read command")
            logging.debug(f'---{hex(addr)}-{kk}------------------')
            vc = addr.to_bytes(2,'big')+kk.to_bytes(1,'big')
            vt = viTelegram(vc, 'read')  # create read Telegram
            vo.vs.send(vt)                    # send Telegram
            logging.debug(f'Send telegram {vt.hex()}')

            try:
                # Check if sending was successfull
                ack=vo.vs.read(1)
                if ack!=ctrlcode['acknowledge']:
                    logging.debug(f'Viessmann returned {ack.hex()}')
                    vo.initComm()
                    raise viControlException(f'Expected acknowledge byte, received {ack}')

                # Receive response and evaluate data
                vr1 = vo.vs.read(2)  # receive response
                vr2 = vo.vs.read(vr1[1]+1) # read rest of telegram
                # FIXME: create Telegram instead of low-level access (for better readability)
                logging.debug(f'received telegram {vr1.hex()} {vr2.hex()}')

                if vr2[0].to_bytes(1,'little') == viTelegram.tTypes['response']:
                    v=int.from_bytes(vr2[-1-kk:-1],'little')
                    print(f'Found working command 0x{hex(addr)}, payload length {kk}, value {v}')


            except Exception as e:
                logging.error({e})
                print(f'An exception occurred: {e}')


def vimonitor(commandlist, updateinterval=30):
# repeatedly executes commands
# commandlist is a list of strings (command names from viCommand)

# TODO: accept also addresses & length as commands
# Option 1) "Generic command" based on addr and length 2) add command to command set first
    if not isinstance(commandlist,list):
        # wrap single commands into a list
        commandlist=[commandlist]

    logging.basicConfig(filename='Monitor.log', filemode='w', level=logging.DEBUG)
    vo = viControl()

    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.nodelay(True)

    loop_monitor = True
    while loop_monitor:
        stdscr.clear()
        stdscr.addstr(0,0,'Reading values...')
        stdscr.refresh()
        stdscr.addstr(1,0,"--- Viessmann monitor ---\n")
        try:
            vo.initComm()
            for c in commandlist:
                v = vo.execReadCmd(c).value
                stdscr.addstr(f"{c}: " , curses.A_BOLD)
                stdscr.addstr(f"{v}\n")
        except Exception as e:
            stdscr.addstr(f'Error: {e}')

        stdscr.addstr('\n-----------------------\nPress any key to abort')
        for k in range(updateinterval):
            time.sleep(1)
            stdscr.addstr(0,0,f"[Update in {updateinterval-k}s]       ")
            stdscr.refresh()
            if stdscr.getch() > 0:
                loop_monitor = False
                break

    curses.nocbreak()
    curses.echo()
    curses.endwin()