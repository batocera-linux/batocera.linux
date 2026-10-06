from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

import pytest
from pytest_batocera import write_ps2_disc

from batocera_common.asyncio import AsyncCompletedProcess
from batocera_common.dataclasses import cached_dataclass
from batocera_common.paths import CACHE, ROMS, SQUASHFS_DIR
from batocera_launch.emulators.opengoal import (
    _BUILD_MARKER,
    _GAMES,
    _INSTALL_DIR,
    _RELEASE_FILE,
    _RUNTIME_PROJECT_DIRS,
    _SERIAL_GAMES,
    _SHIPPED_DATA,
    OpenGOAL,
)
from batocera_launch.exceptions import BatoceraException
from batocera_launch.rom import Rom

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem
    from pytest_batocera import MockSystemConfig
    from pytest_mock import MockerFixture

    from batocera_launch import SystemConfig

_OLD = 'v1.0.0'
_NEW = 'v1.0.1'

pytestmark = [pytest.mark.usefixtures('fs'), pytest.mark.launch_config_system('opengoal')]


@pytest.fixture
def fs(fs: FakeFilesystem) -> None:
    fs.makedirs(str(_SHIPPED_DATA))

    _RELEASE_FILE.write_text(f'{_NEW}\n')

    for directory in _RUNTIME_PROJECT_DIRS:
        _SHIPPED_DATA.joinpath(directory).mkdir(parents=True, exist_ok=True)


def _write_build(root: Path, game: str, release: str, /, *, iso_data: bool) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / 'opengoal-build.json').write_text(json.dumps({'game': game, 'release': release}))
    (root / 'out' / game / 'iso').mkdir(parents=True, exist_ok=True)
    (root / 'out' / game / 'iso' / 'KERNEL.CGO').write_text(release)
    if iso_data:
        (root / 'iso_data' / game / 'DGO').mkdir(parents=True)


@cached_dataclass
class _Harness(OpenGOAL):
    def __init__(self, config: SystemConfig, rom: Rom, /) -> None:
        self.config = config
        self.rom = rom
        self._repacked = None

        OpenGOAL.__post_init__(self)


@pytest.fixture(params=_GAMES)
def game(request: pytest.FixtureRequest) -> str:
    return request.param


@pytest.fixture
def game_release(request: pytest.FixtureRequest) -> str:
    return getattr(request, 'param', _OLD)


@pytest.fixture
def mock_run(mocker: MockerFixture, request: pytest.FixtureRequest) -> AsyncMock:
    mksquashfs_fails = getattr(request, 'param', False)

    async def side_effect(cmd: str | Path, /, *args: str | Path, **_: object) -> AsyncCompletedProcess[bytes]:
        if Path(cmd).name == 'extractor':
            game = str(args[args.index('-g') + 1])
            project = Path(args[args.index('--proj-path') + 1])
            (project / 'out' / game / 'iso').mkdir(parents=True, exist_ok=True)
            (project / 'out' / game / 'iso' / 'KERNEL.CGO').write_text('rebuilt')

            return AsyncCompletedProcess(0, b'', b'')

        if mksquashfs_fails or mock.__force_fail__:
            return AsyncCompletedProcess(1, b'', b'No space left on device')

        Path(args[3]).write_text('\n'.join(str(source) for source in args[:3]))
        return AsyncCompletedProcess(0, b'', b'')

    mock = mocker.patch('batocera_launch.emulators.opengoal.run', new_callable=AsyncMock, side_effect=side_effect)

    mock.__force_fail__ = False

    return mock


@pytest.fixture
def packed_launch_rom(fs: FakeFilesystem, launch_config_system: str, game: str, game_release: str) -> Rom:
    rom = Rom(ROMS / launch_config_system / f'{game}.squashfs', SQUASHFS_DIR / game)

    rom.source.parent.mkdir(parents=True, exist_ok=True)
    rom.source.write_text('old image')

    _write_build(rom, game, game_release, iso_data=True)

    return rom


class TestSquashfsFromAnOlderVersion:
    async def test_rebuilds_repacks_and_tidies_up(
        self,
        mock_run: AsyncMock,
        game: str,
        packed_launch_rom: Rom,
        launch_config: MockSystemConfig,
    ) -> None:
        emulator = _Harness(launch_config, packed_launch_rom)

        await emulator._resolve_game()
        assert mock_run.await_args_list == [
            (
                (
                    _INSTALL_DIR / 'extractor',
                    CACHE / 'opengoal' / game / 'iso_data' / game,
                    '--proj-path',
                    CACHE / 'opengoal' / game,
                    '-g',
                    game,
                    '-d',
                    '-c',
                    '-f',
                ),
                {'capture_output': False},
            ),
            (
                (
                    'mksquashfs',
                    packed_launch_rom / 'iso_data',
                    ROMS / 'opengoal' / game / 'out',
                    ROMS / 'opengoal' / game / _BUILD_MARKER,
                    packed_launch_rom.source.with_name(f'.{packed_launch_rom.source.name}.new'),
                    '-comp',
                    'zstd',
                    '-noappend',
                    '-no-progress',
                    '-quiet',
                ),
                {},
            ),
        ]

        assert packed_launch_rom.source.read_text().splitlines() == [
            str(packed_launch_rom / 'iso_data'),
            str(emulator.data_dir / 'out'),
            str(emulator.data_dir / 'opengoal-build.json'),
        ]
        assert not list(packed_launch_rom.source.parent.glob('.*.new'))

        assert (emulator.project_dir / 'out').resolve() == emulator.data_dir / 'out'
        assert emulator._repacked is not None
        emulator._drop_local_build(emulator._repacked)
        assert not emulator.data_dir.exists()

    async def test_a_failed_repack_still_plays_and_retries_without_rebuilding(
        self,
        mock_run: AsyncMock,
        game: str,
        packed_launch_rom: Rom,
        launch_config: MockSystemConfig,
    ) -> None:
        emulator = _Harness(launch_config, packed_launch_rom)

        mock_run.__force_fail__ = True
        assert await emulator._resolve_game() == game
        assert packed_launch_rom.source.read_text() == 'old image'
        assert not list(packed_launch_rom.source.parent.glob('.*.new'))
        mock_run.__force_fail__ = False

        assert await emulator._resolve_game() == game
        assert mock_run.await_args_list[-1] == (
            (
                'mksquashfs',
                packed_launch_rom / 'iso_data',
                ROMS / 'opengoal' / game / 'out',
                ROMS / 'opengoal' / game / _BUILD_MARKER,
                packed_launch_rom.source.with_name(f'.{packed_launch_rom.source.name}.new'),
                '-comp',
                'zstd',
                '-noappend',
                '-no-progress',
                '-quiet',
            ),
            {},
        )

    async def test_without_iso_data_it_cannot_rebuild(
        self,
        mock_run: AsyncMock,
        game: str,
        packed_launch_rom: Rom,
        launch_config: MockSystemConfig,
    ) -> None:
        emulator = _Harness(launch_config, packed_launch_rom)

        for child in (packed_launch_rom / 'iso_data' / game).iterdir():
            child.rmdir()

        with pytest.raises(BatoceraException, match='no iso_data'):
            await emulator._resolve_game()


