from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from batocera_launch.emulators.opengoal import (
    _GAMES,
    _SERIAL_GAMES,
    _SHIPPED_DATA,
    _game_data_target,
    _iso_serial,
    _link_or_replace,
    _pckernel_version,
    _read_build,
)

if TYPE_CHECKING:
    from collections.abc import Callable

pytestmark = pytest.mark.usefixtures('fs')

_ROM = Path('/userdata/roms/opengoal/game')
_PROJECT = Path('/userdata/saves/opengoal/projects/game')


def _write(path: Path, content: str = '') -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


@pytest.mark.parametrize('game', _GAMES)
class TestPckernelVersion:
    def test_packs_the_four_parts_the_way_the_game_does(self, game: str) -> None:
        _write(
            _SHIPPED_DATA / 'goal_src' / game / 'pc' / 'pckernel-impl.gc',
            ';; comment\n(defconstant PC_KERNEL_VERSION (static-pckernel-version 1 10 4 0))\n',
        )

        assert _pckernel_version(_SHIPPED_DATA / 'goal_src', game) == 0x1000A00040000

    def test_returns_nothing_when_the_source_is_missing(self, game: str) -> None:
        assert _pckernel_version(_SHIPPED_DATA / 'goal_src', game) is None


class TestLinkOrReplace:
    def test_creates_the_link(self) -> None:
        target = _SHIPPED_DATA / 'goal_src'
        target.mkdir(parents=True)
        _PROJECT.mkdir(parents=True)

        _link_or_replace(_PROJECT / 'goal_src', target)

        assert str((_PROJECT / 'goal_src').readlink()) == str(target)

    def test_repoints_a_stale_link(self) -> None:
        old = Path('/old/goal_src')
        new = Path('/new/goal_src')
        old.mkdir(parents=True)
        new.mkdir(parents=True)
        _PROJECT.mkdir(parents=True)
        (_PROJECT / 'goal_src').symlink_to(old)

        _link_or_replace(_PROJECT / 'goal_src', new)

        assert str((_PROJECT / 'goal_src').readlink()) == str(new)

    @pytest.mark.parametrize('game', _GAMES)
    def test_leaves_a_real_directory_alone(self, game: str) -> None:
        target = _SHIPPED_DATA / 'out'
        target.mkdir(parents=True)
        built = _write(_PROJECT / 'out' / game / 'iso' / 'KERNEL.CGO')

        _link_or_replace(_PROJECT / 'out', target)

        assert not (_PROJECT / 'out').is_symlink()
        assert built.is_file()


@pytest.mark.parametrize('game', _GAMES)
class TestReadBuild:
    def _built(self, game: str, release: str = 'v1.2.3') -> Path:
        _write(_PROJECT / 'opengoal-build.json', f'{{"game": "{game}", "release": "{release}"}}')
        _write(_PROJECT / 'out' / game / 'iso' / 'KERNEL.CGO')
        return _PROJECT

    def test_reads_the_game_and_version_of_a_finished_build(self, game: str) -> None:
        assert _read_build(self._built(game)) == (game, 'v1.2.3')

    def test_the_built_game_has_to_be_the_one_the_marker_names(self, game: str) -> None:
        other = _GAMES[(_GAMES.index(game) + 1) % len(_GAMES)]
        self._built(game)
        _write(_PROJECT / 'opengoal-build.json', f'{{"game": "{other}", "release": "v1.2.3"}}')

        assert _read_build(_PROJECT) is None

    def test_an_unfinished_build_has_no_marker(self, game: str) -> None:
        _write(_PROJECT / 'out' / game / 'iso' / 'KERNEL.CGO')

        assert _read_build(_PROJECT) is None

    def test_a_marker_without_its_built_game_is_not_a_build(self, game: str) -> None:
        self._built(game)
        (_PROJECT / 'out' / game / 'iso' / 'KERNEL.CGO').unlink()

        assert _read_build(_PROJECT) is None

    def test_rejects_a_game_opengoal_does_not_ship(self, game: str) -> None:
        assert _read_build(self._built(f'{game}-unknown')) is None

    def test_rejects_a_corrupt_marker(self, game: str) -> None:
        _write(_PROJECT / 'opengoal-build.json', 'not json')
        _write(_PROJECT / 'out' / game / 'iso' / 'KERNEL.CGO')

        assert _read_build(_PROJECT) is None

    def test_rejects_a_marker_without_a_release(self, game: str) -> None:
        assert _read_build(self._built(game, release='')) is None

    def test_rejects_a_marker_from_before_releases_were_recorded(self, game: str) -> None:
        _write(_PROJECT / 'opengoal-build.json', f'{{"game": "{game}", "pc_kernel_version": "0x1000a00040000"}}')
        _write(_PROJECT / 'out' / game / 'iso' / 'KERNEL.CGO')

        assert _read_build(_PROJECT) is None


