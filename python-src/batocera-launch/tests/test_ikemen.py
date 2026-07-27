from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pytest

from batocera_launch.emulators import ikemen
from batocera_launch.emulators.ikemen import Ikemen
from batocera_launch.types import Resolution
from batocera_launch_wine import wine

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import ModuleType


def _stub_runner(stub: _StubRunner, /) -> Any:
    def runner(*args: object, **kwargs: object) -> _StubRunner:
        return stub

    return runner


def _prime_path(marker: Path, /) -> Callable[[str], Path]:
    def path(name: str) -> Path:
        return marker if name == '/var/tmp/nvidia.prime' else Path(name)

    return path


class _StubRunner:
    """The prefix a windows ikemen game is played in, without the wine to build one."""

    def __init__(self, prefix_dir: Path, /, *, dxvk: list[str] | None = None) -> None:
        self.prefix_dir = prefix_dir
        self.wine = prefix_dir / 'bin' / 'wine'
        self.tricks: list[str] = []
        self.prepared = False
        self._dxvk = dxvk if dxvk is not None else ['d3d11=n', 'nvapi64=']

    def create_or_update_prefix(self) -> None:
        self.prepared = True

    def install_wine_trick(self, name: str, /) -> None:
        self.tricks.append(name)

    def install_dxvk(self, *, nvapi: bool = False) -> list[str]:
        return list(self._dxvk)

    def install_builtin_d3d(self) -> set[str]:
        return set()

    def get_environment(self) -> dict[str, str | Path]:
        return {'WINEPREFIX': self.prefix_dir}

    def game_command(self, game_exe: Path, /) -> list[str | Path]:
        return [self.wine, game_exe]


@pytest.fixture
def runner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> _StubRunner:
    stub = _StubRunner(tmp_path / 'bottles' / 'ikemen')
    monkeypatch.setattr(wine, 'Runner', _stub_runner(stub))
    return stub


class _StubConfig:
    """The options an ikemen game is launched with, all left at what they default to."""

    def get_bool(self, key: str, /, default: bool = False) -> bool:
        return default


def _emulator(rom: Path, /, *, width: int = 1920, height: int = 1080) -> Ikemen:
    """An Ikemen with only what a launch asks of it: the launcher fills in the rest."""
    emulator = object.__new__(Ikemen)

    emulator.rom = cast('Any', rom)
    emulator.resolution = Resolution(width, height)
    emulator.config = cast('Any', _StubConfig())
    emulator._runner = None

    return emulator


def _autorun(rom: Path, /) -> Path:
    rom.mkdir(parents=True, exist_ok=True)
    (rom / 'autorun.cmd').write_text('CMD=game.exe\n')
    (rom / 'game.exe').write_text('MZ')
    return rom


class TestWhatItRuns:
    def test_a_game_with_no_engine_of_its_own_runs_the_one_batocera_builds(self, tmp_path: Path) -> None:
        (rom := tmp_path / 'Game.ikemen').mkdir()

        assert _emulator(rom)._linux_binary == Path('/usr/bin/ikemen')

    def test_the_engine_a_game_ships_is_preferred(self, tmp_path: Path) -> None:
        (rom := tmp_path / 'Game.ikemen').mkdir()
        # a game packs it under whichever case it likes
        (binary := rom / 'Ikemen_GO_Linux').write_text('')
        binary.chmod(0o755)

        assert _emulator(rom)._linux_binary == binary

    def test_an_engine_that_cannot_be_run_is_made_runnable(self, tmp_path: Path) -> None:
        (rom := tmp_path / 'Game.ikemen').mkdir()
        (binary := rom / 'ikemen_go_linux').write_text('')
        binary.chmod(0o644)

        assert _emulator(rom)._linux_binary == binary
        assert os.access(binary, os.X_OK)

    def test_a_game_saying_it_is_a_windows_one_has_no_linux_engine_to_run(self, tmp_path: Path) -> None:
        rom = _autorun(tmp_path / 'Game.ikemen')

        assert _emulator(rom)._windows_exe is not None

    def test_any_other_game_is_a_linux_one(self, tmp_path: Path) -> None:
        (rom := tmp_path / 'Game.ikemen').mkdir()

        assert _emulator(rom)._wine is None
        assert _emulator(rom)._windows_exe is None


