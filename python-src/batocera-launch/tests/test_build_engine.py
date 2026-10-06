from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from batocera_launch.config.build_engine import parse_build_engine_args
from batocera_launch.exceptions import InvalidConfiguration

if TYPE_CHECKING:
    from collections.abc import Iterable

pytestmark = pytest.mark.usefixtures('fs')

_ROM_DIR = Path('/userdata/roms/duke')


def _write_rom(content: str, *, name: str = 'game.eduke32') -> Path:
    _ROM_DIR.mkdir(parents=True, exist_ok=True)
    rom_path = _ROM_DIR / name
    rom_path.write_text(content)
    return rom_path


class TestParseBuildEngineArgs:
    def test_empty_script_returns_empty_list(self) -> None:
        rom = _write_rom('')

        assert parse_build_engine_args(rom) == []

    def test_skips_blank_lines_and_comments(self) -> None:
        rom = _write_rom(
            '\n'.join(
                [
                    '',
                    '# comment',
                    '// also a comment',
                    '  # indented comment',
                    'FILE=duke3d.grp',
                    '  ',
                ]
            ),
        )

        assert parse_build_engine_args(rom) == ['-gamegrp', 'duke3d.grp']

    def test_parses_all_known_keys(self) -> None:
        rom = _write_rom(
            '\n'.join(
                [
                    'DIR=addons',
                    'FILE=duke3d.grp',
                    'FILE+=mod.zip',
                    'CON=GAME.CON',
                    'CON+=extra.con',
                    'DEF=duke.def',
                    'DEF+=extra.def',
                    'MAP=e1l1.map',
                ]
            ),
        )

        assert parse_build_engine_args(rom) == [
            '-j',
            'addons',
            '-gamegrp',
            'duke3d.grp',
            '-g',
            'mod.zip',
            '-x',
            'GAME.CON',
            '-mx',
            'extra.con',
            '-h',
            'duke.def',
            '-mh',
            'extra.def',
            '-map',
            'e1l1.map',
        ]

    def test_keys_are_case_insensitive_and_whitespace_trimmed(self) -> None:
        rom = _write_rom('  file  =  duke3d.grp  \n')

        assert parse_build_engine_args(rom) == ['-gamegrp', 'duke3d.grp']

    def test_leading_slash_resolves_path_relative_to_rom_parent(self) -> None:
        _ROM_DIR.mkdir(parents=True, exist_ok=True)
        (_ROM_DIR / 'duke3d.grp').write_text('grp')
        (_ROM_DIR / 'addons').mkdir()
        rom = _write_rom('FILE=/duke3d.grp\nDIR=/addons\n')

        assert parse_build_engine_args(rom) == [
            '-gamegrp',
            _ROM_DIR / 'duke3d.grp',
            '-j',
            _ROM_DIR / 'addons',
        ]

    def test_missing_physical_path_raises(self) -> None:
        rom = _write_rom('FILE=/missing.grp\n')

        with pytest.raises(InvalidConfiguration, match='does not exist') as exc_info:
            parse_build_engine_args(rom)

        assert '1 error(s) found' in str(exc_info.value)
        assert 'line 1|' in str(exc_info.value)

    def test_allows_multiple_non_only_one_keys(self) -> None:
        rom = _write_rom('FILE+=a.zip\nFILE+=b.zip\nDIR=one\nDIR=two\n')

        assert parse_build_engine_args(rom) == ['-g', 'a.zip', '-g', 'b.zip', '-j', 'one', '-j', 'two']

    def test_rejects_duplicate_only_one_key_in_script(self) -> None:
        rom = _write_rom('FILE=a.grp\nFILE=b.grp\n')

        with pytest.raises(InvalidConfiguration, match="found another 'FILE'") as exc_info:
            parse_build_engine_args(rom)

        assert '1 error(s) found' in str(exc_info.value)
        assert 'line 2|' in str(exc_info.value)

    def test_rejects_only_one_key_already_in_existing(self) -> None:
        rom = _write_rom('FILE=duke3d.grp\n')
        existing: Iterable[str | Path] = ['eduke32', '-cfg', 'settings.cfg', '-gamegrp']

        with pytest.raises(InvalidConfiguration, match="found another 'FILE'"):
            parse_build_engine_args(rom, existing=existing)

    def test_existing_paths_are_ignored_for_seen_options(self) -> None:
        rom = _write_rom('FILE=duke3d.grp\n')
        existing: Iterable[str | Path] = [Path('/-gamegrp')]

        assert parse_build_engine_args(rom, existing=existing) == ['-gamegrp', 'duke3d.grp']

    @pytest.mark.parametrize(
        ('content', 'error'),
        [
            ('FILE duke3d.grp', "KEY and/or VAL is empty; are you missing a '='?"),
            ('FILE=', "KEY and/or VAL is empty; are you missing a '='?"),
            ('=duke3d.grp', "KEY and/or VAL is empty; are you missing a '='?"),
            ('FILE=a=b', "found another '=', but there should only be one"),
            ('UNKNOWN=value', "KEY 'UNKNOWN' is not valid"),
        ],
    )
    def test_parse_errors(self, content: str, error: str) -> None:
        rom = _write_rom(f'{content}\n')

        with pytest.raises(InvalidConfiguration, match=error):
            parse_build_engine_args(rom)

    def test_collects_multiple_errors(self) -> None:
        rom = _write_rom(
            '\n'.join(
                [
                    'BAD',
                    'UNKNOWN=x',
                    'FILE=/missing.grp',
                ]
            ),
        )

        with pytest.raises(InvalidConfiguration) as exc_info:
            parse_build_engine_args(rom)

        message = str(exc_info.value)
        assert '3 error(s) found' in message
        assert 'line 1|' in message
        assert 'line 2|' in message
        assert 'line 3|' in message
        assert "missing a '='" in message
        assert "KEY 'UNKNOWN' is not valid" in message
        assert 'does not exist' in message
