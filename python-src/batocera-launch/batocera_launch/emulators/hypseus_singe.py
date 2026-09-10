from __future__ import annotations

import filecmp
import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Final, cast

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Command, Emulator, HotkeysContext

_logger: Final = logging.getLogger(__name__)

_CONFIG_NAME: Final = 'hypinput.ini'
_SHARE_DIR: Final = Path('/usr/share/hypseus-singe')

# Bezel images are shared across a family of related ROM variants (regional /
# alternate releases, revisions, ...); map each known variant back to the
# bezel filename it should use.
_BEZEL_TO_ROM: Final = {
    'ace': ['ace', 'ace_a', 'ace_a2', 'ace91', 'ace91_euro', 'aceeuro'],
    'astron': ['astron', 'astronp'],
    'badlands': ['badlands', 'badlandsp'],
    'bega': ['bega', 'begar1'],
    'captainpower': ['cpower1', 'cpower2', 'cpower3', 'cpower4', 'cpowergh'],
    'cliff': ['cliffhanger', 'cliff', 'cliffalt', 'cliffalt2'],
    'cobra': ['cobra', 'cobraab', 'cobraconv', 'cobram3'],
    'conan': ['conan', 'future_boy'],
    'chantze_hd': ['chantze_hd', 'triad_hd', 'triadstone'],
    'crimepatrol': ['crimepatrol', 'crimepatrol-hd', 'cp_hd'],
    'dle': ['dle', 'dle_alt', 'dle11', 'dle21'],
    'dragon': ['dragon', 'dragon_trainer'],
    'drugwars': ['drugwars', 'drugwars-hd', 'cp2dw_hd'],
    'daitarn': ['daitarn', 'daitarn_3'],
    'fire_and_ice': ['fire_and_ice', 'fire_and_ice_v2'],
    'galaxy': ['galaxy', 'galaxyp'],
    'lair': [
        'lair',
        'lair_a',
        'lair_b',
        'lair_c',
        'lair_d',
        'lair_d2',
        'lair_e',
        'lair_f',
        'lair_ita',
        'lair_n1',
        'lair_x',
        'laireuro',
    ],
    'lbh': ['lbh', 'lbh-hd', 'lbh_hd'],
    'maddog': ['maddog', 'maddog-hd', 'maddog_hd'],
    'maddog2': ['maddog2', 'maddog2-hd', 'maddog2_hd'],
    'jack': ['jack', 'samurai_jack'],
    'johnnyrock': ['johnnyrock', 'johnnyrock-hd', 'johnnyrocknoir', 'wsjr_hd', 'wsjr-hd'],
    'pussinboots': ['pussinboots', 'puss_in_boots'],
    'spacepirates': ['spacepirates', 'spacepirates-hd', 'space_pirates_hd'],
}


def _find_bezel(rom_name: str) -> str | None:
    for bezel, rom_names in _BEZEL_TO_ROM.items():
        if rom_name in rom_names:
            return bezel
    return None


def _find_m2v_from_txt(txt_file: Path) -> str | None:
    with txt_file.open('r') as file:
        for line in file:
            parts = line.strip().split()
            if parts:
                filename = parts[-1]
                if filename.endswith('.m2v'):
                    return filename
    return None


def _find_file(start_path: Path, filename: str) -> Path | None:
    if (start_path / filename).exists():
        return start_path / filename

    for root, _, files in os.walk(start_path):
        if filename in files:
            full_path = Path(root) / filename
            _logger.debug('Found m2v file in path - %s', full_path)
            return full_path

    return None


def _get_resolution(video_path: Path) -> tuple[int, int] | None:
    # Shell out to ffprobe directly (always present: batocera-emulationstation
    # already selects BR2_PACKAGE_FFMPEG_FFPROBE) rather than pulling in the
    # ffmpeg-python bindings solely for this one call.
    probe = json.loads(
        subprocess.run(
            ['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', str(video_path)],
            capture_output=True,
            check=True,
            text=True,
        ).stdout
    )
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)

    if video_stream is None:
        return None

    width = int(video_stream['width'])
    height = int(video_stream['height'])
    sar_num, sar_den = video_stream['display_aspect_ratio'].split(':')
    sar_num = int(sar_num) if sar_num else 0
    sar_den = int(sar_den) if sar_den else 0
    if sar_num != 0 and sar_den != 0:
        ratio = sar_num / sar_den
        width = int(height * ratio)
    return width, height


