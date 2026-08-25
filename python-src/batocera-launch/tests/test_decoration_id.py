from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from batocera_launch.config.decoration_id import get_decoration_id
from batocera_launch.paths import LAUNCH_DATA_DIR

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem

pytestmark = pytest.mark.usefixtures('fs')

_REAL_SPECIAL_DIR = Path(__file__).resolve().parents[1] / 'resources' / 'data' / 'special'


@pytest.fixture(autouse=True)
def special_data(fs: FakeFilesystem) -> None:
    fs.add_real_directory(_REAL_SPECIAL_DIR, target_path=LAUNCH_DATA_DIR / 'special')  # pyright: ignore


class TestGetDecorationId:
    def test_unknown_system_returns_zero(self) -> None:
        assert get_decoration_id('nosuchsystem', 'any-rom') == '0'

    def test_known_system_unknown_rom_returns_zero(self) -> None:
        assert get_decoration_id('dice', 'not-a-game') == '0'

    def test_matches_rom_from_special_toml(self) -> None:
        assert get_decoration_id('dice', 'breakout') == '270'
        assert get_decoration_id('dice', 'pinpong') == '270'

    def test_match_is_case_insensitive(self) -> None:
        assert get_decoration_id('dice', 'BREAKOUT') == '270'
        assert (
            get_decoration_id(
                'lynx',
                'gauntlet - the third encounter (usa, europe)',
            )
            == '270'
        )

    def test_quoted_keys_with_spaces(self) -> None:
        assert get_decoration_id('lynx', 'Klax (USA, Europe)') == '270'
        assert get_decoration_id('lynx', 'Lexis (USA)') == '90'

    def test_underscore_rom_ids(self) -> None:
        assert get_decoration_id('3ds', 'New_Love_Plus_JPN_3DS-Kirin') == '90'
        assert get_decoration_id('3ds', 'new_love_plus_plus_jpn_3ds-kirin') == '90'
