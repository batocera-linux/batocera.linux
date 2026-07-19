from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import pytest

from batocera_launch.emulators.mugen import Mugen, get_mugen_version
from batocera_launch.exceptions import BatoceraException
from batocera_launch.types import Resolution
from batocera_launch_wine import wine

if TYPE_CHECKING:
    from batocera_launch.command import Command


def _stub_default(stub: _StubRunner, /) -> Any:
    def default(cls: type[wine.Runner], name: str, /) -> _StubRunner:
        return stub

    return classmethod(default)


def _game_exe(rom: Path) -> Path:
    return Path('game.exe')


def _game_dir(rom: Path) -> Path:
    return Path(rom)


class _StubRunner:
    """The prefix a mugen game is played in, without the wine that would build one."""

    def __init__(self, prefix_dir: Path, /, *, dxvk: list[str] | None = None) -> None:
        self.prefix_dir = prefix_dir
        self.wineserver = prefix_dir / 'bin' / 'wineserver'
        self.wine = prefix_dir / 'bin' / 'wine'
        self.tricks: list[str] = []
        self.prepared = False
        self.stopped = False
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

    def stop(self) -> None:
        self.stopped = True


@pytest.fixture
def runner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> _StubRunner:
    stub = _StubRunner(tmp_path / 'bottles' / 'mugen')
    monkeypatch.setattr(wine.Runner, 'default', _stub_default(stub))
    monkeypatch.setattr(wine, 'get_game_exe', _game_exe)
    monkeypatch.setattr(wine, 'get_game_dir', _game_dir)
    return stub


def _emulator(rom: Path, /, *, width: int = 1920, height: int = 1080) -> Mugen:
    """A Mugen with only what a launch asks of it: the launcher fills in the rest."""
    emulator = object.__new__(Mugen)

    emulator.rom = cast('Any', rom)
    emulator.resolution = Resolution(width, height)
    emulator._runner = None
    cast('Any', Mugen._wine.slot_descriptor).__set__(emulator, wine)

    return emulator


def _cfg(rom: Path, content: str, /) -> Path:
    (rom / 'data').mkdir(parents=True, exist_ok=True)
    settings = rom / 'data' / 'mugen.cfg'
    settings.write_text(content, encoding='utf-8-sig')
    return settings


_NEW_CFG = '; a comment\n[Video]\nFullScreen = 0\nWidth = 640\nHeight = 480\nKeep = me\n'
_OLD_CFG = '[Video Win]\nFullScreen = 0\nWidth = 320\n'


class TestMugenVersion:
    def test_a_video_win_section_is_what_an_old_engine_has(self, tmp_path: Path) -> None:
        assert get_mugen_version(_cfg(tmp_path / 'Old.pc', _OLD_CFG)) == 'old'

    def test_anything_else_is_a_new_one(self, tmp_path: Path) -> None:
        assert get_mugen_version(_cfg(tmp_path / 'Game.pc', _NEW_CFG)) == 'new'


class TestWriteConfig:
    def test_a_new_engine_is_given_the_screen_and_the_controls(self, tmp_path: Path) -> None:
        settings = _cfg(rom := tmp_path / 'Game.pc', _NEW_CFG)

        _emulator(rom)._write_config()

        written = settings.read_text(encoding='utf-8-sig')

        assert 'FullScreen = 1' in written
        assert 'Width = 1920' in written
        assert 'Height = 1080' in written
        assert '[P1 Keys]' in written

    def test_an_old_engine_stays_at_the_size_it_can_do(self, tmp_path: Path) -> None:
        settings = _cfg(rom := tmp_path / 'Old.pc', _OLD_CFG)

        _emulator(rom)._write_config()

        written = settings.read_text(encoding='utf-8-sig')

        assert 'Width = 640' in written
        assert 'DXmode = Hardware' in written

    def test_what_the_game_keeps_in_there_is_left_alone(self, tmp_path: Path) -> None:
        settings = _cfg(rom := tmp_path / 'Game.pc', _NEW_CFG)

        _emulator(rom)._write_config()

        written = settings.read_text(encoding='utf-8-sig')

        assert '; a comment' in written
        assert 'Keep = me' in written

    def test_a_game_without_one_is_not_playable(self, tmp_path: Path) -> None:
        (rom := tmp_path / 'None.pc').mkdir()

        with pytest.raises(BatoceraException):
            _emulator(rom)._write_config()


class TestConfigure:
    @staticmethod
    def _configure(tmp_path: Path) -> Command:
        _cfg(rom := tmp_path / 'Game.pc', _NEW_CFG)

        return asyncio.run(_emulator(rom).configure())

    def test_the_game_is_run_through_the_wine_of_its_prefix(self, tmp_path: Path, runner: _StubRunner) -> None:
        command = self._configure(tmp_path)

        assert command.args == [runner.wine, Path('game.exe')]
        assert runner.prepared

    def test_the_sound_trick_some_games_need_is_installed(self, tmp_path: Path, runner: _StubRunner) -> None:
        self._configure(tmp_path)

        assert runner.tricks == ['openal']

    def test_the_game_is_given_the_environment_of_its_prefix(self, tmp_path: Path, runner: _StubRunner) -> None:
        command = self._configure(tmp_path)

        assert command.env['WINEPREFIX'] == runner.prefix_dir

    def test_the_game_draws_through_dxvk(self, tmp_path: Path, runner: _StubRunner) -> None:
        command = self._configure(tmp_path)

        assert command.env['DXVK_ASYNC'] == '1'
        assert command.env['WINEDLLOVERRIDES'] == 'd3d11=n;nvapi64='

    def test_the_shader_cache_goes_with_the_other_caches(self, tmp_path: Path, runner: _StubRunner) -> None:
        # not beside the game, which for a squashed rom is the overlay
        command = self._configure(tmp_path)

        assert command.env['DXVK_STATE_CACHE_PATH'] == Path('/userdata/system/cache')

    def test_a_prefix_without_dxvk_is_put_back_on_the_wined3d_of_wine(
        self, tmp_path: Path, runner: _StubRunner
    ) -> None:
        runner._dxvk = []

        command = self._configure(tmp_path)

        assert command.env['DXVK_ASYNC'] == '0'
        assert command.env['WINEDLLOVERRIDES'] == 'nvapi64,nvapi='


class TestHooks:
    def test_a_squashed_rom_needs_the_overlay(self, tmp_path: Path, runner: _StubRunner) -> None:
        assert _emulator(tmp_path / 'Game.pc').needs_overlayfs is True

    def test_the_rendered_display_matches_the_screen(self, tmp_path: Path, runner: _StubRunner) -> None:
        assert _emulator(tmp_path / 'Game.pc').in_game_ratio == 16 / 9

    def test_exiting_closes_the_wineserver_of_the_prefix(self, tmp_path: Path, runner: _StubRunner) -> None:
        context = _emulator(tmp_path / 'Game.pc').hotkeygen_context

        assert context['name'] == 'mugen'
        assert str(runner.prefix_dir) in context['keys']['exit']
        assert '-k' in context['keys']['exit']
