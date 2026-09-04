from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from batocera_common.paths import BATOCERA_SHARE_DIR
from batocera_labwc.cli import main
from batocera_labwc.config import LabWCConfig

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem
    from pytest_mock import MockerFixture

pytestmark = pytest.mark.usefixtures('fs')

_MINIMAL_RC_XML = """\
<?xml version='1.0' encoding='utf-8'?>
<labwc_config>
</labwc_config>
"""

_RULES_YAML = """\
main:
  - identifier: emulationstation
    actions:
      - name: FocusOutput
        output: primary
      - name: MoveToOutput
        output: primary
  - identifier: batocera-backglass-window
    actions:
      - name: MoveToOutput
        output: secondary
        remove_if_missing: true
  - title: Batocera Control Center
    actions:
      - name: MoveToOutput
        output: secondary
        remove_if_missing: true

azahar:
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

vpinball:
  - identifier: VPinballX_BGFX
    title: Visual Pinball Player
    actions:
      - name: MoveToOutput
        output: primary|secondary
  - identifier: VPinballX_BGFX
    title: Visual Pinball Backglass
    actions:
      - name: MoveToOutput
        output: secondary|primary

plain_secondary:
  - identifier: plain-app
    actions:
      - name: MoveToOutput
        output: secondary

toggle_off:
  - identifier: azahar
    actions:
      - name: ToggleFullscreen
        value: false

focus_remove:
  - identifier: emulationstation
    actions:
      - name: FocusOutput
        output: primary
        remove_if_missing: true

plain_focus:
  - identifier: emulationstation
    actions:
      - name: FocusOutput
        output: primary

both_empty_primary_fallback:
  - identifier: fallback-app
    actions:
      - name: MoveToOutput
        output: primary|secondary
        remove_if_missing: true

both_empty_secondary_fallback:
  - identifier: fallback-app
    actions:
      - name: MoveToOutput
        output: secondary|primary
        remove_if_missing: true

invalid:
  - actions:
      - name: MoveToOutput
        output: primary
"""


@pytest.fixture
def rc_path(fs: FakeFilesystem) -> Path:
    path = Path('/userdata/system/.config/labwc/rc.xml')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_MINIMAL_RC_XML)
    return path


@pytest.fixture
def rules_path(fs: FakeFilesystem) -> Path:
    path = BATOCERA_SHARE_DIR / 'labwc' / 'labwc-rules.yml'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_RULES_YAML)
    return path


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


def _run_main(monkeypatch: pytest.MonkeyPatch, *argv: str) -> None:
    monkeypatch.setattr('sys.argv', ['batocera-labwc-config', *argv])
    main()


