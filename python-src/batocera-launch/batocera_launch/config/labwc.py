from __future__ import annotations

import logging
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Final, Self

from batocera_common.paths import HOME

from ..devices.video import find_screen

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ..types import ScreenInfo

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

    def move_to_output(self, screens: Sequence[ScreenInfo], name: str | None = None, /) -> Self:
        screen = find_screen(screens, name) if name is not None else None

        if screen is None:
            _remove_action(self.element, 'MoveToOutput')
        else:
            _set_action(self.element, 'MoveToOutput', child=('output', screen.name))

        return self

    def toggle_fullscreen(self, fullscreen: bool = True, /) -> Self:
        if not fullscreen:
            _remove_action(self.element, 'ToggleFullscreen')
        else:
            _set_action(self.element, 'ToggleFullscreen')

        return self


@dataclass(slots=True)
class LabWCConfig:
    path: Path = RC_XML
    tree: ET.ElementTree[ET.Element[str]] = field(init=False)
    root: ET.Element[str] = field(init=False)

    _window_rules_cache: dict[tuple[str | None, str | None], WindowRule] = field(init=False)
    _window_rules_element: ET.Element[str] | None = field(init=False, default=None)

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

    def _get_window_rules_element(self) -> ET.Element[str]:
        if self._window_rules_element is None:
            self._window_rules_element = self.root.find('./windowRules')

            if self._window_rules_element is None:
                self._window_rules_element = ET.SubElement(self.root, 'windowRules')

        return self._window_rules_element

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
                element = ET.SubElement(self._get_window_rules_element(), 'windowRule')

            if identifier is not None:
                element.set('identifier', identifier)

            if title is not None:
                element.set('title', title)

            self._window_rules_cache[(identifier, title)] = WindowRule(element)

        return self._window_rules_cache[(identifier, title)]

    def save(self) -> None:
        ET.indent(self.tree, space='  ')
        self.tree.write(self.path, encoding='utf-8', xml_declaration=True, short_empty_elements=True)

        try:
            subprocess.run([LABWC_BIN, '--reconfigure'], check=True)
        except subprocess.CalledProcessError:
            _logger.exception('failed to reconfigure labwc.')