def _copy_resources(source_dir: Path, destination_dir: Path) -> None:
    if not destination_dir.exists():
        shutil.copytree(source_dir, destination_dir)
    else:
        for source_item in source_dir.iterdir():
            destination_item = destination_dir / source_item.name
            if source_item.is_file():
                if not destination_item.exists() or source_item.stat().st_mtime > destination_item.stat().st_mtime:
                    shutil.copy2(source_item, destination_item)
            elif source_item.is_dir():
                _copy_resources(source_item, destination_item)


@cached_dataclass
class HypseusSinge(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'hypseus-singe',
            'keys': {'exit': 'KEY_ESC', 'menu': 'KEY_9'},
        }

    @cached_property
    def in_game_ratio(self) -> float:
        if self.config.get('hypseus_ratio') == 'stretch':
            return 16 / 9
        return 4 / 3

    async def configure(self) -> Command:
        config_file = self.config_dir / _CONFIG_NAME

        # copy input.ini file templates
        hypseus_config_source = _SHARE_DIR / 'hypinput_gamepad.ini'

        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not config_file.exists() or not filecmp.cmp(hypseus_config_source, config_file):
            shutil.copyfile(hypseus_config_source, config_file)

        # create a custom ini
        custom_config_file = self.config_dir / 'custom.ini'
        if not custom_config_file.exists():
            shutil.copyfile(config_file, custom_config_file)

        # copy required resources to userdata config folder as needed
        for directory in ('pics', 'sound', 'fonts', 'bezels'):
            _copy_resources(_SHARE_DIR / directory, self.config_dir / directory)

        # extension used .daphne and the file to start the game is in the folder .daphne with the extension .txt
        rom_name = self.rom.stem
        zip_file = self.rom / f'{rom_name}.zip'
        frame_file = self.rom / f'{rom_name}.txt'
        commands_file = self.rom / f'{rom_name}.commands'
        singe_file = self.rom / f'{rom_name}.singe'

        bezel_file = _find_bezel(rom_name.lower())
        bezel_file = f'{bezel_file}.png' if bezel_file is not None else f'{rom_name.lower()}.png'
        bezel_path = self.config_dir / 'bezels' / bezel_file

        # get the first video file from frame_file to determine the resolution
        m2v_filename = _find_m2v_from_txt(frame_file)

        if m2v_filename:
            _logger.debug('First .m2v file found: %s', m2v_filename)
        else:
            _logger.debug('No .m2v files found in the text file.')

        # now get the resolution from the m2v file
        video_path = self.rom / m2v_filename if m2v_filename is not None else self.rom

        # check the path exists
        if not video_path.exists():
            _logger.debug('Could not find m2v file in path - %s', video_path)
            video_path = _find_file(self.rom, cast('str', m2v_filename))

        _logger.debug('Full m2v path is: %s', video_path)

        video_resolution: tuple[int, int] | None = None
        if video_path is not None:
            video_resolution = _get_resolution(video_path)
            _logger.debug('Resolution: %s', video_resolution)

        if self.system == 'singe':
            if zip_file.exists():
                args: list[str | Path] = [
                    'hypseus',
                    'singe',
                    'vldp',
                    '-espath',
                    '-framefile',
                    frame_file,
                    '-zlua',
                    zip_file,
                    '-fullscreen',
                    '-gamepad',
                    '-datadir',
                    self.config_dir,
                    '-singedir',
                    self.roms_dir,
                    '-romdir',
                    self.roms_dir,
                    '-homedir',
                    self.config_dir,
                ]
            else:
                args = [
                    'hypseus',
                    'singe',
                    'vldp',
                    '-espath',
                    '-framefile',
                    frame_file,
                    '-script',
                    singe_file,
                    '-fullscreen',
                    '-gamepad',
                    '-datadir',
                    self.config_dir,
                    '-singedir',
                    self.roms_dir,
                    '-romdir',
                    self.roms_dir,
                    '-homedir',
                    self.config_dir,
                ]
        else:
            args = [
                'hypseus',
                rom_name,
                'vldp',
                '-framefile',
                frame_file,
                '-fullscreen',
                '-fastboot',
                '-gamepad',
                '-datadir',
                self.config_dir,
                '-romdir',
                self.roms_dir,
                '-homedir',
                self.config_dir,
            ]

        # controller config file
        args.extend(
            [
                '-keymapfile',
                self.config.get_bool('hypseus_joy', return_values=('custom.ini', _CONFIG_NAME)),
            ]
        )

        # Default -fullscreen behaviour respects game aspect ratio
        bezel_required = False
        xratio = None
        # stretch
        match self.config.get('hypseus_ratio'):
            case 'stretch':
                args.extend(['-x', str(self.resolution.width), '-y', str(self.resolution.height)])
                bezel_required = False
                if abs(self.resolution.width / self.resolution.height - 4 / 3) < 0.01:
                    xratio = 4 / 3
            case 'force_ratio':
                # 4:3
                args.extend(['-x', str(self.resolution.width), '-y', str(self.resolution.height)])
                args.extend(['-force_aspect_ratio'])
                xratio = 4 / 3
                bezel_required = True
            case _:
                # original
                if video_resolution and video_resolution[0]:
                    scaling_factor = self.resolution.height / video_resolution[1]
                    new_width = video_resolution[0] * scaling_factor
                    args.extend(['-x', str(new_width), '-y', str(self.resolution.height)])
                    # check if 4:3 for bezels
                    if abs(new_width / self.resolution.height - 4 / 3) < 0.01:
                        bezel_required = True
                        xratio = 4 / 3
                    # unique xratio formula for fast draw game (video is 3:4)
                    # e.g.: (16/9) / (3/4) = 64/27 = ~2.37
                    elif 'fastdraw' in rom_name.lower():
                        bezel_required = True
                        xratio = (video_resolution[1] * self.resolution.width) / (
                            video_resolution[0] * self.resolution.height
                        )
                    else:
                        bezel_required = False
                else:
                    _logger.debug('Video resolution not found - using stretch')
                    args.extend(['-x', str(self.resolution.width), '-y', str(self.resolution.height)])
                    if abs(self.resolution.width / self.resolution.height - 4 / 3) < 0.01:
                        xratio = 4 / 3

        # Don't set bezel if screen resolution is not conducive to needing them (i.e. CRT)
        if self.resolution.width / self.resolution.height < 1.51:
            bezel_required = False

        # Backend - Default OpenGL
        args.append('-vulkan' if self.config.get('hypseus_api') == 'Vulkan' else '-opengl')

        # Enable Bilinear Filtering
        if self.config.get_bool('hypseus_filter'):
            args.append('-linear_scale')

        # The following options should only be set when system is singe.
        # -blend_sprites, -nocrosshair, -sinden or -manymouse
        if self.system == 'singe':
            # Blend Sprites (Singe)
            if self.config.get_bool('singe_sprites'):
                args.append('-blend_sprites')

            borders_size = self.guns_borders_size
            if borders_size is not None:
                match self.gun_borders_color:
                    case 'red':
                        border_color = 'r'
                    case 'green':
                        border_color = 'g'
                    case 'blue':
                        border_color = 'b'
                    case _:
                        border_color = 'w'

                if borders_size == 'thin':
                    args.extend(['-sinden', '4', border_color])
                elif borders_size == 'medium':
                    args.extend(['-sinden', '7', border_color])
                else:
                    args.extend(['-sinden', '9', border_color])

            if self.guns:  # enable manymouse for guns
                args.extend(['-manymouse'])  # sinden implies manymouse
                if xratio is not None:
                    args.extend(['-xratio', str(xratio)])  # accuracy correction based on ratio
            elif self.config.get_bool('singe_abs'):
                args.extend(['-manymouse'])  # this is causing issues on some "non-gun" games

        # bezels
        if not self.config.get_bool('hypseus_bezels', True):
            bezel_required = False

        if bezel_required:
            if not bezel_path.exists():
                args.extend(['-bezel', 'default.png'])
            else:
                args.extend(['-bezel', bezel_file])

        # Invert HAT Axis
        if self.config.get_bool('hypseus_axis'):
            args.append('-tiphat')

        # Game rotation options for vertical screens, default is 0.
        match self.config.get('hypseus_rotate'):
            case '90' | '270' as rotate:
                args.extend(['-rotate', rotate])
            case _:
                pass

        # Singe joystick sensitivity, default is 5.
        if self.system == 'singe' and (joystick_range := self.config.get('singe_joystick_range')):
            args.extend(['-js_range', joystick_range])

        # Scanlines
        if (scanlines := self.config.get_int('hypseus_scanlines', 0)) > 0:
            args.extend(['-scanlines', '-scanline_shunt', str(scanlines)])

        # Crosshair in supported games (e.g. ActionMax, ALG)
        if self.config.use_guns and self.guns and self.config.get_bool('singe_crosshair', True):
            args.append('-nocrosshair')

        # Enable SDL_TEXTUREACCESS_STREAMING, can aid SBC's with SDL2 => 2.0.16
        if self.config.get_bool('hypseus_texturestream'):
            args.append('-texturestream')

        # The folder may have a file with the game name and .commands with extra arguments to run the game.
        if commands_file.is_file():
            args.extend(commands_file.read_text().split())

        return Command(
            args,
            env={
                'SDL_JOYSTICK_HIDAPI': '0',
                'MANYMOUSE_NO_XINPUT2': 'x',  # disable xorg mouse => forces evdev mouse
            },
        )
