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

# Tests the connection to Viessmann. Needs a physical connection

import unittest
import logging
from pyvcontrol.viControl import viControl
from pyvcontrol.viCommand import viCommand
from pyvcontrol.viTools import viscancommands, viscanFuncionCall



class MyTestCase(unittest.TestCase):
    
    
    def test_readsequence(self):
        vo = viControl()
        vo.initComm()

        for cmd, values in viCommand.commandset.items():
            # exclude the func commands ... they will raise an error (default behavior)
            if values.get('func', False):
                    continue
            vd = vo.execReadCmd(cmd)
            print(f'{cmd} : {vd.value} : raw {vd.hex()}')

    
    def test_readonly(self):
        pass

    
    def test_writesequence(self):
        # Ändert einen Datensatz und stellt ursprüngl. Wert wieder her
        vo = viControl()
        vo.initComm()
        cmd = 'SolltempWarmwasser'
        v_orig = vo.execReadCmd(cmd).value

        vdw = vo.execWriteCmd(cmd, v_orig+2)
        vdr = vo.execReadCmd(cmd)
        print(f'Read {cmd} : {vdr.value}')
        self.assertEqual(v_orig+2, vdr.value)

        
        vdw = vo.execWriteCmd(cmd, v_orig)
        vdr = vo.execReadCmd(cmd)
        print(f'Read {cmd} : {vdr.value}')
        self.assertEqual(v_orig, vdr.value)
    

    def test_functioncall(self):
        # Funktion zu Energiebilanz aufrufen ... bringt fehler bei Vitocal 333G
        vo = viControl()
        vo.initComm()
        
        cmd = 'Energiebilanz'
        
        # kumulierte Summe je Tag, der letzten Tage
        print (vo.execFunctionCall(cmd, 2,0).value)
        print (vo.execFunctionCall(cmd, 2,1).value)
        print (vo.execFunctionCall(cmd, 2,3).value)
        print (vo.execFunctionCall(cmd, 2,4).value)
        print (vo.execFunctionCall(cmd, 2,5).value)
        print (vo.execFunctionCall(cmd, 2,6).value)


    

if __name__ == '__main__':
    logging.basicConfig(filename='testViessmann.log', filemode='w', level=logging.DEBUG)
    unittest.main()
    #viscancommands(range(0x0000, 0xA00F))
    #viscanFuncionCall('Energiebilanz', range(0,12+1)) # after Number 12 there ar only ERROR  
    
