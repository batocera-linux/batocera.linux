from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from batocera_common.yaml import safe_load_yaml12
from batocera_labwc.build_rule_sets import main
from batocera_labwc.types import LabWCRule

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.usefixtures('fs')


def _write_info_paths(path: Path, *info_files: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(' '.join(str(info_file) for info_file in info_files) + '\n')


def _write_emulator_yml(path: Path, contents: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents)
    return path


@pytest.fixture
def info_paths() -> Path:
    return Path('/build/info_files.txt')


@pytest.fixture
def destination_dir(fs: FakeFilesystem) -> Path:
    destination_dir = Path('/out/labwc')
    destination_dir.mkdir(parents=True, exist_ok=True)
    return destination_dir


@pytest.fixture
def sys_argv(mocker: MockerFixture, info_paths: Path, destination_dir: Path) -> None:
    mocker.patch('sys.argv', ['build_rule_sets', str(info_paths), str(destination_dir)])


@pytest.mark.usefixtures('sys_argv')
class TestBuildRuleSets:
    def test_writes_labwc_rules_from_emulator_yml(
        self,
        info_paths: Path,
        destination_dir: Path,
    ) -> None:
        azahar = _write_emulator_yml(
            Path('/pkg/azahar/azahar.emulator.yml'),
            """\
labwc:
  window_rules:
    - identifier: azahar
      actions:
        - name: MoveToOutput
          output: primary
    - identifier: azahar
      title: "*Secondary Window*"
      actions:
        - name: MoveToOutput
          output: secondary|primary
        - name: ToggleFullscreen
""",
        )
        _write_info_paths(info_paths, azahar)

        main()

        rules = safe_load_yaml12(destination_dir / 'azahar.labwc-rules.yml', list[LabWCRule])

        assert rules == [
            {
                'identifier': 'azahar',
                'actions': [{'name': 'MoveToOutput', 'output': 'primary'}],
            },
            {
                'identifier': 'azahar',
                'title': '*Secondary Window*',
                'actions': [
                    {'name': 'MoveToOutput', 'output': 'secondary|primary'},
                    {'name': 'ToggleFullscreen'},
                ],
            },
        ]

    def test_writes_global_rules(
        self,
        info_paths: Path,
        destination_dir: Path,
    ) -> None:
        global_info = _write_emulator_yml(
            Path('/pkg/es/_global.emulator.yml'),
            """\
labwc:
  window_rules:
    - identifier: emulationstation
      actions:
        - name: FocusOutput
          output: primary
        - name: MoveToOutput
          output: primary
""",
        )
        _write_info_paths(info_paths, global_info)

        main()

        rules = safe_load_yaml12(destination_dir / '_global.labwc-rules.yml', list[LabWCRule])

        assert rules is not None
        assert len(rules) == 1
        assert rules[0].get('identifier') == 'emulationstation'

        first_action = rules[0]['actions'][0]
        assert first_action['name'] == 'FocusOutput'

    def test_supports_yaml_extension(
        self,
        info_paths: Path,
        destination_dir: Path,
    ) -> None:
        melonds = _write_emulator_yml(
            Path('/pkg/melonds/melonds.emulator.yaml'),
            """\
labwc:
  window_rules:
    - identifier: net.kuribo64.melonDS
      title: "*w1*"
      actions:
        - name: MoveToOutput
          output: primary
""",
        )
        _write_info_paths(info_paths, melonds)

        main()

        assert (destination_dir / 'melonds.labwc-rules.yml').is_file()

    def test_skips_emulator_yml_without_labwc_rules(
        self,
        info_paths: Path,
        destination_dir: Path,
    ) -> None:
        plain = _write_emulator_yml(
            Path('/pkg/plain/plain.emulator.yml'),
            """\
systems:
  - nes
""",
        )
        labwc_without_rules = _write_emulator_yml(
            Path('/pkg/empty/empty.emulator.yml'),
            """\
labwc: {}
""",
        )
        _write_info_paths(info_paths, plain, labwc_without_rules)

        main()

        assert list(destination_dir.iterdir()) == []

    def test_skips_non_emulator_info_filenames(
        self,
        info_paths: Path,
        destination_dir: Path,
    ) -> None:
        nested = _write_emulator_yml(
            Path('/pkg/core/libretro.nestopia.emulator.yml'),
            """\
labwc:
  window_rules:
    - identifier: should-not-write
      actions:
        - name: MoveToOutput
          output: primary
""",
        )
        other = _write_emulator_yml(
            Path('/pkg/notes/readme.yml'),
            """\
labwc:
  window_rules:
    - identifier: should-not-write
      actions:
        - name: MoveToOutput
          output: primary
""",
        )
        _write_info_paths(info_paths, nested, other)

        main()

        assert list(destination_dir.iterdir()) == []

    def test_builds_multiple_rule_sets(
        self,
        info_paths: Path,
        destination_dir: Path,
    ) -> None:
        global_info = _write_emulator_yml(
            Path('/pkg/es/_global.emulator.yml'),
            """\
labwc:
  window_rules:
    - identifier: emulationstation
      actions:
        - name: MoveToOutput
          output: primary
""",
        )
        azahar = _write_emulator_yml(
            Path('/pkg/azahar/azahar.emulator.yml'),
            """\
labwc:
  window_rules:
    - identifier: azahar
      actions:
        - name: MoveToOutput
          output: primary
""",
        )
        ignored = _write_emulator_yml(
            Path('/pkg/mame/mame.emulator.yml'),
            """\
systems:
  - mame
""",
        )
        _write_info_paths(info_paths, global_info, azahar, ignored)

        main()

        assert sorted(path.name for path in destination_dir.iterdir()) == [
            '_global.labwc-rules.yml',
            'azahar.labwc-rules.yml',
        ]

    def test_empty_info_path_file_writes_nothing(
        self,
        info_paths: Path,
        destination_dir: Path,
    ) -> None:
        _write_info_paths(info_paths)

        main()

        assert list(destination_dir.iterdir()) == []
