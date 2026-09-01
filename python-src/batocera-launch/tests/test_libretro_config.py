from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pytest

from batocera_launch.config.config import Config
from batocera_launch.config.libretro import LibretroConfig

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem

pytestmark = pytest.mark.usefixtures('fs')


@pytest.fixture
def config_data(request: pytest.FixtureRequest) -> dict[str, Any]:
    return getattr(request, 'param', {})


@pytest.fixture
def config(config_data: dict[str, Any]) -> Config:
    return Config(config_data)


@pytest.fixture
def config_path(request: pytest.FixtureRequest, fs: FakeFilesystem) -> Path:
    param = getattr(request, 'param', Path('/retroarch/custom.cfg'))

    if isinstance(param, tuple):
        path, content = cast('tuple[Path, str]', param)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    return Path(param) if isinstance(param, str) else param


@pytest.fixture
def retroconfig(config_path: Path, config: Config) -> LibretroConfig:
    return LibretroConfig(config_path, config)


class TestLibretroConfigSet:
    def test_quotes_string_values(self, retroconfig: LibretroConfig) -> None:
        retroconfig.set('input_enable_hotkey', 'shift')

        assert retroconfig.key_value_config['input_enable_hotkey'] == '"shift"'

    def test_quotes_none_as_empty_string(self, retroconfig: LibretroConfig) -> None:
        retroconfig.set('input_screenshot', None)

        assert retroconfig.key_value_config['input_screenshot'] == '""'

    def test_quotes_booleans_as_lowercase_strings(self, retroconfig: LibretroConfig) -> None:
        retroconfig.set('run_ahead_enabled', True)
        retroconfig.set('run_ahead_secondary_instance', False)

        assert retroconfig.key_value_config['run_ahead_enabled'] == '"true"'
        assert retroconfig.key_value_config['run_ahead_secondary_instance'] == '"false"'

    def test_quotes_numeric_values(self, retroconfig: LibretroConfig) -> None:
        retroconfig.set('input_player1_a_btn', 0)
        retroconfig.set('input_player1_l_y_plus_axis', '+1')

        assert retroconfig.key_value_config['input_player1_a_btn'] == '"0"'
        assert retroconfig.key_value_config['input_player1_l_y_plus_axis'] == '"+1"'


class TestLibretroConfigWrite:
    def test_writes_space_separated_file(self, retroconfig: LibretroConfig, config_path: Path) -> None:
        retroconfig.set('stella_console', 'auto')
        retroconfig.set('input_enable_hotkey', 'shift')
        retroconfig.write()

        assert (
            config_path.read_text()
            == """stella_console = "auto"
input_enable_hotkey = "shift"
"""
        )

    @pytest.mark.parametrize(
        'config_path',
        [Path('/userdata/system/configs/amiberry/custom/uae4arm-libretro.cfg')],
        indirect=True,
    )
    def test_creates_parent_directories(self, retroconfig: LibretroConfig, config_path: Path) -> None:
        retroconfig.set('key', 'value')
        retroconfig.write()

        assert config_path.is_file()
        assert config_path.parent.is_dir()


class TestLibretroConfigRead:
    _RETROARCH_CONFIG = """\
input_enable_hotkey = "shift"
input_menu_toggle = "f1"
video_smooth = true
input_player1_a_btn = "0"
global.shader = "crt"
"""

    @pytest.mark.parametrize(
        'config_path',
        [(Path('/retroarch/custom.cfg'), _RETROARCH_CONFIG)],
        indirect=True,
    )
    def test_reads_retroarch_config_on_init(self, retroconfig: LibretroConfig) -> None:
        assert retroconfig.key_value_config['input_enable_hotkey'] == '"shift"'
        assert retroconfig.key_value_config['input_menu_toggle'] == '"f1"'
        assert retroconfig.key_value_config['video_smooth'] == 'true'
        assert retroconfig.key_value_config['input_player1_a_btn'] == '"0"'
        assert retroconfig.key_value_config['global.shader'] == '"crt"'

    @pytest.mark.parametrize(
        'config_path',
        [(Path('/retroarch/custom.cfg'), 'existing = kept\n')],
        indirect=True,
    )
    def test_reads_unquoted_values(self, retroconfig: LibretroConfig) -> None:
        assert retroconfig.key_value_config['existing'] == 'kept'

    def test_missing_file_on_init_does_not_raise(self, config: Config) -> None:
        retroconfig = LibretroConfig(Path('/does/not/exist.cfg'), config)

        assert 'anything' not in retroconfig.key_value_config

    def test_write_read_roundtrip(self, retroconfig: LibretroConfig, config_path: Path, config: Config) -> None:
        retroconfig.set('input_enable_hotkey', 'shift')
        retroconfig.set('run_ahead_enabled', True)
        retroconfig.write()

        reloaded = LibretroConfig(config_path, config)

        assert reloaded.key_value_config['input_enable_hotkey'] == '"shift"'
        assert reloaded.key_value_config['run_ahead_enabled'] == '"true"'

    @pytest.mark.parametrize(
        'config_path',
        [(Path('/retroarch/custom.cfg'), 'from_file = "yes"\n')],
        indirect=True,
    )
    def test_preserves_read_keys_when_adding(self, retroconfig: LibretroConfig) -> None:
        retroconfig.set('added', 'value')

        assert retroconfig.key_value_config['from_file'] == '"yes"'
        assert retroconfig.key_value_config['added'] == '"value"'


