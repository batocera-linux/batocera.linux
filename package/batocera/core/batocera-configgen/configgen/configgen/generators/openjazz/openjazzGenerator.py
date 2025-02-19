from __future__ import annotations

import logging
import os
import struct
from pathlib import Path
from typing import TYPE_CHECKING, Final

from ... import Command
from ...batoceraPaths import CACHE, CONFIGS, ROMS, SAVES, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator

_logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ...types import HotkeysContext

# Path to the configuration file
_CONFIG: Final = CONFIGS / 'openjazz' / 'openjazz.cfg'
STRING_LENGTH = 32  # Max character length for `characterName`
CONTROLS = 16  # Number of control settings

class OpenJazzGenerator(Generator):
    def __init__(self):
        # Default configuration attributes
        self.version: int = 6
        self.video_width: int = 640
        self.video_height: int = 480
        self.video_scale: int = 1
        self.fullscreen: bool = True

        # Initialize controls with default values
        self.controls_keys: list[int] = [
            1073741906, 1073741905, 1073741904, 1073741903,
            32, 32, 1073742050, 1073742052, 13, 27, 49, 50
        ]

        self.controls_buttons: list[int] = [
            51, 52, 53, 4294967295, 4294967295, 4294967295,
            4294967295, 2, 4, 1, 3, 8, 7,
            4294967295, 4294967295, 4294967295
        ]

        self.controls_axes: list[tuple[int, int]] = [
            (4294967295, 4294967295), (4294967295, 4),
            (4294967295, 4294967295), (1, 0),
            (1, 1), (0, 0), (0, 1),
            (4294967295, 0), (4294967295, 0),
            (4294967295, 0), (4294967295, 0),
            (4294967295, 0), (4294967295, 0),
            (4294967295, 0), (4294967295, 0),
            (4294967295, 0)
        ]

        self.controls_hats: list[tuple[int, int]] = [
            (4294967295, 0), (4294967295, 0),
            (4294967295, 0), (4294967295, 0),
            (4294967295, 0), (4294967295, 0),
            (0, 1), (0, 4),
            (0, 8), (0, 2),
            (4294967295, 0), (4294967295, 0),
            (4294967295, 0), (4294967295, 0),
            (4294967295, 0), (4294967295, 0)
        ]

        self.character_name: str = "Jazz"
        self.character_colors: list[int] = [255, 255, 255, 255]
        self.music_volume: int = 255
        self.sound_volume: int = 255
        self.many_birds: bool = False
        self.leave_unneeded: bool = False
        self.slow_motion: bool = False
        self.scale2x: bool = True

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "OpenJazz",
            "keys": { "exit": ["KEY_LEFTALT", "KEY_F4"] }
        }

    def load(self, filename=_CONFIG):
        if not Path(filename).exists():
            _logger.info("No config file found, creating default configuration")
            self.create_default_config(filename)
            return

        try:
            with filename.open("rb") as file:
                # Read version
                data = file.read(1)
                if not data:
                    _logger.warning("Empty config file, creating default configuration")
                    self.create_default_config(filename)
                    return

                self.version = struct.unpack("B", data)[0]
                _logger.debug("Loading configuration version: %s", self.version)

                # Video settings
                self.video_width = struct.unpack("<H", file.read(2))[0]
                self.video_height = struct.unpack("<H", file.read(2))[0]
                video_opts = struct.unpack("B", file.read(1))[0]
                self.fullscreen = bool(video_opts & 1)
                self.video_scale = video_opts >> 1

                # Controls
                self.controls_keys = []
                for _ in range(CONTROLS - 4):
                    key = struct.unpack("<I", file.read(4))[0]
                    self.controls_keys.append(key)

                self.controls_buttons = []
                for _ in range(CONTROLS):
                    button = struct.unpack("<I", file.read(4))[0]
                    self.controls_buttons.append(button)

                self.controls_axes = []
                for _ in range(CONTROLS):
                    axis_x = struct.unpack("<I", file.read(4))[0]
                    axis_y = struct.unpack("<I", file.read(4))[0]
                    self.controls_axes.append((axis_x, axis_y))

                self.controls_hats = []
                for _ in range(CONTROLS):
                    hat_id = struct.unpack("<I", file.read(4))[0]
                    hat_value = struct.unpack("<I", file.read(4))[0]
                    self.controls_hats.append((hat_id, hat_value))

                # Character settings
                name_bytes = file.read(STRING_LENGTH)
                name_bytes = [struct.unpack("B", file.read(1))[0] for _ in range(STRING_LENGTH)]
                self.character_name = "".join(chr(b) for b in name_bytes if b != 0).strip()

                # Colors
                self.character_colors = []
                for _ in range(4):
                    color = struct.unpack("B", file.read(1))[0]
                    self.character_colors.append(color)

                # Volume settings
                self.music_volume = struct.unpack("B", file.read(1))[0]
                self.sound_volume = struct.unpack("B", file.read(1))[0]

                # Gameplay options
                gameplay_opts = struct.unpack("B", file.read(1))[0]
                self.many_birds = bool(gameplay_opts & 1)
                self.leave_unneeded = bool(gameplay_opts & 2)
                self.slow_motion = bool(gameplay_opts & 4)
                self.scale2x = not bool(gameplay_opts & 8)

        except Exception as e:
            _logger.error("Error loading configuration: %s", e)
            _logger.info("Creating new default configuration")
            self.create_default_config(filename)

    def create_default_config(self, filename: Path):
        _logger.info("Creating default configuration file")
        mkdir_if_not_exists(filename.parent)

        try:
            with filename.open("wb") as file:
                # Version
                file.write(struct.pack("B", self.version))

                # Video settings
                file.write(struct.pack("<H", self.video_width))
                file.write(struct.pack("<H", self.video_height))
                video_opts = (self.fullscreen) | (self.video_scale << 1)
                file.write(struct.pack("B", video_opts))

                # Controls - Keys
                for key in self.controls_keys:
                    file.write(struct.pack("<I", key))

                # Default buttons
                for button in self.controls_buttons:
                    file.write(struct.pack("<I", button))

                # Default axes
                for x, y in self.controls_axes:
                    file.write(struct.pack("<I", x))  # Axis X
                    file.write(struct.pack("<I", y))  # Axis Y

                # Default hats
                for id, value in self.controls_hats:
                    file.write(struct.pack("<I", id))  # Hat ID
                    file.write(struct.pack("<I", value))  # Hat value

                # Character name
                name_bytes = self.character_name.encode('utf-8')[:STRING_LENGTH]
                name_bytes = name_bytes.ljust(STRING_LENGTH, b'\x00')
                file.write(name_bytes)

                # Colours
                for color in self.character_colors:
                    file.write(struct.pack("B", color))

                # Volume
                file.write(struct.pack("B", self.music_volume))
                file.write(struct.pack("B", self.sound_volume))

                # Gameplay options
                gameplay_opts = (self.many_birds) | (self.leave_unneeded << 1) | \
                                (self.slow_motion << 2) | (not self.scale2x << 3)
                file.write(struct.pack("B", gameplay_opts))

        except Exception as e:
            _logger.error("Error creating default configuration: %s", e)

    def save(self, filename=_CONFIG):
        _logger.info("Saving configuration")
        try:
            with filename.open("wb") as file:
                # Version
                file.write(struct.pack("B", self.version))

                # Video settings
                file.write(struct.pack("<H", self.video_width))
                file.write(struct.pack("<H", self.video_height))
                video_opts = (self.fullscreen) | (self.video_scale << 1)
                file.write(struct.pack("B", video_opts))

                # Controls
                for key in self.controls_keys:
                    file.write(struct.pack("<I", key))

                for button in self.controls_buttons:
                    file.write(struct.pack("<I", button))

                for axis_x, axis_y in self.controls_axes:
                    file.write(struct.pack("<I", axis_x))
                    file.write(struct.pack("<I", axis_y))

                for hat_id, hat_value in self.controls_hats:
                    file.write(struct.pack("<I", hat_id))
                    file.write(struct.pack("<I", hat_value))

                # Character name
                name_bytes = self.character_name.encode('utf-8')[:STRING_LENGTH]
                name_bytes = name_bytes.ljust(STRING_LENGTH, b'\x00')
                file.write(name_bytes)

                # Colors
                for color in self.character_colors:
                    file.write(struct.pack("B", color))

                # Volume
                file.write(struct.pack("B", self.music_volume))
                file.write(struct.pack("B", self.sound_volume))

                # Gameplay options
                gameplay_opts = (self.many_birds) | (self.leave_unneeded << 1) | \
                              (self.slow_motion << 2) | (not self.scale2x << 3)
                file.write(struct.pack("B", gameplay_opts))

        except Exception as e:
            _logger.error("Error saving configuration: %s", e)

    def print_config(self):
        _logger.info("OpenJazz Configuration:")
        _logger.info("Version: %s", self.version)
        _logger.info("Resolution: %sx%s", self.video_width, self.video_height)
        _logger.info("Fullscreen: %s", self.fullscreen)
        _logger.info("Video Scale: %s", self.video_scale)
        _logger.info("Character Name: %s", self.character_name)
        _logger.info("Character Colors: %s", self.character_colors)
        _logger.info("Music Volume: %s", self.music_volume)
        _logger.info("Sound Volume: %s", self.sound_volume)
        _logger.info("Many Birds: %s", self.many_birds)
        _logger.info("Leave Unneeded: %s", self.leave_unneeded)
        _logger.info("Slow Motion: %s", self.slow_motion)
        _logger.info("Scale2x: %s", self.scale2x)
        _logger.info("Controls Configuration:")
        _logger.info("Keys: %s", self.controls_keys)
        _logger.info("Buttons: %s", self.controls_buttons)
        _logger.info("Axes: %s", self.controls_axes)
        _logger.info("Hats: %s", self.controls_hats)

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        # Load configuration file
        self.load()
        self.print_config()

        # Controller config mapping example
        jazzMapping = {
            'a': 'jump',
            'b': 'fire',
            'x': 'swim up',
            'y': 'weapon',
            'select': 'back',
            'start': 'enter',
            'up': 'up',
            'down': 'down',
            'left': 'left',
            'right': 'right',
        }

        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            controller = playersControllers[playercontroller]
            if nplayer == 1:
                for index in controller.inputs:
                    input = controller.inputs[index]
                    # We only need to write button layouts as hats & axis are already configured by default correctly
                    if input.type == 'button':
                        # Write buttons in order to the appropriate slots of controls_buttons
                        if input.name == 'a':
                            self.controls_buttons[7] = int(input.id)
                        elif input.name == 'b':
                            self.controls_buttons[9] = int(input.id)
                        elif input.name== 'x':
                            self.controls_buttons[8] = int(input.id)
                        elif input.name == 'y':
                            self.controls_buttons[10] = int(input.id)
                        elif input.name == 'select':
                            self.controls_buttons[12] = int(input.id)
                        elif input.name == 'start':
                            self.controls_buttons[11] = int(input.id)
                _logger.info("Configured Controls - Buttons: %s", self.controls_buttons)

            nplayer += 1

        # User configuration
        if system.isOptSet("jazz_resolution"):
            resolution = system.config["jazz_resolution"]
            width_str, height_str = resolution.split('x')
            self.video_width = int(width_str)
            self.video_height = int(height_str)
        else:
            self.video_width = int(gameResolution["width"])
            self.video_height = int(gameResolution["height"])

        # Save the changes
        self.save()

        # Attempt to change directory to the game's assets
        try:
            os.chdir(ROMS / "openjazz")
        except Exception as e:
            _logger.error("Error: %s", e)

        commandArray = ["OpenJazz"]

        return Command.Command(
            array=commandArray,
            env={
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_CACHE_HOME': CACHE,
                'XDG_DATA_HOME': SAVES,
                'SDL_GAMECONTROLLERCONFIG': generate_sdl_game_controller_config(playersControllers)
            }
        )

    def getInGameRatio(self, config, gameResolution, rom):
        return 16 / 9
