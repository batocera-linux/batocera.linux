from __future__ import annotations

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from batocera_labwc.config import LABWC_BIN, LabWCConfig

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
      <action name="FocusOutput"><output>HDMI-1</output></action>
    </windowRule>
    <windowRule identifier="azahar" title="*Secondary Window*">
      <action name="MoveToOutput"><output>HDMI-2</output></action>
      <action name="ToggleFullscreen" />
    </windowRule>
  </windowRules>
</labwc_config>
"""

_EXISTING_TOUCH_RC_XML = """\
<?xml version='1.0' encoding='utf-8'?>
<labwc_config>
  <touch deviceName="old-touch" mapToOutput="HDMI-0" mouseEmulation="no" />
</labwc_config>
"""


@pytest.fixture
def rc_path(fs: FakeFilesystem) -> Path:
    path = Path('/userdata/system/.config/labwc/rc.xml')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_MINIMAL_RC_XML)
    return path


@pytest.fixture
def labwc_pid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv('LABWC_PID', '12345')


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


def _action_output_name(rule: ET.Element[str], action_name: str) -> str | None:
    action = rule.find(f'./action[@name="{action_name}"]/output')

    return action.text if action is not None else None


def _output_name(rule: ET.Element[str]) -> str | None:
    return _action_output_name(rule, 'MoveToOutput')


def _focus_output_name(rule: ET.Element[str]) -> str | None:
    return _action_output_name(rule, 'FocusOutput')


def _has_fullscreen(rule: ET.Element[str]) -> bool:
    return rule.find('./action[@name="ToggleFullscreen"]') is not None


def _touch_elements(root: ET.Element[str]) -> list[ET.Element[str]]:
    return root.findall('./touch')


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

    def test_finds_existing_window_rule_by_identifier(self, rc_path: Path) -> None:
        rc_path.write_text(_EXISTING_RULES_RC_XML)
        config = LabWCConfig(path=rc_path)

        rule = config.window_rule(identifier='azahar')

        assert _output_name(rule.element) == 'HDMI-1'
        assert _focus_output_name(rule.element) == 'HDMI-1'

    def test_finds_existing_window_rule_by_identifier_and_title(self, rc_path: Path) -> None:
        rc_path.write_text(_EXISTING_RULES_RC_XML)
        config = LabWCConfig(path=rc_path)

        rule = config.window_rule(identifier='azahar', title='*Secondary Window*')

        assert _output_name(rule.element) == 'HDMI-2'
        assert _has_fullscreen(rule.element)


class TestWindowRuleMoveToOutput:
    def test_move_to_output_sets_output_name(self, rc_path: Path) -> None:
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar').move_to_output('HDMI-A-1')

        rule = _find_rule(config.root, identifier='azahar')

        assert _output_name(rule) == 'HDMI-A-1'

    def test_move_to_output_none_removes_action(self, rc_path: Path) -> None:
        rc_path.write_text(_EXISTING_RULES_RC_XML)
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar').move_to_output(None)

        rule = _find_rule(config.root, identifier='azahar')

        assert _output_name(rule) is None

    def test_move_to_output_updates_existing_output(self, rc_path: Path) -> None:
        rc_path.write_text(_EXISTING_RULES_RC_XML)
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar').move_to_output('HDMI-A-1')

        rule = _find_rule(config.root, identifier='azahar')

        assert _output_name(rule) == 'HDMI-A-1'


class TestWindowRuleFocusOutput:
    def test_focus_output_sets_output_name(self, rc_path: Path) -> None:
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='emulationstation').focus_output('HDMI-A-1')

        rule = _find_rule(config.root, identifier='emulationstation')

        assert _focus_output_name(rule) == 'HDMI-A-1'

    def test_focus_output_none_removes_action(self, rc_path: Path) -> None:
        rc_path.write_text(_EXISTING_RULES_RC_XML)
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar').focus_output(None)

        rule = _find_rule(config.root, identifier='azahar')

        assert _focus_output_name(rule) is None

    def test_supports_method_chaining_with_move_to_output(self, rc_path: Path) -> None:
        config = LabWCConfig(path=rc_path)
        rule = config.window_rule(identifier='emulationstation').focus_output('HDMI-A-1').move_to_output('HDMI-A-1')

        assert _focus_output_name(rule.element) == 'HDMI-A-1'
        assert _output_name(rule.element) == 'HDMI-A-1'


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

    def test_supports_method_chaining(self, rc_path: Path) -> None:
        config = LabWCConfig(path=rc_path)
        rule = (
            config.window_rule(identifier='azahar', title='*Secondary Window*')
            .move_to_output('HDMI-A-2')
            .toggle_fullscreen()
        )

        assert _output_name(rule.element) == 'HDMI-A-2'
        assert _has_fullscreen(rule.element)


class TestLabWCConfigSetTouchscreen:
    def test_set_touchscreen_creates_touch_element(self, rc_path: Path) -> None:
        config = LabWCConfig(path=rc_path)
        config.set_touchscreen(name='touch-panel', map_to_output_name='HDMI-A-1')

        touch_elements = _touch_elements(config.root)

        assert len(touch_elements) == 1
        assert touch_elements[0].get('deviceName') == 'touch-panel'
        assert touch_elements[0].get('mapToOutput') == 'HDMI-A-1'
        assert touch_elements[0].get('mouseEmulation') == 'no'

    def test_set_touchscreen_replaces_existing_entries(self, rc_path: Path) -> None:
        rc_path.write_text(_EXISTING_TOUCH_RC_XML)
        config = LabWCConfig(path=rc_path)
        config.set_touchscreen(name='new-touch', map_to_output_name='HDMI-A-2')

        touch_elements = _touch_elements(config.root)

        assert len(touch_elements) == 1
        assert touch_elements[0].get('deviceName') == 'new-touch'
        assert touch_elements[0].get('mapToOutput') == 'HDMI-A-2'

    def test_set_touchscreen_clear_removes_existing_entries(self, rc_path: Path) -> None:
        rc_path.write_text(_EXISTING_TOUCH_RC_XML)
        config = LabWCConfig(path=rc_path)
        config.set_touchscreen()

        assert _touch_elements(config.root) == []

    def test_set_touchscreen_requires_both_name_and_output(self, rc_path: Path) -> None:
        config = LabWCConfig(path=rc_path)
        config.set_touchscreen(name='touch-panel', map_to_output_name=None)

        assert _touch_elements(config.root) == []

    def test_set_touchscreens_maps_each_device_with_calibration(self, rc_path: Path) -> None:
        config = LabWCConfig(path=rc_path)
        config.set_touchscreens([('bottom-touch', 'DSI-1', 0), ('top-touch', 'DP-1', 1)])

        touch_elements = _touch_elements(config.root)

        assert [(t.get('deviceName'), t.get('mapToOutput')) for t in touch_elements] == [
            ('bottom-touch', 'DSI-1'),
            ('top-touch', 'DP-1'),
        ]
        matrices = {
            d.get('category'): d.findtext('./calibrationMatrix') for d in config.root.findall('./libinput/device')
        }
        assert matrices == {'bottom-touch': '1 0 0 0 1 0', 'top-touch': '0 1 0 -1 0 1'}

    def test_set_touchscreens_removes_stale_calibration(self, rc_path: Path) -> None:
        config = LabWCConfig(path=rc_path)
        config.set_touchscreens([('top-touch', 'DP-1', 1)])
        config.set_touchscreens([('bottom-touch', 'DSI-1', 0)])

        assert [t.get('deviceName') for t in _touch_elements(config.root)] == ['bottom-touch']
        assert [d.get('category') for d in config.root.findall('./libinput/device')] == ['bottom-touch']

    def test_set_touchscreen_leaves_calibration_to_udev(self, rc_path: Path) -> None:
        config = LabWCConfig(path=rc_path)
        config.set_touchscreens([('top-touch', 'DP-1', 1)])
        config.set_touchscreen(name='touch-panel', map_to_output_name='DSI-1')

        assert [t.get('deviceName') for t in _touch_elements(config.root)] == ['touch-panel']
        assert config.root.find('./libinput') is None

    def test_set_touchscreens_keeps_unrelated_libinput_devices(self, rc_path: Path) -> None:
        rc_path.write_text(
            "<labwc_config><libinput><device category='touchpad'><tap>yes</tap></device></libinput></labwc_config>"
        )
        config = LabWCConfig(path=rc_path)
        config.set_touchscreens([('top-touch', 'DP-1', 3)])
        config.set_touchscreen()

        devices = config.root.findall('./libinput/device')
        assert [d.get('category') for d in devices] == ['touchpad']


class TestLabWCConfigSave:
    def test_writes_xml(self, rc_path: Path) -> None:
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar').move_to_output('HDMI-A-1')
        config.save()

        saved = ET.parse(rc_path).getroot()
        rule = _find_rule(saved, identifier='azahar')

        assert _output_name(rule) == 'HDMI-A-1'
        assert rc_path.read_text().startswith("<?xml version='1.0' encoding='utf-8'?>")

    def test_save_does_not_reconfigure(self, rc_path: Path, mocker: MockerFixture) -> None:
        mock_run = mocker.patch('subprocess.run')
        config = LabWCConfig(path=rc_path)
        config.save()

        mock_run.assert_not_called()
        assert rc_path.read_text().startswith("<?xml version='1.0' encoding='utf-8'?>")

    def test_azahar_window_rules(self, rc_path: Path) -> None:
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar').move_to_output('HDMI-A-1')
        (
            config.window_rule(identifier='azahar', title='*Secondary Window*')
            .move_to_output('HDMI-A-2')
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


class TestLabWCConfigReconfigure:
    @pytest.mark.usefixtures('labwc_pid')
    def test_reconfigure_calls_labwc_when_labwc_pid_set(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch('subprocess.run')

        LabWCConfig.reconfigure()

        mock_run.assert_called_once_with([LABWC_BIN, '--reconfigure'], check=True)

    def test_reconfigure_skips_when_labwc_pid_unset(
        self,
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        monkeypatch.delenv('LABWC_PID', raising=False)
        mock_run = mocker.patch('subprocess.run')

        with caplog.at_level('WARNING'):
            LabWCConfig.reconfigure()

        mock_run.assert_not_called()
        assert 'LABWC_PID not set, skipping labwc reconfigure' in caplog.text

    @pytest.mark.usefixtures('labwc_pid')
    def test_labwc_reconfigure_failure_is_logged_not_raised(
        self,
        mocker: MockerFixture,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        mocker.patch(
            'subprocess.run',
            side_effect=subprocess.CalledProcessError(1, 'labwc'),
        )

        with caplog.at_level('ERROR'):
            LabWCConfig.reconfigure()

        assert 'failed to reconfigure labwc' in caplog.text