class TestMain:
    def test_reconfigure_only_skips_config_load(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mocker: MockerFixture,
    ) -> None:
        config_cls = mocker.patch('batocera_labwc.cli.LabWCConfig')

        _run_main(monkeypatch, '--reconfigure')

        config_cls.reconfigure.assert_called_once_with()
        config_cls.assert_not_called()

    def test_applies_main_rules_and_saves(
        self,
        rc_path: Path,
        rules_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mocker: MockerFixture,
    ) -> None:
        reconfigure = mocker.patch('batocera_labwc.cli.LabWCConfig.reconfigure')

        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--primary',
            'HDMI-A-1',
            '--secondary',
            'HDMI-A-2',
        )

        saved = ET.parse(rc_path).getroot()
        es_rule = _find_rule(saved, identifier='emulationstation')
        backglass = _find_rule(saved, identifier='batocera-backglass-window')
        bcc = _find_rule(saved, title='Batocera Control Center')

        assert _focus_output_name(es_rule) == 'HDMI-A-1'
        assert _output_name(es_rule) == 'HDMI-A-1'
        assert _output_name(backglass) == 'HDMI-A-2'
        assert _output_name(bcc) == 'HDMI-A-2'
        reconfigure.assert_not_called()

    def test_applies_named_rule_set(
        self,
        rc_path: Path,
        rules_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--primary',
            'HDMI-A-1',
            '--secondary',
            'HDMI-A-2',
            'azahar',
        )

        saved = ET.parse(rc_path).getroot()
        primary = _find_rule(saved, identifier='azahar')
        secondary = _find_rule(saved, identifier='azahar', title='*Secondary Window*')

        assert _output_name(primary) == 'HDMI-A-1'
        assert _output_name(secondary) == 'HDMI-A-2'
        assert _has_fullscreen(secondary)

    def test_unknown_rule_set_applies_no_window_rules(
        self,
        rc_path: Path,
        rules_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--primary',
            'HDMI-A-1',
            '--secondary',
            'HDMI-A-2',
            'missing',
        )

        assert ET.parse(rc_path).getroot().find('./windowRules') is None

    def test_empty_rules_yaml_applies_no_window_rules(
        self,
        rc_path: Path,
        fs: FakeFilesystem,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        path = BATOCERA_SHARE_DIR / 'labwc' / 'labwc-rules.yml'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('')

        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--primary',
            'HDMI-A-1',
            '--secondary',
            'HDMI-A-2',
        )

        assert ET.parse(rc_path).getroot().find('./windowRules') is None

    def test_named_rule_set_falls_back_when_secondary_empty(
        self,
        rc_path: Path,
        rules_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--primary',
            'HDMI-A-1',
            '--secondary',
            '',
            'azahar',
        )

        saved = ET.parse(rc_path).getroot()
        secondary = _find_rule(saved, identifier='azahar', title='*Secondary Window*')

        assert _output_name(_find_rule(saved, identifier='azahar')) == 'HDMI-A-1'
        assert _output_name(secondary) == 'HDMI-A-1'
        assert _has_fullscreen(secondary)

    def test_vpinball_rule_set_uses_output_fallbacks(
        self,
        rc_path: Path,
        rules_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--primary',
            '',
            '--secondary',
            'HDMI-A-2',
            'vpinball',
        )

        saved = ET.parse(rc_path).getroot()
        player = _find_rule(saved, identifier='VPinballX_BGFX', title='Visual Pinball Player')
        backglass = _find_rule(saved, identifier='VPinballX_BGFX', title='Visual Pinball Backglass')

        assert _output_name(player) == 'HDMI-A-2'
        assert _output_name(backglass) == 'HDMI-A-2'

    def test_vpinball_prefers_primary_when_both_present(
        self,
        rc_path: Path,
        rules_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--primary',
            'HDMI-A-1',
            '--secondary',
            'HDMI-A-2',
            'vpinball',
        )

        saved = ET.parse(rc_path).getroot()
        player = _find_rule(saved, identifier='VPinballX_BGFX', title='Visual Pinball Player')
        backglass = _find_rule(saved, identifier='VPinballX_BGFX', title='Visual Pinball Backglass')

        assert _output_name(player) == 'HDMI-A-1'
        assert _output_name(backglass) == 'HDMI-A-2'

    def test_skips_move_when_secondary_empty_without_remove_if_missing(
        self,
        rc_path: Path,
        rules_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='plain-app').move_to_output('HDMI-A-1')
        config.save()

        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--primary',
            'HDMI-A-1',
            '--secondary',
            '',
            'plain_secondary',
        )

        assert _output_name(_find_rule(ET.parse(rc_path).getroot(), identifier='plain-app')) == 'HDMI-A-1'

    def test_remove_if_missing_clears_move_when_secondary_empty(
        self,
        rc_path: Path,
        rules_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='batocera-backglass-window').move_to_output('HDMI-A-2')
        config.save()

        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--primary',
            'HDMI-A-1',
            '--secondary',
            '',
        )

        saved = ET.parse(rc_path).getroot()

        assert _output_name(_find_rule(saved, identifier='batocera-backglass-window')) is None
        assert _output_name(_find_rule(saved, identifier='emulationstation')) == 'HDMI-A-1'

    def test_remove_if_missing_clears_focus_when_primary_empty(
        self,
        rc_path: Path,
        rules_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='emulationstation').focus_output('HDMI-A-1')
        config.save()

        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--primary',
            '',
            '--secondary',
            'HDMI-A-2',
            'focus_remove',
        )

        assert _focus_output_name(_find_rule(ET.parse(rc_path).getroot(), identifier='emulationstation')) is None

    def test_skips_focus_when_primary_empty_without_remove_if_missing(
        self,
        rc_path: Path,
        rules_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='emulationstation').focus_output('HDMI-A-1')
        config.save()

        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--primary',
            '',
            '--secondary',
            'HDMI-A-2',
            'plain_focus',
        )

        assert _focus_output_name(_find_rule(ET.parse(rc_path).getroot(), identifier='emulationstation')) == 'HDMI-A-1'

    @pytest.mark.parametrize('rule_set', ['both_empty_primary_fallback', 'both_empty_secondary_fallback'])
    def test_fallback_with_both_outputs_empty_clears_when_remove_if_missing(
        self,
        rc_path: Path,
        rules_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        rule_set: str,
    ) -> None:
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='fallback-app').move_to_output('HDMI-A-1')
        config.save()

        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--primary',
            '',
            '--secondary',
            '',
            rule_set,
        )

        assert _output_name(_find_rule(ET.parse(rc_path).getroot(), identifier='fallback-app')) is None

    def test_toggle_fullscreen_can_disable(
        self,
        rc_path: Path,
        rules_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        config = LabWCConfig(path=rc_path)
        config.window_rule(identifier='azahar').toggle_fullscreen()
        config.save()

        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--primary',
            'HDMI-A-1',
            '--secondary',
            'HDMI-A-2',
            'toggle_off',
        )

        assert not _has_fullscreen(_find_rule(ET.parse(rc_path).getroot(), identifier='azahar'))

    def test_raises_when_rule_missing_identifier_and_title(
        self,
        rc_path: Path,
        rules_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        with pytest.raises(ValueError, match="at least an 'identifier' or a 'title'"):
            _run_main(
                monkeypatch,
                '--config-path',
                str(rc_path),
                '--primary',
                'HDMI-A-1',
                '--secondary',
                'HDMI-A-2',
                'invalid',
            )

    def test_does_not_apply_rules_without_both_outputs(
        self,
        rc_path: Path,
        rules_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--primary',
            'HDMI-A-1',
        )

        assert ET.parse(rc_path).getroot().find('./windowRules') is None

    def test_sets_touchscreen_with_primary(
        self,
        rc_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--primary',
            'HDMI-A-1',
            '--touchscreen',
            'touch-panel',
        )

        touch_elements = _touch_elements(ET.parse(rc_path).getroot())

        assert len(touch_elements) == 1
        assert touch_elements[0].get('deviceName') == 'touch-panel'
        assert touch_elements[0].get('mapToOutput') == 'HDMI-A-1'

    def test_touchscreen_without_primary_clears_mapping(
        self,
        rc_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        config = LabWCConfig(path=rc_path)
        config.set_touchscreen(name='old-touch', map_to_output_name='HDMI-A-1')
        config.save()

        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--touchscreen',
            'touch-panel',
        )

        assert _touch_elements(ET.parse(rc_path).getroot()) == []

    def test_reconfigure_after_save(
        self,
        rc_path: Path,
        rules_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mocker: MockerFixture,
    ) -> None:
        reconfigure = mocker.patch('batocera_labwc.cli.LabWCConfig.reconfigure')

        _run_main(
            monkeypatch,
            '--config-path',
            str(rc_path),
            '--primary',
            'HDMI-A-1',
            '--secondary',
            'HDMI-A-2',
            '--reconfigure',
            'azahar',
        )

        saved = ET.parse(rc_path).getroot()

        assert _output_name(_find_rule(saved, identifier='azahar')) == 'HDMI-A-1'
        reconfigure.assert_called_once_with()

    def test_save_only_when_no_outputs_or_touchscreen(
        self,
        rc_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        mocker: MockerFixture,
    ) -> None:
        reconfigure = mocker.patch('batocera_labwc.cli.LabWCConfig.reconfigure')

        _run_main(monkeypatch, '--config-path', str(rc_path))

        assert rc_path.read_text().startswith("<?xml version='1.0' encoding='utf-8'?>")
        assert ET.parse(rc_path).getroot().tag == 'labwc_config'
        reconfigure.assert_not_called()
