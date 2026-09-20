from __future__ import annotations

from pathlib import Path

import pytest

from batocera_launch.emulators.opengoal import (
    _built_games,
    _disc_serial,
    _extracted_games,
    _game_data_target,
    _iso_serial,
    _link_or_replace,
    _pckernel_version,
    _recorded_version,
    _rom_project_dir,
)

pytestmark = pytest.mark.usefixtures('fs')

_ROM = Path('/userdata/roms/opengoal/game')
_PROJECT = Path('/userdata/saves/opengoal/projects/game')


def _write(path: Path, content: str = '') -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


class TestRomProjectDir:
    def test_finds_a_release_layout(self) -> None:
        (_ROM / 'data' / 'out' / 'jak1').mkdir(parents=True)

        assert _rom_project_dir(_ROM) == _ROM / 'data'

    def test_finds_a_bare_project_layout(self) -> None:
        (_ROM / 'iso_data' / 'jak1').mkdir(parents=True)

        assert _rom_project_dir(_ROM) == _ROM

    def test_ignores_a_directory_with_no_game_data(self) -> None:
        (_ROM / 'goal_src').mkdir(parents=True)

        assert _rom_project_dir(_ROM) is None

    def test_ignores_a_file(self) -> None:
        assert _rom_project_dir(_write(_ROM.with_suffix('.iso'))) is None


class TestGameDetection:
    def test_a_game_counts_as_built_only_with_its_boot_dgo(self) -> None:
        (_PROJECT / 'out' / 'jak1' / 'iso').mkdir(parents=True)

        assert _built_games(_PROJECT) == []

        _write(_PROJECT / 'out' / 'jak1' / 'iso' / 'KERNEL.CGO')

        assert _built_games(_PROJECT) == ['jak1']

    def test_a_disc_folder_is_recognised_by_its_dgo_directory(self) -> None:
        (_PROJECT / 'iso_data' / 'jak2' / 'DGO').mkdir(parents=True)

        assert _extracted_games(_PROJECT) == ['jak2']

    def test_nothing_is_detected_in_an_empty_project(self) -> None:
        _PROJECT.mkdir(parents=True)

        assert _built_games(_PROJECT) == []
        assert _extracted_games(_PROJECT) == []


class TestDiscSerial:
    def test_reads_the_serial_the_extractor_recorded(self) -> None:
        _write(_ROM / 'buildinfo.json', '[\n  {\n    "elf_hash": 1,\n    "serial": "SCES-50361"\n  }\n]')

        assert _disc_serial(_ROM) == 'SCES-50361'

    def test_falls_back_to_the_boot_elf_name(self) -> None:
        _write(_ROM / 'SYSTEM.CNF', 'BOOT2 = cdrom0:\\SCES_503.61;1\nVER = 1.00\n')

        assert _disc_serial(_ROM) == 'SCES-50361'

    def test_survives_a_corrupt_buildinfo(self) -> None:
        _write(_ROM / 'buildinfo.json', 'not json')
        _write(_ROM / 'SYSTEM.CNF', 'BOOT2 = cdrom0:\\SCUS_971.24;1\n')

        assert _disc_serial(_ROM) == 'SCUS-97124'

    def test_returns_nothing_when_the_disc_is_unidentifiable(self) -> None:
        _ROM.mkdir(parents=True)

        assert _disc_serial(_ROM) is None


class TestPckernelVersion:
    def test_packs_the_four_parts_the_way_the_game_does(self) -> None:
        _write(
            Path('/goal_src/jak1/pc/pckernel-impl.gc'),
            ';; comment\n(defconstant PC_KERNEL_VERSION (static-pckernel-version 1 10 4 0))\n',
        )

        assert _pckernel_version(Path('/goal_src'), 'jak1') == 0x1000A00040000

    def test_returns_nothing_when_the_source_is_missing(self) -> None:
        assert _pckernel_version(Path('/goal_src'), 'jak1') is None


