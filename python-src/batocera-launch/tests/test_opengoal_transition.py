from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from batocera_common.asyncio import AsyncCompletedProcess
from batocera_launch.emulators import opengoal
from batocera_launch.emulators.opengoal import _GAMES, _SERIAL_GAMES, OpenGOAL
from batocera_launch.exceptions import BatoceraException
from batocera_launch.rom import Rom

if TYPE_CHECKING:
    from collections.abc import Callable

_OLD = 'v1.0.0'
_NEW = 'v1.0.1'


def _write_build(root: Path, game: str, release: str, /, *, iso_data: bool) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / 'opengoal-build.json').write_text(json.dumps({'game': game, 'release': release}))
    (root / 'out' / game / 'iso').mkdir(parents=True, exist_ok=True)
    (root / 'out' / game / 'iso' / 'KERNEL.CGO').write_text(release)
    if iso_data:
        (root / 'iso_data' / game / 'DGO').mkdir(parents=True)


class _Harness(OpenGOAL):
    def __init__(self, rom: Rom, base: Path, /) -> None:
        object.__setattr__(self, 'rom', rom)
        object.__setattr__(self, '_repacked', None)
        self._base = base

    @property
    def project_dir(self) -> Path:  # pyright: ignore[reportIncompatibleVariableOverride]
        return self._base / 'cache' / self.rom.id

    @property
    def data_dir(self) -> Path:  # pyright: ignore[reportIncompatibleVariableOverride]
        return self._base / 'roms' / self.rom.id