@pytest.mark.parametrize('game_release', [_NEW], indirect=True)
class TestSquashfsFromThisVersion:
    async def test_plays_straight_from_the_image(
        self,
        mock_run: AsyncMock,
        game: str,
        packed_launch_rom: Rom,
        launch_config: MockSystemConfig,
    ) -> None:
        emulator = _Harness(launch_config, packed_launch_rom)

        assert await emulator._resolve_game() == game
        mock_run.assert_not_awaited()
        assert (emulator.project_dir / 'out').samefile(packed_launch_rom / 'out')

    async def test_clears_a_leftover_from_an_interrupted_repack(
        self,
        mock_run: AsyncMock,
        game: str,
        packed_launch_rom: Rom,
        launch_config: MockSystemConfig,
    ) -> None:
        emulator = _Harness(launch_config, packed_launch_rom)
        _write_build(emulator.data_dir, game, _NEW, iso_data=False)

        await emulator._resolve_game()

        assert not emulator.data_dir.exists()
        assert (emulator.project_dir / 'out').samefile(packed_launch_rom / 'out')

    async def test_keeps_a_folder_that_carries_its_own_disc(
        self,
        mock_run: AsyncMock,
        game: str,
        packed_launch_rom: Rom,
        launch_config: MockSystemConfig,
    ) -> None:
        emulator = _Harness(launch_config, packed_launch_rom)
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
        serial: str,
        disc_game: str,
        mock_run: AsyncMock,
        launch_config: MockSystemConfig,
    ) -> None:
        iso = write_ps2_disc(ROMS / 'opengoal' / f'{serial}.iso', serial)

        assert await _Harness(launch_config, Rom(iso, None))._resolve_game() == disc_game
        assert mock_run.await_args_list == [
            (
                (
                    _INSTALL_DIR / 'extractor',
                    iso,
                    '--proj-path',
                    CACHE / 'opengoal' / serial,
                    '-g',
                    disc_game,
                    '-d',
                    '-c',
                    '-e',
                    '-v',
                ),
                {'capture_output': False},
            )
        ]

        mock_run.reset_mock()

        assert await _Harness(launch_config, Rom(iso, None))._resolve_game() == disc_game
        mock_run.assert_not_awaited()

    async def test_rebuilds_over_another_games_leftovers(
        self,
        serial: str,
        disc_game: str,
        mock_run: AsyncMock,
        launch_config: MockSystemConfig,
    ) -> None:
        iso = write_ps2_disc(ROMS / 'opengoal' / f'{serial}.iso', serial)

        for leftover in (game for game in _GAMES if game != disc_game):
            emulator = _Harness(launch_config, Rom(iso, None))
            _write_build(emulator.data_dir, leftover, _NEW, iso_data=False)

            mock_run.reset_mock()

            assert await emulator._resolve_game() == disc_game
            assert mock_run.await_args_list == [
                (
                    (
                        _INSTALL_DIR / 'extractor',
                        iso,
                        '--proj-path',
                        CACHE / 'opengoal' / serial,
                        '-g',
                        disc_game,
                        '-d',
                        '-c',
                        '-e',
                        '-v',
                    ),
                    {'capture_output': False},
                )
            ]


@pytest.mark.parametrize('serial', sorted(_SERIAL_GAMES))
async def test_rejects_the_unsupported_disc_next_to_each_supported_one(
    serial: str,
    mock_run: AsyncMock,
    launch_config: MockSystemConfig,
) -> None:
    unsupported = _unsupported_neighbour(serial)
    iso = write_ps2_disc(ROMS / 'opengoal' / f'{unsupported}.iso', unsupported)

    with pytest.raises(BatoceraException, match=unsupported):
        await _Harness(launch_config, Rom(iso, None))._resolve_game()

    mock_run.assert_not_awaited()


async def test_rejects_a_plain_folder(game: str, launch_config: MockSystemConfig, mock_run: AsyncMock) -> None:
    folder = ROMS / 'opengoal' / game
    _write_build(folder, game, _NEW, iso_data=True)

    with pytest.raises(BatoceraException, match='neither'):
        await _Harness(launch_config, Rom(folder, None))._resolve_game()

    mock_run.assert_not_awaited()
