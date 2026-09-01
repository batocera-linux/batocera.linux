from __future__ import annotations

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from batocera_launch.config.labwc import LABWC_BIN, LabWCConfig
from batocera_launch.types import Resolution, ScreenInfo

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.usefixtures('fs')

_MINIMAL_RC_XML = """\
<?xml version='1.0' encoding='utf-8'?>
<labwc_config>
</labwc_config>
"""

_EXISTING_RULES_RC_XML = """\
<?xml version='1.0' encoding='utf-8'?>
<labwc_config>
  <windowRules>
    <windowRule identifier="azahar">
      <action name="MoveToOutput"><output>HDMI-1</output></action>
    </windowRule>
    <windowRule identifier="azahar" title="*Secondary Window*">
      <action name="MoveToOutput"><output>HDMI-2</output></action>
      <action name="ToggleFullscreen" />
    </windowRule>
  </windowRules>
</labwc_config>
"""


@pytest.fixture
def rc_path(fs: FakeFilesystem) -> Path:
    path = Path('/userdata/system/.config/labwc/rc.xml')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_MINIMAL_RC_XML)
    return path


@pytest.fixture
def screens() -> list[ScreenInfo]:
    return [
        ScreenInfo('HDMI-A-1', Resolution(1920, 1080), 0, 0),
        ScreenInfo('HDMI-A-2', Resolution(1280, 720), 1920, 0),
    ]


def _find_rule(root: ET.Element[str], /, *, identifier: str | None = None, title: str | None = None) -> ET.Element[str]:
    attribute_query = ''

    if identifier is not None:
        attribute_query = f'[@identifier="{identifier}"]'

    if title is not None:
        attribute_query = f'{attribute_query}[@title="{title}"]'

    rule = root.find(f'./windowRules/windowRule{attribute_query}')

    if rule is None:
        raise AssertionError(f'window rule not found: identifier={identifier!r}, title={title!r}')

    return rule


def _output_name(rule: ET.Element[str]) -> str | None:
    action = rule.find('./action[@name="MoveToOutput"]/output')

    return action.text if action is not None else None


def _has_fullscreen(rule: ET.Element[str]) -> bool:
    return rule.find('./action[@name="ToggleFullscreen"]') is not None


class TestLabWCConfigLoad:
    def test_raises_when_file_not_found(self, fs: FakeFilesystem) -> None:
        fs.create_dir('/userdata/system/.config/labwc')  # pyright: ignore

        with pytest.raises(FileNotFoundError):
            LabWCConfig(path=Path('/userdata/system/.config/labwc/rc.xml'))

    def test_raises_on_invalid_xml(self, rc_path: Path) -> None:
        rc_path.write_text('not xml')

        with pytest.raises(ET.ParseError):
            LabWCConfig(path=rc_path)


class TestLabWCConfigWindowRule:
    def test_requires_identifier_or_title(self, rc_path: Path) -> None:
        config = LabWCConfig(path=rc_path)

        with pytest.raises(ValueError, match='Either identifier or title must be provided'):
            config.window_rule()

    def test_creates_window_rules_section_when_missing(self, rc_path: Path) -> None:
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar')

        window_rules = config.root.find('./windowRules')

        assert window_rules is not None
        assert _find_rule(config.root, identifier='azahar').get('identifier') == 'azahar'

    def test_returns_same_window_rule_from_cache(self, rc_path: Path) -> None:
        config = LabWCConfig(path=rc_path)

        first = config.window_rule(identifier='azahar')
        second = config.window_rule(identifier='azahar')

        assert first is second

    def test_finds_existing_window_rule_by_identifier(self, rc_path: Path) -> None:
        rc_path.write_text(_EXISTING_RULES_RC_XML)
        config = LabWCConfig(path=rc_path)

        rule = config.window_rule(identifier='azahar')

        assert _output_name(rule.element) == 'HDMI-1'

    def test_finds_existing_window_rule_by_identifier_and_title(self, rc_path: Path) -> None:
        rc_path.write_text(_EXISTING_RULES_RC_XML)
        config = LabWCConfig(path=rc_path)

        rule = config.window_rule(identifier='azahar', title='*Secondary Window*')

        assert _output_name(rule.element) == 'HDMI-2'
        assert _has_fullscreen(rule.element)


