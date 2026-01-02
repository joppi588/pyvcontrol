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


def test_writesequence():
    """Ändert einen Datensatz und stellt ursprüngl. Wert wieder her."""
    vc = ViControl()
    vc.initialize_communication()
    cmd = "RaumsolltempParty"
    original_value = vc.execute_read_command(cmd).value
    print(f"Original value: {original_value}")

    vc.execute_write_command(cmd, original_value + 1)
    new_value = vc.execute_read_command(cmd).value
    print(f"Wrote {cmd}={original_value + 1}; result={new_value}")
    assert original_value + 1 == new_value

    vc.execute_write_command(cmd, original_value)
    original_value_restored = vc.execute_read_command(cmd)
    print(f"Restored {cmd} -> {original_value_restored}")
    assert original_value == original_value_restored


if __name__ == "__main__":
    test_writesequence()