class TestLibretroConfigFromConfig:
    @pytest.mark.parametrize('config_data', [{'stella_console': 'NTSC'}], indirect=True)
    def test_set_from_config(self, retroconfig: LibretroConfig) -> None:
        retroconfig.set_from_config('stella_console')

        assert retroconfig.key_value_config['stella_console'] == '"NTSC"'

    @pytest.mark.parametrize(
        'config_data',
        [{'internal_resolution_desmume': '512x384'}],
        indirect=True,
    )
    def test_set_from_config_with_config_name(self, retroconfig: LibretroConfig) -> None:
        retroconfig.set_from_config('desmume_internal_resolution', 'internal_resolution_desmume')

        assert retroconfig.key_value_config['desmume_internal_resolution'] == '"512x384"'

    def test_set_from_config_uses_default(self, retroconfig: LibretroConfig) -> None:
        retroconfig.set_from_config('stella_console', default='auto')

        assert retroconfig.key_value_config['stella_console'] == '"auto"'

    @pytest.mark.parametrize('config_data', [{'toggle_fast_forward': '1'}], indirect=True)
    def test_set_bool_from_config(self, retroconfig: LibretroConfig) -> None:
        retroconfig.set_bool_from_config('toggle_fast_forward')

        assert retroconfig.key_value_config['toggle_fast_forward'] == '"true"'

    @pytest.mark.parametrize('config_data', [{'default_vkbd_enabled': '0'}], indirect=True)
    def test_set_bool_from_config_return_values(self, retroconfig: LibretroConfig) -> None:
        retroconfig.set_bool_from_config(
            'default_vkbd_enabled',
            values=(1, 0),
        )

        assert retroconfig.key_value_config['default_vkbd_enabled'] == '"0"'

    @pytest.mark.parametrize('config_data', [{'amiberry_cpu_multiplier': '4'}], indirect=True)
    def test_set_int_from_config(self, retroconfig: LibretroConfig) -> None:
        retroconfig.set_int_from_config('amiberry_cpu_multiplier')

        assert retroconfig.key_value_config['amiberry_cpu_multiplier'] == '"4"'

    @pytest.mark.parametrize('config_data', [{'video_aspect_ratio': '1.333333'}], indirect=True)
    def test_set_float_from_config(self, retroconfig: LibretroConfig) -> None:
        retroconfig.set_float_from_config('video_aspect_ratio')

        assert retroconfig.key_value_config['video_aspect_ratio'] == '"1.333333"'


class TestLibretroConfigRemove:
    def test_remove_all_starting_with(self, retroconfig: LibretroConfig) -> None:
        retroconfig.set('input_player1_a_btn', 0)
        retroconfig.set('input_player2_a_btn', 1)
        retroconfig.set('input_menu_toggle', 'f1')

        retroconfig.remove_all_starting_with('input_player')

        assert 'input_player1_a_btn' not in retroconfig.key_value_config
        assert 'input_player2_a_btn' not in retroconfig.key_value_config
        assert retroconfig.key_value_config['input_menu_toggle'] == '"f1"'

    def test_remove_section(self, retroconfig: LibretroConfig) -> None:
        retroconfig.key_value_config['global.shader'] = 'crt'
        retroconfig.key_value_config['global.smooth'] = '1'
        retroconfig.key_value_config['global_extra'] = '2'

        retroconfig.remove_section('global')

        assert 'global.shader' not in retroconfig.key_value_config
        assert 'global.smooth' not in retroconfig.key_value_config
        assert retroconfig.key_value_config['global_extra'] == '2'
