from __future__ import annotations

from pathlib import Path

import pytest

from batocera_common.key_value_config import KeyValueConfig
from batocera_common.paths import BATOCERA_CONF, SYSCONFIG
from batocera_common.settings import board_model, get_master_setting

pytestmark = pytest.mark.usefixtures('fs')

_DEVICETREE_MODEL = Path('/sys/firmware/devicetree/base/model')
_DMI_PRODUCT_NAME = Path('/sys/devices/virtual/dmi/id/product_name')
_DMI_BOARD_NAME = Path('/sys/devices/virtual/dmi/id/board_name')


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


class TestBoardModel:
    def test_none_without_sysfs(self) -> None:
        assert board_model() is None

    def test_devicetree_model_is_sanitised(self) -> None:
        _write(_DEVICETREE_MODEL, 'Anbernic RG-DS Plus\0')

        assert board_model() == 'Anbernic_RG_DS_Plus'

    def test_dmi_product_name(self) -> None:
        _write(_DMI_PRODUCT_NAME, 'ROG Ally RC71L_RC71L\n')

        assert board_model() == 'ROG_Ally_RC71L_RC71L'

    def test_default_string_falls_back_to_board_name(self) -> None:
        _write(_DMI_PRODUCT_NAME, 'Default string\n')
        _write(_DMI_BOARD_NAME, 'B550M DS3H\n')

        assert board_model() == 'B550M_DS3H'


class TestGetMasterSetting:
    def test_user_value_wins(self) -> None:
        _write(BATOCERA_CONF, 'system.cpu.governor=ondemand\n')
        _write(SYSCONFIG, 'system.cpu.governor=performance\n')

        assert get_master_setting('system.cpu.governor') == 'ondemand'

    @pytest.mark.parametrize('value', ['auto', ''])
    def test_auto_and_empty_fall_through(self, value: str) -> None:
        _write(BATOCERA_CONF, f'system.cpu.governor={value}\n')
        _write(SYSCONFIG, 'system.cpu.governor=performance\n')

        assert get_master_setting('system.cpu.governor') == 'performance'

    def test_board_config_beats_general(self) -> None:
        _write(BATOCERA_CONF, '')
        _write(_DEVICETREE_MODEL, 'Raspberry Pi 4 Model B Rev 1.4')
        _write(SYSCONFIG.with_name('batocera.conf.Raspberry_Pi_4_Model_B_Rev_1_4'), 'system.cpu.governor=performance\n')
        _write(SYSCONFIG, 'system.cpu.governor=schedutil\n')

        assert get_master_setting('system.cpu.governor') == 'performance'

    def test_missing_everywhere(self) -> None:
        _write(BATOCERA_CONF, 'global.powermode=balanced\n')

        assert get_master_setting('system.cpu.governor') is None

    def test_given_user_config_is_used(self) -> None:
        config = KeyValueConfig()
        config['global.powermode'] = 'balanced'

        assert get_master_setting('global.powermode', user_config=config) == 'balanced'
