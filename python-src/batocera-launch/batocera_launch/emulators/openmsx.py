from __future__ import annotations

import logging
import re
import shutil
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Final, cast

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import CONFIGS, SCREENSHOTS
from batocera_launch import Command, Emulator, HotkeysContext

_logger = logging.getLogger(__name__)

_OPENMSX_CONFIG: Final = Path('/usr/share/openmsx')

_MACHINE_BY_SYSTEM: Final = {
    'msx1': 'Boosted_MSX2_EN',
    'msx2': 'Boosted_MSX2_EN',
    'msx2+': 'Boosted_MSX2+_JP',
    'msxturbor': 'Boosted_MSXturboR_with_IDE',
    'colecovision': 'ColecoVision_SGM',
    'spectravideo': 'Spectravideo_SVI-328',
}


@cached_dataclass
class Openmsx(Emulator):
    @property
    def handles_hud(self) -> bool:
        return True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'openmsx',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4'], 'restore_state': 'KEY_F6'},
        }

    @cached_property
    def config_dir(self) -> Path:
        return CONFIGS / 'openmsx'

    async def configure(self) -> Command:
        share_dir = self.config_dir / 'share'
        settings_xml = share_dir / 'settings.xml'
        settings_tcl = share_dir / 'script.tcl'

        self.config_dir.mkdir(parents=True, exist_ok=True)
        (SCREENSHOTS / 'openmsx').mkdir(parents=True, exist_ok=True)

        if not share_dir.exists():
            share_dir.mkdir()
            shutil.copytree(_OPENMSX_CONFIG, share_dir, dirs_exist_ok=True)

        # always use our settings.xml file as a base
        shutil.copy2(_OPENMSX_CONFIG / 'settings.xml', share_dir)

        tree = ET.parse(settings_xml)
        root = tree.getroot()

        settings_elem = cast('ET.Element', root.find('settings'))
        fullspeed_elem = ET.Element('setting', {'id': 'fullspeedwhenloading'})
        fullspeed_elem.text = self.config.get_str('openmsx_loading', 'true')
        settings_elem.append(fullspeed_elem)

        bindings_elem = ET.Element('bindings')
        new_bind = ET.Element('bind', {'key': 'keyb F6'})
        new_bind.text = 'cycle videosource'
        bindings_elem.append(new_bind)
        root.append(bindings_elem)

        with settings_xml.open('w') as f:
            f.write("<!DOCTYPE settings SYSTEM 'settings.dtd'>\n")
            xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent='  ')
            f.write('\n'.join(line for line in xml_string.split('\n') if line.strip()))

        with settings_tcl.open('w') as file:
            file.write('filepool add -path /userdata/bios/Machines -types system_rom -position 1\n')
            file.write('filepool add -path /userdata/bios/openmsx -types system_rom -position 2\n')

            # simplify the rom name for the savestate name: drop bracketed/parenthesised tags
            save_name = re.sub(r'\([^)]*\)', '', self.rom.stem)
            save_name = re.sub(r'\[[^]]*\]', '', save_name)
            file.write('\n# -= Save state =-\n')
            file.write(f'savestate "{save_name}"\n')

            file.write('\n# -= Screenshots =-\n')
            file.write(
                'bind F5 {screenshot [utils::get_next_numbered_filename '
                '/userdata/screenshots/openmsx "[guess_title] " ".png"]}\n'
            )

            file.write('\n# -= Controller config =-\n')
            for nplayer, pad in enumerate(self.controllers[:2], start=1):
                if nplayer == 1:
                    file.write('plug joyporta joystick1\n')
                    file.write('dict set joystick1_config LEFT {-axis0 L_hat0}\n')
                    file.write('dict set joystick1_config RIGHT {+axis0 R_hat0}\n')
                    file.write('dict set joystick1_config UP {-axis1 U_hat0}\n')
                    file.write('dict set joystick1_config DOWN {+axis1 D_hat0}\n')
                if nplayer == 2:
                    file.write('plug joyportb joystick2\n')
                    file.write('dict set joystick2_config LEFT {-axis0 L_hat0}\n')
                    file.write('dict set joystick2_config RIGHT {+axis0 R_hat0}\n')
                    file.write('dict set joystick2_config UP {-axis1 U_hat0}\n')
                    file.write('dict set joystick2_config DOWN {+axis1 D_hat0}\n')

                for input_ in pad.inputs.values():
                    if input_.name == 'y':
                        file.write(f'bind "joy{nplayer} button{input_.id} down" "keymatrixdown 6 0x40"\n')
                    if input_.name == 'x':
                        file.write(f'bind "joy{nplayer} button{input_.id} down" "keymatrixdown 6 0x80"\n')
                    if input_.name == 'pagedown':
                        file.write(f'bind "joy{nplayer} button{input_.id} up" "set fastforward off"\n')
                        file.write(f'bind "joy{nplayer} button{input_.id} down" "set fastforward on"\n')
                    if input_.name == 'select':
                        file.write(f'bind "joy{nplayer} button{input_.id} down" "toggle pause"\n')
                    if input_.name == 'start':
                        file.write(f'bind "joy{nplayer} button{input_.id} down" "main_menu_toggle"\n')
                    if input_.name == 'l3':
                        file.write(f'bind "joy{nplayer} button{input_.id} down" "toggle_osd_keyboard"\n')
                    if input_.name == 'r3':
                        file.write(f'bind "joy{nplayer} button{input_.id} down" "toggle console"\n')

        args: list[str | Path] = ['/usr/bin/openmsx', '-cart', self.rom, '-script', settings_tcl]

        machine = _MACHINE_BY_SYSTEM.get(self.system)
        if machine:
            args[1:1] = ['-machine', machine]

        if self.config.get_bool('hud_support') and self.config.get_str('hud', 'none') != 'none':
            args.insert(0, 'mangohud')

        file_extension = self.rom.suffix.lower()
        if file_extension == '.zip':
            with zipfile.ZipFile(self.rom, 'r') as zip_file:
                for zip_info in zip_file.infolist():
                    candidate = Path(zip_info.filename).suffix
                    # usually a zip only holds one file, but stop at the first known media type
                    if candidate in ('.cas', '.dsk', '.ogv'):
                        _logger.debug('Zip file contains: %s', candidate)
                        file_extension = candidate
                        break

        if file_extension == '.ogv':
            _logger.debug('File is a laserdisc')
            for i, arg in enumerate(args):
                if arg == '-machine':
                    args[i + 1] = 'Pioneer_PX-7'
                elif arg == '-cart':
                    args[i] = '-laserdisc'

        if file_extension == '.cas':
            _logger.debug('File is a cassette')
            for i, arg in enumerate(args):
                if arg == '-cart':
                    args[i] = '-cassetteplayer'

        if file_extension == '.dsk':
            _logger.debug('File is a disk')
            disk_type = '-hda' if self.config.get_str('openmsx_disk') == 'hda' else '-diska'
            for i, arg in enumerate(args):
                if arg == '-cart':
                    args[i] = disk_type

        if file_extension == '.openmsx':
            # our own stacked-media playlist format: two rom/disk paths, one per line
            lines = self.rom.read_text().splitlines()
            openmsx_dir = self.rom.parent
            rom1 = openmsx_dir / lines[0].strip()
            rom2 = openmsx_dir / lines[1].strip()

            extension = rom1.suffix[1:].lower()
            if extension in ('rom', 'dsk'):
                cart_index = args.index('-cart')
                args[cart_index] = '-carta' if extension == 'rom' else '-diska'
                args[cart_index + 1] = rom1

                rom2_index = cart_index + 2
                args.insert(rom2_index, '-cartb' if extension == 'rom' else '-diskb')
                args.insert(rom2_index + 1, rom2)

        return Command(args, env={'XDG_DATA_HOME': share_dir})