class TestGameDataTarget:
    @pytest.mark.parametrize('game', _GAMES)
    def test_uses_what_the_rom_ships_when_nothing_was_built_here(self, game: str) -> None:
        supplied = _ROM / 'out'
        (supplied / game).mkdir(parents=True)

        assert _game_data_target(_PROJECT / 'out', supplied) == supplied

    @pytest.mark.parametrize('game', _GAMES)
    def test_prefers_a_rebuild_over_the_stale_data_the_rom_ships(self, game: str) -> None:
        supplied = _ROM / 'out'
        (supplied / game).mkdir(parents=True)
        local = _PROJECT / 'out'
        _write(local / game / 'iso' / 'KERNEL.CGO')

        assert _game_data_target(local, supplied) == local

    @pytest.mark.parametrize('game', _GAMES)
    def test_ignores_an_empty_local_directory(self, game: str) -> None:
        supplied = _ROM / 'out'
        (supplied / game).mkdir(parents=True)
        local = _PROJECT / 'out'
        local.mkdir(parents=True)

        assert _game_data_target(local, supplied) == supplied

    def test_falls_back_to_local_when_the_rom_ships_nothing(self) -> None:
        assert _game_data_target(_PROJECT / 'out', None) == _PROJECT / 'out'


@pytest.mark.parametrize('serial', sorted(_SERIAL_GAMES))
class TestIsoSerial:
    def test_reads_the_serial_from_the_boot_elf_name(self, serial: str, write_ps2_disc: Callable[..., Path]) -> None:
        assert _iso_serial(write_ps2_disc(_ROM.with_suffix('.iso'), serial)) == serial

    def test_finds_the_elf_past_the_first_directory_sector(
        self, serial: str, write_ps2_disc: Callable[..., Path]
    ) -> None:
        iso = write_ps2_disc(_ROM.with_suffix('.iso'), serial, pad_first_sector=True)

        assert _iso_serial(iso) == serial

    def test_ignores_a_name_that_only_contains_the_serial(
        self, serial: str, write_ps2_disc: Callable[..., Path]
    ) -> None:
        iso = write_ps2_disc(_ROM.with_suffix('.iso'), serial, elf_suffix='.BAK')

        assert _iso_serial(iso) is None

    def test_returns_nothing_for_a_truncated_root_directory(
        self, serial: str, write_ps2_disc: Callable[..., Path]
    ) -> None:
        iso = write_ps2_disc(_ROM.with_suffix('.iso'), serial)
        iso.write_bytes(iso.read_bytes()[: 20 * 2048 + 34 * 2 + 20])

        assert _iso_serial(iso) is None

    def test_returns_nothing_for_a_file_that_is_not_an_iso(self, serial: str) -> None:
        iso = _ROM.with_suffix('.iso')
        iso.parent.mkdir(parents=True, exist_ok=True)
        iso.write_bytes(f'BOOT2 = cdrom0:\\{serial};1\n'.encode() + b'\x00' * 65536)

        assert _iso_serial(iso) is None

    def test_returns_nothing_for_a_missing_file(self, serial: str) -> None:
        assert _iso_serial(_ROM.with_suffix(f'.{serial}.iso')) is None
