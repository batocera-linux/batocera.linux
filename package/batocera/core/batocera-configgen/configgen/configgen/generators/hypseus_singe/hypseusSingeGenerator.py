from __future__ import annotations

import filecmp
import logging
import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast

import ffmpeg

from ... import Command
from ...batoceraPaths import CONFIGS, ROMS, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

if TYPE_CHECKING:
    from ...types import HotkeysContext

_logger = logging.getLogger(__name__)

_DATA_DIR: Final = CONFIGS / 'hypseus-singe'
_CONFIG: Final = _DATA_DIR / 'hypinput.ini'
_DAPHNE_ROM_DIR: Final = ROMS / 'daphne'
_SINGE_ROM_DIR: Final = ROMS / 'singe'
_SHARE_DIR: Final = Path("/usr/share/hypseus-singe")

class HypseusSingeGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "hypseus-singe",
            "keys": { "exit": "KEY_ESC", "menu": "KEY_9" }
        }

    @staticmethod
    def find_m2v_from_txt(txt_file: Path) -> str | None:
        with txt_file.open('r') as file:
            for line in file:
                parts = line.strip().split()
                if parts:
                    filename = parts[-1]
                    if filename.endswith(".m2v"):
                        return filename
        return None

    @staticmethod
    def find_file(start_path: Path, filename: str) -> Path | None:
        if (start_path / filename).exists():
            return start_path / filename

        for root, _, files in os.walk(start_path):
            if filename in files:
                full_path = Path(root) / filename
                _logger.debug("Found m2v file in path - %s", full_path)
                return full_path

        return None

    @staticmethod
    def get_resolution(video_path: Path) -> tuple[int, int] | None:
        probe = ffmpeg.probe(video_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)

        if video_stream is None:
            return None

        width = int(video_stream['width'])
        height = int(video_stream['height'])
        sar_num = video_stream['display_aspect_ratio'].split(':')[0]
        sar_den = video_stream['display_aspect_ratio'].split(':')[1]
        sar_num = int(sar_num) if sar_num else 0
        sar_den = int(sar_den) if sar_den else 0
        if sar_num != 0 and sar_den != 0:
            ratio = sar_num / sar_den
            width = int(height * ratio)
        return width, height

    # Main entry of the module
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # copy input.ini file templates
        hypseusConfigSource = _SHARE_DIR / "hypinput_gamepad.ini"

        bezel_to_rom = {
            "ace": ["ace", "ace_a", "ace_a2", "ace91", "ace91_euro", "aceeuro"],
            "astron": ["astron", "astronp"],
            "badlands": ["badlands", "badlandsp"],
            "bega": ["bega", "begar1"],
            "captainpower": ["cpower1", "cpower2", "cpower3", "cpower4", "cpowergh"],
            "cliff": ["cliffhanger", "cliff", "cliffalt", "cliffalt2"],
            "cobra": ["cobra", "cobraab", "cobraconv", "cobram3"],
            "conan": ["conan", "future_boy"],
            "chantze_hd": ["chantze_hd", "triad_hd", "triadstone"],
            "crimepatrol": ["crimepatrol", "crimepatrol-hd", "cp_hd"],
            "dle": ["dle", "dle_alt", "dle11", "dle21"],
            "dragon": ["dragon", "dragon_trainer"],
            "drugwars": ["drugwars", "drugwars-hd", "cp2dw_hd"],
            "daitarn": ["daitarn", "daitarn_3"],
            "dle": ["dle", "dle_alt"],  # noqa: F601
            "fire_and_ice": ["fire_and_ice", "fire_and_ice_v2"],
            "galaxy": ["galaxy", "galaxyp"],
            "lair": ["lair", "lair_a", "lair_b", "lair_c", "lair_d", "lair_d2", "lair_e", "lair_f", "lair_ita", "lair_n1", "lair_x", "laireuro"],
            "lbh": ["lbh", "lbh-hd", "lbh_hd"],
            "maddog": ["maddog", "maddog-hd", "maddog_hd"],
            "maddog2": ["maddog2", "maddog2-hd", "maddog2_hd"],
            "jack": ["jack", "samurai_jack"],
            "johnnyrock": ["johnnyrock", "johnnyrock-hd", "johnnyrocknoir", "wsjr_hd"],
            "pussinboots": ["pussinboots", "puss_in_boots"],
            "spacepirates": ["spacepirates", "spacepirates-hd", "space_pirates_hd"],
        }

        def find_bezel(rom_name: str) -> str | None:
            for bezel, rom_names in bezel_to_rom.items():
                if rom_name in rom_names:
                    return bezel
            return None

        mkdir_if_not_exists(_DATA_DIR)
        if not _CONFIG.exists() or not filecmp.cmp(hypseusConfigSource, _CONFIG):
            shutil.copyfile(hypseusConfigSource, _CONFIG)

        # create a custom ini
        if not (_DATA_DIR / "custom.ini").exists():
            shutil.copyfile(_CONFIG, _DATA_DIR / "custom.ini")

        # copy required resources to userdata config folder as needed
        def copy_resources(source_dir: Path, destination_dir: Path) -> None:
            if not destination_dir.exists():
                shutil.copytree(source_dir, destination_dir)
            else:
                for source_item in source_dir.iterdir():
                    destination_item = destination_dir / source_item.name
                    if source_item.is_file():
                        if not destination_item.exists() or source_item.stat().st_mtime > destination_item.stat().st_mtime:
                            shutil.copy2(source_item, destination_item)
                    elif source_item.is_dir():
                        copy_resources(source_item, destination_item)

        directories = ["pics", "sound", "fonts", "bezels"]

        # Copy/update directories
        for directory in directories:
            copy_resources(_SHARE_DIR / directory, _DATA_DIR / directory)

        # extension used .daphne and the file to start the game is in the folder .daphne with the extension .txt
        romName = rom.stem
        frameFile = rom / f"{romName}.txt"
        commandsFile = rom / f"{romName}.commands"
        singeFile = rom / f"{romName}.singe"

        bezelFile = find_bezel(romName.lower())
        if bezelFile is not None:
            bezelFile += ".png"
        else:
            bezelFile = romName.lower() + ".png"
        bezelPath = _DATA_DIR / "bezels" / bezelFile

        # get the first video file from frameFile to determine the resolution
        m2v_filename = self.find_m2v_from_txt(frameFile)

        if m2v_filename:
            _logger.debug("First .m2v file found: %s", m2v_filename)
        else:
            _logger.debug("No .m2v files found in the text file.")

        # now get the resolution from the m2v file
        video_path = rom / m2v_filename if m2v_filename is not None else rom

        # check the path exists
        if not video_path.exists():
            _logger.debug("Could not find m2v file in path - %s", video_path)
            video_path = self.find_file(rom, cast('str', m2v_filename))

        _logger.debug("Full m2v path is: %s", video_path)

        video_resolution: tuple[int, int] | None = None
        if video_path is not None:
            video_resolution = self.get_resolution(video_path)
            _logger.debug("Resolution: %s", video_resolution)

        if system.name == "singe":
            commandArray = ['/usr/bin/hypseus',
                            "singe", "vldp", "-retropath", "-framefile", frameFile, "-script", singeFile,
                            "-fullscreen", "-gamepad", "-datadir", _DATA_DIR, "-singedir", _SINGE_ROM_DIR,
                            "-romdir", _SINGE_ROM_DIR, "-homedir", _DATA_DIR]
        else:
            commandArray = ['/usr/bin/hypseus',
                            romName, "vldp", "-framefile", frameFile, "-fullscreen",
                            "-fastboot", "-gamepad", "-datadir", _DATA_DIR,
                            "-romdir", _DAPHNE_ROM_DIR, "-homedir", _DATA_DIR]

        # controller config file
        commandArray.extend([
            '-keymapfile',
            system.config.get_bool('hypseus_joy', return_values=('custom.ini', _CONFIG.name))
        ])

        # Default -fullscreen behaviour respects game aspect ratio
        bezelRequired = False
        xratio = None
        # stretch
        match system.config.get('hypseus_ratio'):
            case 'stretch':
                commandArray.extend(["-x", str(gameResolution["width"]), "-y", str(gameResolution["height"])])
                bezelRequired = False
                if abs(gameResolution["width"] / gameResolution["height"] - 4/3) < 0.01:
                    xratio = 4/3
            case 'force_ratio':
                # 4:3
                commandArray.extend(["-x", str(gameResolution["width"]), "-y", str(gameResolution["height"])])
                commandArray.extend(["-force_aspect_ratio"])
                xratio = 4/3
                bezelRequired = True
            case _:
                # original
                if video_resolution and video_resolution[0]:
                    scaling_factor = gameResolution["height"] / video_resolution[1]
                    new_width = video_resolution[0] * scaling_factor
                    commandArray.extend(["-x", str(new_width), "-y", str(gameResolution["height"])])
                    # check if 4:3 for bezels
                    if abs(new_width / gameResolution["height"] - 4/3) < 0.01:
                        bezelRequired = True
                        xratio = 4/3
                    # unique xratio formula for fast draw game (video is 3:4)
                    # e.g.: (16/9) / (3/4) = 64/27 = ~2.37
                    elif "fastdraw" in romName.lower():
                        bezelRequired = True
                        xratio = (video_resolution[1] * gameResolution["width"]) / (video_resolution[0] * gameResolution["height"])
                    else:
                        bezelRequired = False
                else:
                    _logger.debug("Video resolution not found - using stretch")
                    commandArray.extend(["-x", str(gameResolution["width"]), "-y", str(gameResolution["height"])])
                    if abs(gameResolution["width"] / gameResolution["height"] - 4/3) < 0.01:
                        xratio = 4/3

        # Don't set bezel if screeen resolution is not conducive to needing them (i.e. CRT)
        if gameResolution["width"] / gameResolution["height"] < 1.51:
            bezelRequired = False

        # Backend - Default OpenGL
        commandArray.append("-vulkan" if system.config.get("hypseus_api") == 'Vulkan' else "-opengl")

        # Enable Bilinear Filtering
        if system.config.get_bool('hypseus_filter'):
            commandArray.append("-linear_scale")

        #The following options should only be set when system is singe.
        #-blend_sprites, -nocrosshair, -sinden or -manymouse
        if system.name == "singe":
            # Blend Sprites (Singe)
            if system.config.get_bool("singe_sprites"):
                commandArray.append("-blend_sprites")

            bordersSize = system.guns_borders_size_name(guns)
            if bordersSize is not None:
                match system.config.get("controllers.guns.borderscolor"):
                    case "red":
                        borderColor = "r"
                    case "green":
                        borderColor = "g"
                    case "blue":
                        borderColor = "b"
                    case _:
                        borderColor = "w"

                if bordersSize == "thin":
                    commandArray.extend(["-sinden", "4", borderColor])
                elif bordersSize == "medium":
                    commandArray.extend(["-sinden", "7", borderColor])
                else:
                    commandArray.extend(["-sinden", "9", borderColor])
            
            if guns: # enable manymouse for guns
                commandArray.extend(["-manymouse"]) # sinden implies manymouse
                if xratio is not None:
                    commandArray.extend(["-xratio", str(xratio)]) # accuracy correction based on ratio
            else:
                if system.config.get_bool("singe_abs"):
                    commandArray.extend(["-manymouse"]) # this is causing issues on some "non-gun" games
        
        # bezels
        if not system.config.get_bool('hypseus_bezels', True):
            bezelRequired = False

        if bezelRequired:
            if not bezelPath.exists():
                commandArray.extend(["-bezel", "default.png"])
            else:
                commandArray.extend(["-bezel", bezelFile])

        # Invert HAT Axis
        if system.config.get_bool("hypseus_axis"):
            commandArray.append("-tiphat")

        # Game rotation options for vertical screens, default is 0.
        match system.config.get('hypseus_rotate'):
            case '90' | '270' as rotate:
                commandArray.extend(["-rotate", rotate])

        # Singe joystick sensitivity, default is 5.
        if system.name == "singe" and (joystick_range := system.config.get('singe_joystick_range')):
            commandArray.extend(["-js_range", joystick_range])

        # Scanlines
        if (scanlines := system.config.get_int('hypseus_scanlines')) > 0:
            commandArray.extend(["-scanlines", "-scanline_shunt", str(scanlines)])

        # Crosshair in supported games (e.g. ActionMax, ALG)
        # needCrosshair
        if system.config.use_guns and guns and system.config.get_bool('singe_crosshair', True):
            commandArray.append("-nocrosshair")

        # Enable SDL_TEXTUREACCESS_STREAMING, can aid SBC's with SDL2 => 2.0.16
        if system.config.get_bool("hypseus_texturestream"):
            commandArray.append("-texturestream")

        # The folder may have a file with the game name and .commands with extra arguments to run the game.
        if commandsFile.is_file():
            with commandsFile.open() as f:
                commandArray.extend(f.read().split())

        # We now use SDL controller config
        return Command.Command(
            array=commandArray,
            env={
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers),
                'SDL_JOYSTICK_HIDAPI': '0',
                'MANYMOUSE_NO_XINPUT2': 'x' # disable xorg mouse => forces evdev mouse
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        if config.get("hypseus_ratio") == "stretch":
            return 16/9
        return 4/3