class TestWindowRuleMoveToOutput:
    def test_move_to_output_primary(self, rc_path: Path, screens: list[ScreenInfo]) -> None:
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar').move_to_output(screens, 'primary')

        rule = _find_rule(config.root, identifier='azahar')

        assert _output_name(rule) == 'HDMI-A-1'

    def test_move_to_output_backglass_uses_second_screen(self, rc_path: Path, screens: list[ScreenInfo]) -> None:
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar', title='*Secondary Window*').move_to_output(screens, 'backglass')

        rule = _find_rule(config.root, identifier='azahar', title='*Secondary Window*')

        assert _output_name(rule) == 'HDMI-A-2'

    def test_move_to_output_backglass_falls_back_to_primary_on_single_screen(self, rc_path: Path) -> None:
        single_screen = [ScreenInfo('HDMI-A-1', Resolution(1920, 1080), 0, 0)]
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar', title='*Secondary Window*').move_to_output(single_screen, 'backglass')

        rule = _find_rule(config.root, identifier='azahar', title='*Secondary Window*')

        assert _output_name(rule) == 'HDMI-A-1'

    def test_move_to_output_none_removes_action(self, rc_path: Path, screens: list[ScreenInfo]) -> None:
        rc_path.write_text(_EXISTING_RULES_RC_XML)
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar').move_to_output(screens, None)

        rule = _find_rule(config.root, identifier='azahar')

        assert _output_name(rule) is None

    def test_move_to_output_updates_existing_output(self, rc_path: Path, screens: list[ScreenInfo]) -> None:
        rc_path.write_text(_EXISTING_RULES_RC_XML)
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar').move_to_output(screens, 'primary')

        rule = _find_rule(config.root, identifier='azahar')

        assert _output_name(rule) == 'HDMI-A-1'


class TestWindowRuleToggleFullscreen:
    def test_toggle_fullscreen_adds_action(self, rc_path: Path) -> None:
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar').toggle_fullscreen()

        rule = _find_rule(config.root, identifier='azahar')

        assert _has_fullscreen(rule)

    def test_toggle_fullscreen_false_removes_action(self, rc_path: Path) -> None:
        rc_path.write_text(_EXISTING_RULES_RC_XML)
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar', title='*Secondary Window*').toggle_fullscreen(False)

        rule = _find_rule(config.root, identifier='azahar', title='*Secondary Window*')

        assert not _has_fullscreen(rule)

    def test_supports_method_chaining(self, rc_path: Path, screens: list[ScreenInfo]) -> None:
        config = LabWCConfig(path=rc_path)
        rule = (
            config.window_rule(identifier='azahar', title='*Secondary Window*')
            .move_to_output(screens, 'backglass')
            .toggle_fullscreen()
        )

        assert _output_name(rule.element) == 'HDMI-A-2'
        assert _has_fullscreen(rule.element)


class TestLabWCConfigSave:
    def test_writes_xml_and_reconfigures_labwc(
        self, rc_path: Path, screens: list[ScreenInfo], mocker: MockerFixture
    ) -> None:
        mock_run = mocker.patch('subprocess.run')
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar').move_to_output(screens, 'primary')
        config.save()

        saved = ET.parse(rc_path).getroot()
        rule = _find_rule(saved, identifier='azahar')

        assert _output_name(rule) == 'HDMI-A-1'
        assert rc_path.read_text().startswith("<?xml version='1.0' encoding='utf-8'?>")
        mock_run.assert_called_once_with([LABWC_BIN, '--reconfigure'], check=True)

    def test_azahar_window_rules(self, rc_path: Path, screens: list[ScreenInfo], mocker: MockerFixture) -> None:
        mocker.patch('subprocess.run')
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar').move_to_output(screens, 'primary')
        (
            config.window_rule(identifier='azahar', title='*Secondary Window*')
            .move_to_output(screens, 'backglass')
            .toggle_fullscreen()
        )
        config.save()

        saved = ET.parse(rc_path).getroot()
        primary = _find_rule(saved, identifier='azahar')
        secondary = _find_rule(saved, identifier='azahar', title='*Secondary Window*')

        assert _output_name(primary) == 'HDMI-A-1'
        assert _output_name(secondary) == 'HDMI-A-2'
        assert _has_fullscreen(secondary)
        assert not _has_fullscreen(primary)

    def test_labwc_reconfigure_failure_is_logged_not_raised(
        self, rc_path: Path, mocker: MockerFixture, caplog: pytest.LogCaptureFixture
    ) -> None:
        mocker.patch(
            'subprocess.run',
            side_effect=subprocess.CalledProcessError(1, 'labwc'),
        )
        config = LabWCConfig(path=rc_path)

        with caplog.at_level('ERROR'):
            config.save()

        assert 'failed to reconfigure labwc' in caplog.text