@pytest.fixture(params=_GAMES)
def game(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture
def base(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    release_file = tmp_path / 'shipped' / 'version'
    release_file.parent.mkdir()
    release_file.write_text(f'{_NEW}\n')
    monkeypatch.setattr(opengoal, '_RELEASE_FILE', release_file)
    monkeypatch.setattr(opengoal, '_SHIPPED_DATA', tmp_path / 'shipped')
    for directory in opengoal._RUNTIME_PROJECT_DIRS:
        (tmp_path / 'shipped' / directory).mkdir(parents=True)
    return tmp_path


def _fake_tools(monkeypatch: pytest.MonkeyPatch, *, mksquashfs_fails: bool = False) -> list[str]:
    calls: list[str] = []

    async def fake_run(cmd: str | Path, /, *args: str | Path, **_: object) -> AsyncCompletedProcess[bytes]:
        if Path(cmd).name == 'extractor':
            game = str(args[args.index('-g') + 1])
            calls.append(f'extractor {game}' + (' validated' if '-e' in args and '-v' in args else ''))
            project = Path(args[args.index('--proj-path') + 1])
            (project / 'out' / game / 'iso').mkdir(parents=True, exist_ok=True)
            (project / 'out' / game / 'iso' / 'KERNEL.CGO').write_text('rebuilt')
            return AsyncCompletedProcess(0, b'', b'')

        calls.append(Path(cmd).name)

        if mksquashfs_fails:
            return AsyncCompletedProcess(1, b'', b'No space left on device')

        Path(args[3]).write_text('\n'.join(str(source) for source in args[:3]))
        return AsyncCompletedProcess(0, b'', b'')

    monkeypatch.setattr(opengoal, 'run', fake_run)
    return calls


def _packed(base: Path, game: str, release: str, /) -> tuple[Rom, Callable[[], _Harness]]:
    source = base / 'roms' / f'{game}.squashfs'
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text('old image')
    mount = base / 'mnt' / source.stem
    _write_build(mount, game, release, iso_data=True)
    rom = Rom(source, mount)
    return rom, lambda: _Harness(rom, base)


class TestSquashfsFromAnOlderVersion:
    async def test_rebuilds_repacks_and_tidies_up(self, base: Path, game: str, monkeypatch: pytest.MonkeyPatch) -> None:
        calls = _fake_tools(monkeypatch)
        rom, harness = _packed(base, game, _OLD)
        emulator = harness()

        assert await emulator._resolve_game() == game
        assert calls == [f'extractor {game}', 'mksquashfs']

        assert rom.source.read_text().splitlines() == [
            str(rom / 'iso_data'),
            str(emulator.data_dir / 'out'),
            str(emulator.data_dir / 'opengoal-build.json'),
        ]
        assert not list(rom.source.parent.glob('.*.new'))

        assert (emulator.project_dir / 'out').resolve() == emulator.data_dir / 'out'
        emulator._drop_local_build(emulator._repacked)  # pyright: ignore[reportArgumentType]
        assert not emulator.data_dir.exists()

    async def test_a_failed_repack_still_plays_and_retries_without_rebuilding(
        self, base: Path, game: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _fake_tools(monkeypatch, mksquashfs_fails=True)
        rom, harness = _packed(base, game, _OLD)

        assert await harness()._resolve_game() == game
        assert rom.source.read_text() == 'old image'
        assert not list(rom.source.parent.glob('.*.new'))

        calls = _fake_tools(monkeypatch)
        assert await harness()._resolve_game() == game
        assert calls == ['mksquashfs']

    async def test_without_iso_data_it_cannot_rebuild(
        self, base: Path, game: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _fake_tools(monkeypatch)
        rom, harness = _packed(base, game, _OLD)
        for child in (rom / 'iso_data' / game).iterdir():
            child.rmdir()

        with pytest.raises(BatoceraException, match='no iso_data'):
            await harness()._resolve_game()


class TestSquashfsFromThisVersion:
    async def test_plays_straight_from_the_image(self, base: Path, game: str, monkeypatch: pytest.MonkeyPatch) -> None:
        calls = _fake_tools(monkeypatch)
        rom, harness = _packed(base, game, _NEW)
        emulator = harness()

        assert await emulator._resolve_game() == game
        assert calls == []
        assert (emulator.project_dir / 'out').resolve() == rom / 'out'

    async def test_clears_a_leftover_from_an_interrupted_repack(
        self, base: Path, game: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _fake_tools(monkeypatch)
        rom, harness = _packed(base, game, _NEW)
        emulator = harness()
        _write_build(emulator.data_dir, game, _NEW, iso_data=False)

        await emulator._resolve_game()

        assert not emulator.data_dir.exists()
        assert (emulator.project_dir / 'out').resolve() == rom / 'out'

    async def test_keeps_a_folder_that_carries_its_own_disc(
        self, base: Path, game: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _fake_tools(monkeypatch)
        _, harness = _packed(base, game, _NEW)
        emulator = harness()
        _write_build(emulator.data_dir, game, _NEW, iso_data=True)

        await emulator._resolve_game()

        assert (emulator.data_dir / 'opengoal-build.json').is_file()


def _unsupported_neighbour(serial: str, /) -> str:
    number = int(serial[5:])
    while (candidate := f'{serial[:5]}{number}') in _SERIAL_GAMES:
        number += 1
    return candidate


@pytest.mark.parametrize(('serial', 'disc_game'), sorted(_SERIAL_GAMES.items()))
class TestDiscImage:
    async def test_builds_then_plays_the_game_on_the_disc(
        self,
        base: Path,
        serial: str,
        disc_game: str,
        monkeypatch: pytest.MonkeyPatch,
        write_ps2_disc: Callable[..., Path],
    ) -> None:
        calls = _fake_tools(monkeypatch)
        iso = write_ps2_disc(base / 'roms' / f'{serial}.iso', serial)

        assert await _Harness(Rom(iso, None), base)._resolve_game() == disc_game
        assert calls == [f'extractor {disc_game} validated']

        calls.clear()
        assert await _Harness(Rom(iso, None), base)._resolve_game() == disc_game
        assert calls == []

    async def test_rebuilds_over_another_games_leftovers(
        self,
        base: Path,
        serial: str,
        disc_game: str,
        monkeypatch: pytest.MonkeyPatch,
        write_ps2_disc: Callable[..., Path],
    ) -> None:
        iso = write_ps2_disc(base / 'roms' / f'{serial}.iso', serial)

        for leftover in (game for game in _GAMES if game != disc_game):
            emulator = _Harness(Rom(iso, None), base)
            _write_build(emulator.data_dir, leftover, _NEW, iso_data=False)
            calls = _fake_tools(monkeypatch)

            assert await emulator._resolve_game() == disc_game
            assert calls == [f'extractor {disc_game} validated']


@pytest.mark.parametrize('serial', sorted(_SERIAL_GAMES))
async def test_rejects_the_unsupported_disc_next_to_each_supported_one(
    base: Path, serial: str, monkeypatch: pytest.MonkeyPatch, write_ps2_disc: Callable[..., Path]
) -> None:
    calls = _fake_tools(monkeypatch)
    unsupported = _unsupported_neighbour(serial)
    iso = write_ps2_disc(base / 'roms' / f'{unsupported}.iso', unsupported)

    with pytest.raises(BatoceraException, match=unsupported):
        await _Harness(Rom(iso, None), base)._resolve_game()

    assert calls == []


async def test_rejects_a_plain_folder(base: Path, game: str, monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _fake_tools(monkeypatch)
    folder = base / 'roms' / game
    _write_build(folder, game, _NEW, iso_data=True)

    with pytest.raises(BatoceraException, match='neither'):
        await _Harness(Rom(folder, None), base)._resolve_game()

    assert calls == []
