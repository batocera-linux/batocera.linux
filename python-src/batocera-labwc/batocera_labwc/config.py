from __future__ import annotations

import logging
import os
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final, Self

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import HOME

if TYPE_CHECKING:
    from collections.abc import Mapping

_logger = logging.getLogger(__name__)

RC_XML: Final = HOME / '.config' / 'labwc' / 'rc.xml'
LABWC_BIN: Final = Path('/usr/bin/labwc')


def _remove_action(window_rule: ET.Element[str], action_name: str, /) -> bool:
    found = False

    for action in window_rule.findall(f'./action[@name="{action_name}"]'):
        window_rule.remove(action)
        found = True

    return found


def _set_action(
    window_rule: ET.Element[str],
    action_name: str,
    /,
    text: str | None = None,
    child: tuple[str, str] | None = None,
    attributes: Mapping[str, str] | None = None,
) -> None:
    action = window_rule.find(f'./action[@name="{action_name}"]')

    if action is None:
        action = ET.SubElement(window_rule, 'action', {'name': action_name})

    if attributes is not None:
        for key, value in attributes.items():
            action.set(key, value)

    if text is not None:
        action.text = text
    elif child is not None:
        child_tag, child_text = child

        child_element = action.find(f'./{child_tag}')

        if child_element is None:
            child_element = ET.SubElement(action, child_tag)

        child_element.text = child_text


@dataclass(slots=True)
class WindowRule:
    element: ET.Element[str]

    def move_to_output(self, output_name: str | None = None, /) -> Self:
        if output_name is None:
            _remove_action(self.element, 'MoveToOutput')
        else:
            _set_action(self.element, 'MoveToOutput', child=('output', output_name))

        return self

    def focus_output(self, output_name: str | None = None, /) -> Self:
        if output_name is None:
            _remove_action(self.element, 'FocusOutput')
        else:
            _set_action(self.element, 'FocusOutput', child=('output', output_name))

        return self

    def toggle_fullscreen(self, fullscreen: bool = True, /) -> Self:
        if not fullscreen:
            _remove_action(self.element, 'ToggleFullscreen')
        else:
            _set_action(self.element, 'ToggleFullscreen')

        return self


@cached_dataclass
class LabWCConfig:
    path: Path = RC_XML
    tree: ET.ElementTree[ET.Element[str]] = field(init=False)
    root: ET.Element[str] = field(init=False)

    _window_rules_cache: dict[tuple[str | None, str | None], WindowRule] = field(init=False)

    @cached_property
    def window_rules_element(self) -> ET.Element[str]:
        element = self.root.find('./windowRules')

        if element is None:
            element = ET.SubElement(self.root, 'windowRules')

        return element

    @cached_property
    def core_element(self) -> ET.Element[str]:
        element = self.root.find('./core')

        if element is None:
            element = ET.SubElement(self.root, 'core')

        return element

    def __post_init__(self) -> None:
        try:
            self.tree = ET.parse(self.path)
            self.root = self.tree.getroot()
        except FileNotFoundError:
            _logger.exception('file %s not found.', self.path)
            raise
        except ET.ParseError:
            _logger.exception('file %s is not a valid XML file.', self.path)
            raise

        self._window_rules_cache = {}

    def set_touchscreen(self, name: str | None = None, map_to_output_name: str | None = None) -> None:
        # Always strip any existing <touch> elements to keep a clean slate
        for touch_element in self.root.findall('./touch'):
            self.root.remove(touch_element)

        if name is not None and map_to_output_name is not None:
            touch_element = ET.SubElement(self.root, 'touch')
            touch_element.set('deviceName', name)
            touch_element.set('mapToOutput', map_to_output_name)
            touch_element.set('mouseEmulation', 'no')

    def window_rule(self, /, *, identifier: str | None = None, title: str | None = None) -> WindowRule:
        if identifier is None and title is None:
            raise ValueError('Either identifier or title must be provided.')

        if (identifier, title) not in self._window_rules_cache:
            attribute_query = ''

            if identifier is not None:
                attribute_query = f'[@identifier="{identifier}"]'

            if title is not None:
                attribute_query = f'{attribute_query}[@title="{title}"]'

            element = self.root.find(f'./windowRules/windowRule{attribute_query}')

            if element is None:
                element = ET.SubElement(self.window_rules_element, 'windowRule')

            if identifier is not None:
                element.set('identifier', identifier)

            if title is not None:
                element.set('title', title)

            self._window_rules_cache[(identifier, title)] = WindowRule(element)

        return self._window_rules_cache[(identifier, title)]

    def save(self) -> None:
        ET.indent(self.tree, space='  ')
        self.tree.write(self.path, encoding='utf-8', xml_declaration=True, short_empty_elements=True)

    @staticmethod
    def reconfigure() -> None:
        if 'LABWC_PID' in os.environ:
            try:
                subprocess.run([LABWC_BIN, '--reconfigure'], check=True)
            except subprocess.CalledProcessError:
                _logger.exception('failed to reconfigure labwc.')
        else:
            _logger.warning('LABWC_PID not set, skipping labwc reconfigure.')
