from __future__ import annotations

import os
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from batocera_launch import Config, Rom, SystemConfig
from batocera_launch_wine import emulator as wine_emulator, wine

_DEFAULT_ROM = Path('/userdata/roms/windows/Game.wine')


@dataclass(slots=True, frozen=True)
class _StubSystemConfig(Config):
    """Only what the wine emulator asks of the system config it is given."""

    rom: Path = _DEFAULT_ROM
    core: str = ''


def _config(rom: Path | None = None, /, **options: str) -> SystemConfig:
    return cast(
        'SystemConfig',
        _StubSystemConfig(dict(options), rom=rom if rom is not None else _DEFAULT_ROM, core=options.get('core', '')),
    )


def _emulator(system: str = 'windows', rom: Path | None = None, /, **options: str) -> wine_emulator.Wine:
    """
    A Wine with only what a question asked of it needs: the launcher fills the rest in
    on its way to running a game, and none of it is worth building to ask.
    """
    emulator = object.__new__(wine_emulator.Wine)

    emulator.config = _config(rom, **options)
    emulator.system = system
    emulator.rom = Rom(rom if rom is not None else _DEFAULT_ROM, None)
    emulator._resources = ExitStack()
    emulator._runner = None

    return emulator


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('MZ')
    return path


@pytest.fixture
def quiet(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> list[list[str]]:
    commands: list[list[str]] = []
    monkeypatch.setattr(wine_emulator, '_run', commands.append)
    monkeypatch.setattr(wine_emulator, 'CACHE', tmp_path / 'cache')
    monkeypatch.setattr(wine_emulator, '_NVIDIA_CACHE_DIR', tmp_path / 'cache' / 'nvidia')
    return commands


class _StubRunner:
    def __init__(
        self,
        dxvk: list[str] | None = None,
        builtin: set[str] | None = None,
        *,
        forces_hidraw: bool = False,
    ) -> None:
        self._dxvk = dxvk or []
        self._builtin = builtin or set()
        self.forces_hidraw = forces_hidraw
        # the emulator's half of the decision, what the dlls become is the runner's
        self.nvapi: bool | None = None

    def install_dxvk(self, *, nvapi: bool = False) -> list[str]:
        self.nvapi = nvapi

        return list(self._dxvk)

    def install_builtin_d3d(self) -> set[str]:
        return self._builtin

    def install_d7vk(self, enabled: bool, /) -> bool:
        return enabled


def _stub_runner(*args: object, **kwargs: object) -> Any:
    """A stand-in for the runner, typed loosely so it can be handed to what wants a real one."""
    return _StubRunner(*args, **kwargs)  # pyright: ignore[reportArgumentType]


class TestWantedRunner:
    def test_the_setting_is_preferred(self) -> None:
        emulator = _emulator('windows', None, **{'wine-runner': 'wine-proton', 'core': 'wine-tkg'})

        assert emulator._wanted_runner == 'wine-proton'

    def test_the_core_is_the_fallback(self) -> None:
        assert _emulator('windows', None, core='wine-tkg')._wanted_runner == 'wine-tkg'

    def test_nothing_set_gives_nothing(self) -> None:
        assert _emulator()._wanted_runner == ''


def _identity(wanted: bool, /) -> bool:
    return wanted


def _accessible(path: object, mode: int, /) -> bool:
    return True


def _inaccessible(path: object, mode: int, /) -> bool:
    return False


def _ignored(command: list[str], /) -> None:
    return None


class TestWineOptions:
    def test_the_defaults_are_conservative(self, quiet: list[list[str]]) -> None:
        environment = wine_emulator._wine_options(_config(), _stub_runner())

        assert environment['WINEDEBUG'] == '-all'
        assert environment['PBA_ENABLE'] == '0'
        assert environment['DXVK_FRAME_RATE'] == '0'
        assert environment['WINE_FULLSCREEN_FSR'] == '0'

    def test_debug_turns_the_logging_on_and_the_silencing_off(self, quiet: list[list[str]]) -> None:
        environment = wine_emulator._wine_options(_config(wine_debug='1'), _stub_runner())

        assert environment['WINEDEBUG'] == 'err+all,fixme+all'
        assert 'DXVK_LOG_LEVEL' not in environment
        assert 'VKD3D_DEBUG' not in environment

    def test_fsr_is_turned_on_by_leaving_it_out(self, quiet: list[list[str]]) -> None:
        environment = wine_emulator._wine_options(_config(fsr='1'), _stub_runner())

        assert 'WINE_FULLSCREEN_FSR' not in environment

    def test_the_fps_limit_is_sixty(self, quiet: list[list[str]]) -> None:
        assert wine_emulator._wine_options(_config(fps_limit='1'), _stub_runner())['DXVK_FRAME_RATE'] == '60'

    @pytest.mark.parametrize(
        ('option', 'variable'),
        [
            ('pba', 'PBA_ENABLE'),
            ('allow_xim', 'WINE_ALLOW_XIM'),
            ('no_write_watch', 'WINE_DISABLE_WRITE_WATCH'),
            ('force_large_adress', 'WINE_LARGE_ADDRESS_AWARE'),
            ('heap_delay_free', 'WINE_HEAP_DELAY_FREE'),
            ('hide_nvidia_gpu', 'WINE_HIDE_NVIDIA_GPU'),
            ('wine_ntfs', 'NTFS_MODE'),
        ],
    )
    def test_each_switch_reaches_its_variable(self, quiet: list[list[str]], option: str, variable: str) -> None:
        assert wine_emulator._wine_options(_config(**{option: '1'}), _stub_runner())[variable] == '1'
        assert wine_emulator._wine_options(_config(**{option: '0'}), _stub_runner())[variable] == '0'

    def test_the_nvidia_cache_directory_is_made(self, quiet: list[list[str]], tmp_path: Path) -> None:
        wine_emulator._wine_options(_config(), _stub_runner())

        assert (tmp_path / 'cache' / 'nvidia').is_dir()

    def test_ntsync_is_on_unless_turned_off(self, quiet: list[list[str]], monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(wine_emulator, '_setup_ntsync', _identity)

        assert wine_emulator._wine_options(_config(), _stub_runner())['WINEDISABLEFASTSYNC'] == '0'
        assert wine_emulator._wine_options(_config(ntsync='0'), _stub_runner())['WINEDISABLEFASTSYNC'] == '1'


class TestSetupNtsync:
    def test_turning_it_off_unloads_the_module(self, monkeypatch: pytest.MonkeyPatch) -> None:
        commands: list[list[str]] = []
        monkeypatch.setattr(wine_emulator, '_run', commands.append)

        assert wine_emulator._setup_ntsync(False) is False
        assert commands == [['rmmod', 'ntsync']]

    def test_turning_it_on_loads_it_and_checks_the_device(self, monkeypatch: pytest.MonkeyPatch) -> None:
        commands: list[list[str]] = []
        monkeypatch.setattr(wine_emulator, '_run', commands.append)
        monkeypatch.setattr(os, 'access', _accessible)

        assert wine_emulator._setup_ntsync(True) is True
        assert commands == [['modprobe', 'ntsync']]

    def test_an_unusable_device_disables_it(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(wine_emulator, '_run', _ignored)
        monkeypatch.setattr(os, 'access', _inaccessible)

        assert wine_emulator._setup_ntsync(True) is False


class TestDxvkEnvironment:
    def test_dxvk_off_puts_the_wine_dlls_back_as_builtin(self, quiet: list[list[str]]) -> None:
        runner = _stub_runner(builtin={'d3d11', 'd3d9'})

        environment = wine_emulator._dxvk_environment(_config(dxvk='0'), runner)

        assert environment['DXVK_ASYNC'] == '0'
        assert 'd3d11,d3d9=b' in str(environment['WINEDLLOVERRIDES'])
        assert 'nvapi64,nvapi=' in str(environment['WINEDLLOVERRIDES'])

    def test_dxvk_on_overrides_the_graphics_dlls_as_native(self, quiet: list[list[str]]) -> None:
        runner = _stub_runner(dxvk=['d3d11,dxgi=n'])

        environment = wine_emulator._dxvk_environment(_config(dxvk='1'), runner)

        assert environment['DXVK_ASYNC'] == '1'
        assert 'd3d11,dxgi=n' in str(environment['WINEDLLOVERRIDES'])

    def test_the_start_menu_builder_is_left_to_the_prefix(self, quiet: list[list[str]]) -> None:
        # the game builds no start menu entries, what installs into the prefix does
        environment = wine_emulator._dxvk_environment(_config(), _stub_runner())

        assert 'winemenubuilder' not in str(environment['WINEDLLOVERRIDES'])

    def test_dxvk_asked_for_but_not_built_falls_back(self, quiet: list[list[str]]) -> None:
        environment = wine_emulator._dxvk_environment(_config(dxvk='1'), _stub_runner())

        assert environment['DXVK_ASYNC'] == '0'

    def test_reflex_forces_nvapi_on(self, quiet: list[list[str]]) -> None:
        environment = wine_emulator._dxvk_environment(_config(enable_vkreflex='1'), _stub_runner())

        assert environment['NVAPI'] == '1'
        assert environment['DXVK_ENABLE_NVAPI'] == '1'
        assert environment['DXVK_NVAPI_VKREFLEX'] == '1'
        assert 'DISABLE_DXVK_NVAPI_VKREFLEX' not in environment

    def test_without_reflex_the_layer_is_disabled(self, quiet: list[list[str]]) -> None:
        environment = wine_emulator._dxvk_environment(_config(), _stub_runner())

        assert environment['DISABLE_DXVK_NVAPI_VKREFLEX'] == '1'
        assert 'DXVK_NVAPI_VKREFLEX' not in environment

    def test_the_nvapi_setting_reaches_the_dlls(self, quiet: list[list[str]]) -> None:
        with_nvapi = _stub_runner(dxvk=['d3d11=n'])
        without = _stub_runner(dxvk=['d3d11=n'])

        wine_emulator._dxvk_environment(_config(dxvk='1', enable_nvapi='1'), with_nvapi)
        wine_emulator._dxvk_environment(_config(dxvk='1'), without)

        assert with_nvapi.nvapi is True
        assert without.nvapi is False

    def test_the_hud_is_off_unless_asked(self, quiet: list[list[str]]) -> None:
        assert 'DXVK_HUD' not in wine_emulator._dxvk_environment(_config(), _stub_runner())
        assert wine_emulator._dxvk_environment(_config(dxvk_hud='1'), _stub_runner())['DXVK_HUD'] == '1'

    def test_the_cache_can_be_reset(self, quiet: list[list[str]]) -> None:
        assert wine_emulator._dxvk_environment(_config(), _stub_runner())['DXVK_STATE_CACHE'] == '1'
        assert (
            wine_emulator._dxvk_environment(_config(dxvk_reset_cache='1'), _stub_runner())['DXVK_STATE_CACHE']
            == 'reset'
        )


class TestHidraw:
    def test_the_option_decides_when_it_is_set(self) -> None:
        runner = _stub_runner(forces_hidraw=True)

        assert wine_emulator._get_hidraw(_config(enable_hidraw='0'), runner) is False
        assert wine_emulator._get_hidraw(_config(enable_hidraw='1'), runner) is True

    def test_a_runner_that_forces_it_has_it_on_by_default(self) -> None:
        assert wine_emulator._get_hidraw(_config(), _stub_runner(forces_hidraw=True)) is True

    def test_any_other_runner_leaves_it_off(self) -> None:
        assert wine_emulator._get_hidraw(_config(), _stub_runner()) is False

    def test_it_reaches_the_variable_wine_reads(self, quiet: list[list[str]]) -> None:
        forced = wine_emulator._wine_options(_config(), _stub_runner(forces_hidraw=True))

        assert forced['WINE_ENABLE_HIDRAW'] == '1'
        assert wine_emulator._wine_options(_config(), _stub_runner())['WINE_ENABLE_HIDRAW'] == '0'

    def test_a_runner_that_forces_it_wants_a_sony_pad_to_look_like_xinput(self, quiet: list[list[str]]) -> None:
        forced = wine_emulator._wine_options(_config(), _stub_runner(forces_hidraw=True))

        assert forced['PROTON_SONY_HIDRAW_XINPUT'] == '1'
        assert 'PROTON_SONY_HIDRAW_XINPUT' not in wine_emulator._wine_options(_config(), _stub_runner())

    def test_turning_it_off_leaves_the_sony_pad_alone(self, quiet: list[list[str]]) -> None:
        forced = wine_emulator._wine_options(_config(enable_hidraw='0'), _stub_runner(forces_hidraw=True))

        assert 'PROTON_SONY_HIDRAW_XINPUT' not in forced


class TestD7vk:
    def test_it_is_off_unless_asked(self, quiet: list[list[str]]) -> None:
        environment = wine_emulator._dxvk_environment(_config(), _stub_runner())

        assert 'ddraw=n,b' not in str(environment['WINEDLLOVERRIDES'])

    def test_asking_for_it_overrides_ddraw(self, quiet: list[list[str]]) -> None:
        environment = wine_emulator._dxvk_environment(_config(d7vk='1'), _stub_runner())

        assert 'ddraw=n,b' in str(environment['WINEDLLOVERRIDES'])


class TestCopyInstallerSettings:
    @staticmethod
    def _conf(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, content: str) -> list[list[str]]:
        conf = tmp_path / 'batocera.conf'
        conf.write_text(content)
        monkeypatch.setattr(wine_emulator, 'BATOCERA_CONF', conf)
        commands: list[list[str]] = []
        monkeypatch.setattr(wine_emulator, '_run', commands.append)
        return commands

    def test_a_game_setting_follows_the_installed_game(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        commands = self._conf(tmp_path, monkeypatch, 'windows_installers["setup.exe"].dxvk=1\n')

        wine_emulator._copy_installer_settings('setup.exe', '260809-120000_setup.wine')

        assert commands == [['batocera-settings-set', 'windows["260809-120000_setup.wine"].dxvk', '1']]

    def test_another_installer_is_left_behind(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        commands = self._conf(tmp_path, monkeypatch, 'windows_installers["other.exe"].dxvk=1\n')

        wine_emulator._copy_installer_settings('setup.exe', '260809-120000_setup.wine')

        assert commands == []

    def test_settings_of_the_windows_system_are_not_touched(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        commands = self._conf(tmp_path, monkeypatch, 'windows["Game.wine"].dxvk=1\n')

        wine_emulator._copy_installer_settings('setup.exe', '260809-120000_setup.wine')

        assert commands == []

    def test_a_system_wide_installer_setting_becomes_a_system_wide_windows_one(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        commands = self._conf(tmp_path, monkeypatch, 'windows_installers.wine-runner=wine-proton\n')

        wine_emulator._copy_installer_settings('setup.exe', '260809-120000_setup.wine')

        assert commands == [['batocera-settings-set', 'windows.wine-runner', 'wine-proton']]


class TestEmulatorPaths:
    @pytest.mark.parametrize('name', ['setup.exe', 'image.iso', 'package.msi'])
    def test_an_installer_runs_from_where_it_sits(self, tmp_path: Path, name: str) -> None:
        rom = _touch(tmp_path / 'installers' / name)

        assert _emulator('windows', rom).execution_path == rom.parent

    def test_a_game_directory_runs_from_what_its_autorun_says(self, tmp_path: Path) -> None:
        rom = tmp_path / 'Game.pc'
        (rom / 'bin').mkdir(parents=True)
        (rom / 'autorun.cmd').write_text('DIR=bin\nCMD=game.exe\n')

        assert _emulator('windows', rom).execution_path == rom / 'bin'

    def test_a_squashed_rom_writes_into_its_own_bottle(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(wine, 'WINE_BOTTLES_DIR', tmp_path / 'bottles')
        monkeypatch.setattr(wine, 'WINE_BASE', tmp_path / 'usr')
        monkeypatch.setattr(wine, '_CUSTOM_RUNNERS', tmp_path / 'custom')
        rom = _touch(tmp_path / 'Game.wsquashfs')

        writable = _emulator('windows', rom).writable_overlayfs_dir

        assert writable == tmp_path / 'bottles' / 'windows' / 'wine-tkg' / 'Game.wsquashfs.wine'

    def test_the_bottle_follows_the_system(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(wine, 'WINE_BOTTLES_DIR', tmp_path / 'bottles')
        monkeypatch.setattr(wine, 'WINE_BASE', tmp_path / 'usr')
        monkeypatch.setattr(wine, '_CUSTOM_RUNNERS', tmp_path / 'custom')
        rom = _touch(tmp_path / 'Game.wsquashfs')

        writable = _emulator('mugen', rom).writable_overlayfs_dir

        assert writable.parent.parent.name == 'mugen'

    def test_a_wine_prefix_is_written_to(self) -> None:
        assert _emulator().needs_overlayfs is True

    def test_the_mouse_follows_the_setting(self) -> None:
        assert _emulator('windows', None, force_mouse='1').needs_mouse is True
        assert _emulator().needs_mouse is False


class TestHotkeys:
    @staticmethod
    def _prepared(prefix_dir: Path) -> wine_emulator.Wine:
        """A Wine whose prefix is already known, as it is once the rom is prepared."""
        emulator = _emulator()
        emulator._runner = cast(
            'wine.Runner',
            SimpleNamespace(prefix_dir=prefix_dir, wineserver=prefix_dir.parent / 'bin' / 'wineserver'),
        )
        return emulator

    def test_exiting_closes_the_wineserver_of_the_prefix(self, tmp_path: Path) -> None:
        context = self._prepared(tmp_path / 'Game.wine').hotkeygen_context

        assert context['name'] == 'wine'
        assert str(tmp_path / 'Game.wine') in context['keys']['exit']
        assert 'wineserver' in context['keys']['exit']
        assert '-k' in context['keys']['exit']

    def test_a_prefix_with_a_space_is_quoted(self, tmp_path: Path) -> None:
        assert "'" in self._prepared(tmp_path / 'My Game.wine').hotkeygen_context['keys']['exit']


class TestGenerateAutorunInInstalledPrefix:
    @staticmethod
    def _prefix(tmp_path: Path) -> Path:
        prefix = tmp_path / '260809-120000_setup.wine'
        prefix.mkdir()
        (prefix / 'system.reg').write_text('WINE REGISTRY Version 2\n')
        return prefix

    def _generate_autorun(self, prefix: Path) -> None:
        _emulator()._generate_autorun_in_installed_prefix(cast('wine.Runner', SimpleNamespace(prefix_dir=prefix)))

    def test_a_single_game_is_named_in_the_autorun(self, tmp_path: Path) -> None:
        prefix = self._prefix(tmp_path)
        _touch(prefix / 'drive_c' / 'Program Files' / 'Game' / 'game.exe')
        _touch(prefix / 'drive_c' / 'Program Files' / 'Game' / 'unins000.exe')

        self._generate_autorun(prefix)

        assert (prefix / 'autorun.cmd').read_text() == ('DIR=drive_c/Program Files/Game\nCMD="game.exe"\n')

    def test_several_candidates_leave_the_template(self, tmp_path: Path) -> None:
        prefix = self._prefix(tmp_path)
        for name in ('one.exe', 'two.exe'):
            _touch(prefix / 'drive_c' / 'Program Files' / 'Game' / name)

        self._generate_autorun(prefix)

        assert (prefix / 'autorun.cmd').read_text().startswith('#DIR=')

    def test_the_installation_drive_is_unlinked(self, tmp_path: Path) -> None:
        prefix = self._prefix(tmp_path)
        drive = prefix / 'dosdevices' / 'd:'
        drive.parent.mkdir()
        drive.symlink_to(tmp_path)

        self._generate_autorun(prefix)

        assert not drive.is_symlink()

    def test_an_installer_that_wrote_nothing_leaves_no_autorun(self, tmp_path: Path) -> None:
        prefix = tmp_path / 'empty.wine'
        prefix.mkdir()

        self._generate_autorun(prefix)

        assert not (prefix / 'autorun.cmd').exists()