class TestWineCommand:
    @staticmethod
    def _command(tmp_path: Path) -> Any:
        rom = _autorun(tmp_path / 'Game.ikemen')

        return _emulator(rom)._wine_command(cast('ModuleType', wine), Path('game.exe'))

    def test_the_game_is_run_through_the_wine_of_its_prefix(self, tmp_path: Path, runner: _StubRunner) -> None:
        command = self._command(tmp_path)

        assert command.args == [runner.wine, Path('game.exe')]
        assert runner.prepared

    def test_the_tricks_a_windows_ikemen_needs_are_installed(self, tmp_path: Path, runner: _StubRunner) -> None:
        self._command(tmp_path)

        assert runner.tricks == ['openal', 'corefonts']

    def test_the_game_draws_through_dxvk(self, tmp_path: Path, runner: _StubRunner) -> None:
        command = self._command(tmp_path)

        assert command.env['DXVK_ASYNC'] == '1'
        assert command.env['WINEDLLOVERRIDES'] == 'd3d11=n;nvapi64='
        assert command.env['DXVK_STATE_CACHE_PATH'] == Path('/userdata/system/cache')

    def test_the_game_is_given_the_environment_of_its_prefix(self, tmp_path: Path, runner: _StubRunner) -> None:
        command = self._command(tmp_path)

        assert command.env['WINEPREFIX'] == runner.prefix_dir


class TestNvidiaPrime:
    @staticmethod
    def _prime(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, /, *, laptop: bool) -> None:
        marker = tmp_path / 'nvidia.prime'
        if laptop:
            marker.write_text('pci-0000_01_00_0')
        monkeypatch.setattr(ikemen, 'Path', _prime_path(marker))

    def test_a_native_game_is_offloaded_onto_the_nvidia_card(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        self._prime(monkeypatch, tmp_path, laptop=True)
        (rom := tmp_path / 'Game.ikemen').mkdir()

        command = asyncio.run(_emulator(rom).configure())

        assert command.env['__NV_PRIME_RENDER_OFFLOAD'] == '1'
        assert command.env['__GLX_VENDOR_LIBRARY_NAME'] == 'nvidia'
        # the engine batocera builds is 64bit, unlike a game running in a prefix
        assert 'i686' not in str(command.env['VK_ICD_FILENAMES'])

    def test_a_windows_game_is_given_what_any_wine_game_is(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path, runner: _StubRunner
    ) -> None:
        self._prime(monkeypatch, tmp_path, laptop=True)
        monkeypatch.setattr(wine, 'Path', _prime_path(tmp_path / 'nvidia.prime'))
        rom = _autorun(tmp_path / 'Game.ikemen')

        command = _emulator(rom)._wine_command(cast('ModuleType', wine), Path('game.exe'))

        # the offload of the session is what a game in a prefix does not want
        assert '__NV_PRIME_RENDER_OFFLOAD' not in command.env
        assert 'i686' in str(command.env['VK_ICD_FILENAMES'])

    def test_anything_that_is_not_a_prime_laptop_is_left_as_it_is(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        self._prime(monkeypatch, tmp_path, laptop=False)
        (rom := tmp_path / 'Game.ikemen').mkdir()

        command = asyncio.run(_emulator(rom).configure())

        assert '__NV_PRIME_RENDER_OFFLOAD' not in command.env
        assert 'VK_ICD_FILENAMES' not in command.env


class TestConfigFiles:
    def test_a_json_config_carries_the_screen_and_the_controls(self, tmp_path: Path) -> None:
        (rom := tmp_path / 'Game.ikemen').mkdir()
        config = rom / 'save' / 'config.json'

        _emulator(rom)._write_json_config(config, scale_internal_resolution=False)

        written = json.loads(config.read_text())

        assert written['Fullscreen'] is True
        assert (written['FullscreenWidth'], written['FullscreenHeight']) == (1920, 1080)
        assert len(written['KeyConfig']) == 4
        assert 'GameWidth' not in written

    def test_scaling_renders_at_the_screen_resolution(self, tmp_path: Path) -> None:
        (rom := tmp_path / 'Game.ikemen').mkdir()
        config = rom / 'save' / 'config.json'

        _emulator(rom)._write_json_config(config, scale_internal_resolution=True)

        assert json.loads(config.read_text())['GameWidth'] == 1920

    def test_a_json_config_we_cannot_read_is_left_as_it_is(self, tmp_path: Path) -> None:
        (rom := tmp_path / 'Game.ikemen').mkdir()
        (config := rom / 'save' / 'config.json').parent.mkdir()
        config.write_text('not json at all')

        _emulator(rom)._write_json_config(config, scale_internal_resolution=False)

        assert config.read_text() == 'not json at all'

    def test_an_ini_config_is_rewritten_where_it_stands(self, tmp_path: Path) -> None:
        (rom := tmp_path / 'Game.ikemen').mkdir()
        (config := rom / 'save' / 'config.ini').parent.mkdir()
        config.write_text('[Video]\nFullscreen= 0\nWindowWidth= 640\nKeep= me\n[Keys_P1]\nup= OLD\n')

        _emulator(rom)._write_ini_config(config, scale_internal_resolution=False)

        written = config.read_text()

        assert 'Fullscreen= 1' in written
        assert 'WindowWidth= 1920' in written
        assert 'up= UP' in written
        # what the game keeps in there is its own
        assert 'Keep= me' in written
