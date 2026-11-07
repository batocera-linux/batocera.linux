# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

from __future__ import annotations

import pytest

from batocera_launch.config.config import _system_emulators
from batocera_launch.paths import SYSTEM_ES_DIR, USER_ES_DIR

pytestmark = pytest.mark.usefixtures('fake_fs')

_SYSTEMS = """\
<systemList>
  <system>
    <name>hikaru</name>
    <emulators><emulator name="odin"><cores><core default="true">odin</core></cores></emulator></emulators>
  </system>
  <system>
    <name>gaelco</name>
    <emulators>
      <emulator name="odin"><cores><core>odin</core></cores></emulator>
      <emulator name="libretro"><cores><core>mame</core></cores></emulator>
    </emulators>
  </system>
</systemList>
"""


def test_lists_the_emulators_of_a_system() -> None:
    SYSTEM_ES_DIR.mkdir(parents=True)
    (SYSTEM_ES_DIR / 'es_systems.cfg').write_text(_SYSTEMS)

    assert _system_emulators('hikaru') == {'odin'}
    assert _system_emulators('gaelco') == {'odin', 'libretro'}


def test_unknown_without_a_file_naming_the_system() -> None:
    assert _system_emulators('hikaru') is None

    SYSTEM_ES_DIR.mkdir(parents=True)
    (SYSTEM_ES_DIR / 'es_systems.cfg').write_text(_SYSTEMS)

    assert _system_emulators('naomi') is None


def test_a_user_file_overrides_the_system_one() -> None:
    SYSTEM_ES_DIR.mkdir(parents=True)
    (SYSTEM_ES_DIR / 'es_systems.cfg').write_text(_SYSTEMS)
    USER_ES_DIR.mkdir(parents=True)
    (USER_ES_DIR / 'es_systems_hikaru.cfg').write_text(
        '<systemList><system><name>hikaru</name><emulators><emulator name="demul"/></emulators></system></systemList>'
    )

    assert _system_emulators('hikaru') == {'demul'}
    assert _system_emulators('gaelco') == {'odin', 'libretro'}


def test_a_broken_file_is_skipped() -> None:
    SYSTEM_ES_DIR.mkdir(parents=True)
    (SYSTEM_ES_DIR / 'es_systems.cfg').write_text(_SYSTEMS)
    USER_ES_DIR.mkdir(parents=True)
    (USER_ES_DIR / 'es_systems_broken.cfg').write_text('<systemList><system>')

    assert _system_emulators('hikaru') == {'odin'}
