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


import pytest

from pyvcontrol.vi_access_mode import AccessMode


@pytest.mark.parametrize(
    "mode1,mode2,result",
    [
        (AccessMode.READ, AccessMode.WRITE, False),
        (AccessMode.WRITE, AccessMode.READ, True),
        (AccessMode.CALL, AccessMode.READ, False),
        (AccessMode.CALL, AccessMode.CALL, True),
    ],
)
def test_access_mode_allows(mode1, mode2, result):
    # GIVEN Two access modes
    # WHEN Check if first allows second
    # THEN result as expected
    assert mode1.allows(mode2) == result
