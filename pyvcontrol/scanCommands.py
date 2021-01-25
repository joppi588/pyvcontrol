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

#brute force command scanner
#hilft nicht viel da es sehr viele funktionierende Kommandos gibt.

from pyvcontrol.viControl import viSerial,viControl,viControlCode,viControlException
from pyvcontrol.viCommand import viCommand
from pyvcontrol.viTelegram import viTelegram
import logging

tModes={3:'Error',1:'valid response'}
addressrange = range(0x1640, 0x1690)  # loop addresses


def runScanner():
    vo = viControl()
    vo.initComm()
    #vc=viCommand('Betriebsart') #Create command, overwrite contents later

    for addr in addressrange:
        for kk in range(1,5):
            logging.debug(f'---{hex(addr)}-{kk}------------------')
            vc=addr.to_bytes(2,'big')+kk.to_bytes(1,'big')
            vt = viTelegram(vc, 'read')  # create read Telegram
            vo.vs.send(vt)                    # send Telegram
            logging.debug(f'Send telegram {vt.hex()}')

            try:
                # Check if sending was successfull
                ack=vo.vs.read(1)
                if ack!=viControlCode('Acknowledge'):
                    logging.debug(f'Viessmann returned {ack.hex()}')
                    vo.initComm()
                    raise viControlException(f'Expected acknowledge byte, received {ack}')

                # Receive response and evaluate data
                vr1 = vo.vs.read(2)  # receive response
                vr2 = vo.vs.read(vr1[1]+1) # read rest of telegram
                logging.debug(f'received telegram {vr1.hex()} {vr2.hex()}')

                if vr2[0]==1:
                    v=int.from_bytes(vr2[-1-kk:-1],'little')
                    print(f'Found working command 0x{hex(addr)}, payload length {kk}, value {v}')
                    break

            except Exception as e:
                print(f'An exception occurred: {e}')

if __name__ == '__main__':
    logging.basicConfig(filename='scanCommands.log', filemode='w', level=logging.DEBUG)
    runScanner()