import pytest

from pyvcontrol.vi_command import COMMAND_SETS


@pytest.fixture
def commands_wo1c():
    return COMMAND_SETS["WO1C"]
