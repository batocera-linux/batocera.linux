from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from batocera_launch.config.defaults import load_defaults, load_system_defaults
from batocera_launch.paths import DEFAULTS_DIR

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem

pytestmark = pytest.mark.usefixtures('fs')

_REAL_DEFAULTS_DIR = Path(__file__).resolve().parents[1] / 'resources' / 'defaults'


def _write_yaml(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


class TestLoadDefaults:
    def test_returns_base_default(self) -> None:
        base = _write_yaml(
            Path('/tmp/config.yml'),
            """\
default:
  emulator: libretro
  core: fceumm
  options:
    smooth: true
""",
        )
        arch = Path('/tmp/config-arch.yml')

        assert load_defaults('unknown', base, arch) == {
            'emulator': 'libretro',
            'core': 'fceumm',
            'options': {'smooth': True},
        }

    def test_merges_arch_default_over_base_default(self) -> None:
        base = _write_yaml(
            Path('/tmp/config.yml'),
            """\
default:
  emulator: libretro
  core: fceumm
  options:
    smooth: true
    videomode: default
""",
        )
        arch = _write_yaml(
            Path('/tmp/config-arch.yml'),
            """\
default:
  options:
    smooth: false
    hud_support: true
""",
        )

        assert load_defaults('unknown', base, arch) == {
            'emulator': 'libretro',
            'core': 'fceumm',
            'options': {
                'smooth': False,
                'videomode': 'default',
                'hud_support': True,
            },
        }

    def test_merges_system_over_defaults(self) -> None:
        base = _write_yaml(
            Path('/tmp/config.yml'),
            """\
default:
  emulator: libretro
  core: fceumm
  options:
    smooth: true
nes:
  core: nestopia
  options:
    rewind: true
""",
        )
        arch = Path('/tmp/config-arch.yml')

        assert load_defaults('nes', base, arch) == {
            'emulator': 'libretro',
            'core': 'nestopia',
            'options': {
                'smooth': True,
                'rewind': True,
            },
        }

    def test_arch_system_overrides_system(self) -> None:
        base = _write_yaml(
            Path('/tmp/config.yml'),
            """\
default:
  emulator: libretro
  core: fceumm
nes:
  core: nestopia
  options:
    videomode: default
""",
        )
        arch = _write_yaml(
            Path('/tmp/config-arch.yml'),
            """\
nes:
  emulator: mednafen
  options:
    videomode: max-1920x1080
""",
        )

        assert load_defaults('nes', base, arch) == {
            'emulator': 'mednafen',
            'core': 'nestopia',
            'options': {'videomode': 'max-1920x1080'},
        }

    def test_missing_arch_file_is_ignored(self) -> None:
        base = _write_yaml(
            Path('/tmp/config.yml'),
            """\
default:
  emulator: libretro
  core: fceumm
""",
        )

        assert load_defaults('nes', base, Path('/tmp/missing-arch.yml')) == {
            'emulator': 'libretro',
            'core': 'fceumm',
        }

    def test_empty_arch_file_is_ignored(self) -> None:
        base = _write_yaml(
            Path('/tmp/config.yml'),
            """\
default:
  emulator: libretro
  core: fceumm
""",
        )
        arch = _write_yaml(Path('/tmp/config-arch.yml'), '')

        assert load_defaults('nes', base, arch) == {
            'emulator': 'libretro',
            'core': 'fceumm',
        }

    def test_no_default_section_starts_empty(self) -> None:
        base = _write_yaml(
            Path('/tmp/config.yml'),
            """\
nes:
  emulator: libretro
  core: fceumm
""",
        )
        arch = Path('/tmp/config-arch.yml')

        assert load_defaults('nes', base, arch) == {
            'emulator': 'libretro',
            'core': 'fceumm',
        }


class TestLoadSystemDefaults:
    def test_flattens_options_into_top_level(self) -> None:
        _write_yaml(
            DEFAULTS_DIR / 'config.yml',
            """\
default:
  emulator: libretro
  core: fceumm
  options:
    smooth: true
    videomode: default
nes:
  core: nestopia
  options:
    rewind: true
""",
        )

        assert load_system_defaults('nes') == {
            'emulator': 'libretro',
            'core': 'nestopia',
            'smooth': True,
            'videomode': 'default',
            'rewind': True,
        }

    def test_merges_arch_overrides_when_present(self) -> None:
        _write_yaml(
            DEFAULTS_DIR / 'config.yml',
            """\
default:
  emulator: libretro
  core: fceumm
  options:
    smooth: true
n64:
  emulator: mupen64plus
  core: glide64mk2
""",
        )
        _write_yaml(
            DEFAULTS_DIR / 'config-arch.yml',
            """\
default:
  options:
    hud_support: true
n64:
  options:
    videomode: max-1920x1080
""",
        )

        assert load_system_defaults('n64') == {
            'emulator': 'mupen64plus',
            'core': 'glide64mk2',
            'smooth': True,
            'hud_support': True,
            'videomode': 'max-1920x1080',
        }

    def test_real_defaults_resources(self, fs: FakeFilesystem) -> None:
        fs.add_real_directory(_REAL_DEFAULTS_DIR, target_path=DEFAULTS_DIR)  # pyright: ignore
        fs.add_real_file(  # pyright: ignore
            _REAL_DEFAULTS_DIR / 'config-x86_64.yml',
            target_path=DEFAULTS_DIR / 'config-arch.yml',
        )

        nes = load_system_defaults('nes')
        assert nes['emulator'] == 'libretro'
        assert nes['core'] == 'fceumm'
        assert nes['hud_support'] is True
        assert nes['smooth'] is True

        n64 = load_system_defaults('n64')
        assert n64['emulator'] == 'mupen64plus'
        assert n64['core'] == 'glide64mk2'
        assert n64['videomode'] == 'max-1920x1080'
        assert n64['video_frame_delay_auto'] is True
