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

"""Tests the connection to Viessmann. Needs a physical connection."""

from pyvcontrol.vi_control import ViControl


def write_read():
    """Ändert einen Datensatz und stellt ursprüngl. Wert wieder her."""
    with ViControl() as vc:
        cmd = "RaumsolltempParty"
        v_orig = vc.execute_read_command(cmd).value

        vc.execute_write_command(cmd, v_orig + 1)
        vdr = vc.execute_read_command(cmd)
        print(f"Read {cmd} : {vdr.value}")
        assert v_orig + 1 == vdr.value

        vc.execute_write_command(cmd, v_orig)
        vdr = vc.execute_read_command(cmd)
        print(f"Read {cmd} : {vdr.value}")
        assert v_orig == vdr.value