class TestLinkOrReplace:
    def test_creates_the_link(self) -> None:
        target = Path('/usr/bin/opengoal/data/goal_src')
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

    def test_leaves_a_real_directory_alone(self) -> None:
        target = Path('/usr/bin/opengoal/data/out')
        target.mkdir(parents=True)
        built = _write(_PROJECT / 'out' / 'jak1' / 'iso' / 'KERNEL.CGO')

        _link_or_replace(_PROJECT / 'out', target)

        assert not (_PROJECT / 'out').is_symlink()
        assert built.is_file()


class TestRecordedVersion:
    def test_reads_the_stamp_left_by_an_earlier_build(self) -> None:
        marker = _write(
            _ROM / 'opengoal-build.json', '{\n  "game": "jak1",\n  "pc_kernel_version": "0x1000a00040000"\n}'
        )

        assert _recorded_version(marker) == 0x1000A00040000

    def test_returns_nothing_when_there_is_no_stamp(self) -> None:
        assert _recorded_version(_ROM / 'opengoal-build.json') is None

    def test_returns_nothing_for_a_corrupt_stamp(self) -> None:
        assert _recorded_version(_write(_ROM / 'opengoal-build.json', 'not json')) is None

    def test_returns_nothing_for_an_unparseable_version(self) -> None:
        marker = _write(_ROM / 'opengoal-build.json', '{"pc_kernel_version": "nonsense"}')

        assert _recorded_version(marker) is None


class TestGameDataTarget:
    def test_uses_what_the_rom_ships_when_nothing_was_built_here(self) -> None:
        supplied = _ROM / 'out'
        (supplied / 'jak1').mkdir(parents=True)

        assert _game_data_target(_PROJECT / 'out', supplied) == supplied

    def test_prefers_a_rebuild_over_the_stale_data_the_rom_ships(self) -> None:
        supplied = _ROM / 'out'
        (supplied / 'jak1').mkdir(parents=True)
        local = _PROJECT / 'out'
        _write(local / 'jak1' / 'iso' / 'KERNEL.CGO')

        assert _game_data_target(local, supplied) == local

    def test_ignores_an_empty_local_directory(self) -> None:
        supplied = _ROM / 'out'
        (supplied / 'jak1').mkdir(parents=True)
        local = _PROJECT / 'out'
        local.mkdir(parents=True)

        assert _game_data_target(local, supplied) == supplied

    def test_falls_back_to_local_when_the_rom_ships_nothing(self) -> None:
        assert _game_data_target(_PROJECT / 'out', None) == _PROJECT / 'out'


class TestIsoSerial:
    def test_reads_the_serial_from_the_boot_line(self) -> None:
        iso = _ROM.with_suffix('.iso')
        iso.parent.mkdir(parents=True, exist_ok=True)
        iso.write_bytes(b'\x00' * 4096 + b'BOOT2 = cdrom0:\\SCES_516.08;1\r\nVER = 1.00\r\n')

        assert _iso_serial(iso) == 'SCES-51608'

    def test_finds_a_serial_split_across_the_read_boundary(self) -> None:
        iso = _ROM.with_suffix('.iso')
        iso.parent.mkdir(parents=True, exist_ok=True)
        boot = b'cdrom0:\\SCES_524.60;1'
        # straddle the 1MiB chunk edge
        iso.write_bytes(b'\x00' * ((1 << 20) - 10) + boot)

        assert _iso_serial(iso) == 'SCES-52460'

    def test_returns_nothing_without_a_boot_line(self) -> None:
        iso = _ROM.with_suffix('.iso')
        iso.parent.mkdir(parents=True, exist_ok=True)
        iso.write_bytes(b'\x00' * 8192)

        assert _iso_serial(iso) is None

    def test_returns_nothing_for_a_missing_file(self) -> None:
        assert _iso_serial(_ROM.with_suffix('.iso')) is None
