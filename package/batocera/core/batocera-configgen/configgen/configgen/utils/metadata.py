from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Final

_logger = logging.getLogger(__name__)

# hardcoded list of system for arcade
# this list can be found in es_system.yml
# at this stage we don't know if arcade will be kept as one system only in metadata, so i hardcode this list for now
_ARCADE_SYSTEMS: Final = {
    'lindbergh',
    'naomi',
    'naomi2',
    'atomiswave',
    'fbneo',
    'mame',
    'neogeo',
    'triforce',
    'hypseus-singe',
    'model2',
    'model3',
    'hikaru',
    'gaelco',
    'cave3rd',
    'namco2x6',
    'namco22',
}

def _short_name_from_path(path: str | Path) -> str:
    redname = Path(path).stem.lower()
    inpar   = False
    inblock = False
    ret = ""
    for c in redname:
        if not inpar and not inblock and ( (c >= 'a' and c <= 'z') or (c >= '0' and c <= '9') ):
            ret += c
        elif c == '(':
            inpar = True
        elif c == ')':
            inpar = False
        elif c == '[':
            inblock = True
        elif c == ']':
            inblock = False
    return ret

def _update_metadata_from_element(md: dict[str, str], element: ET.Element, /, extra_log_text: str = '') -> None:
    for child in element:
        for attrib_name, attrib_value in child.attrib.items():
            key = f'{child.tag}_{attrib_name}'
            md[key] = attrib_value
            _logger.info("found game metadata %s=%s%s", key, attrib_value, extra_log_text)

def get_games_meta_data(db_xml: str | Path, system: str, rom: str | Path) -> dict[str, str]:
    # load the database
    tree = ET.parse(db_xml)
    root: ET.Element = tree.getroot()
    game = _short_name_from_path(rom)
    md: dict[str, str] = {}

    _logger.info("looking for game metadata (%s, %s) in %s", system, game, db_xml)

    target_system = 'arcade' if system in _ARCADE_SYSTEMS else system

    for system_element in root.iterfind('./system[@id]'):
        if target_system not in system_element.attrib['id'].split(','):
            continue

        # search the game named default
        if (default_element := system_element.find('./game[@id="default"]')) is not None:
            _update_metadata_from_element(md, default_element, extra_log_text=' (system level)')

        for game_element in system_element.iterfind('./game[@id!="default"]'):
            if game_element.attrib['id'] not in game:
                continue
            _update_metadata_from_element(md, game_element)
            return md

    return md
