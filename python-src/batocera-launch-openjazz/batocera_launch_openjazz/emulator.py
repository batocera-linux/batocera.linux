from __future__ import annotations

import logging
import struct
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, Self

from batocera_common.paths import CACHE, CONFIGS, ROMS, SAVES
from batocera_launch import Command, Controller, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path
    from typing import BinaryIO

_logger = logging.getLogger(__name__)

_STRING_LENGTH: Final = 32  # Max character length for `characterName`
_CONTROLS: Final = 19  # Number of control settings
_ROM_DIR: Final = ROMS / 'openjazz'

_BUTTON_SLOTS: Final = {
    'a': 4,  # Jump
    'b': 6,  # Fire
    'x': 5,  # Swim
    'y': 7,  # Change
    'select': 9,  # Escape
    'start': 8,  # Enter
}

_char = struct.Struct('B')
_short = struct.Struct('<H')
_int = struct.Struct('<i')


def _read_char(reader: BinaryIO, /) -> int:
    return _char.unpack(reader.read(1))[0]


def _write_char(writer: BinaryIO, data: int, /) -> None:
    writer.write(_char.pack(data))


def _read_short(reader: BinaryIO) -> int:
    return _short.unpack(reader.read(2))[0]


def _write_short(writer: BinaryIO, data: int, /) -> None:
    writer.write(_short.pack(data))


def _read_int(reader: BinaryIO) -> int:
    return _int.unpack(reader.read(4))[0]


def _write_int(writer: BinaryIO, data: int, /) -> None:
    writer.write(_int.pack(data))


@dataclass(slots=True)
class _OpenJazzConfig:
    path: Path
    version: int = 6
    video_width: int = 640
    video_height: int = 480
    fullscreen: bool = True
    video_scale: int = 1
    keys: list[int] = field(
        default_factory=lambda: [
            1073741906,  # Up
            1073741905,  # Down
            1073741904,  # Left
            1073741903,  # Right
            32,  # Jump
            32,  # Swim
            1073742050,  # Fire
            1073742052,  # Change
            13,  # Enter
            27,  # Escape
            49,  # Blaster
            50,  # Toaster
            51,  # Missle
            52,  # Bouncer
            53,  # TNT
        ]
    )
    buttons: list[int] = field(
        default_factory=lambda: [
            -1,  # Up
            -1,  # Down
            -1,  # Left
            -1,  # Right
            2,  # Jump
            4,  # Swim
            1,  # Fire
            3,  # Change
            8,  # Enter
            7,  # Escape
            -1,  # Blaster
            -1,  # Toaster
            -1,  # Missle
            -1,  # Bouncer
            -1,  # TNT
            -1,  # Stats
            4,  # Pause
            -1,  # Yes
            -1,  # No
        ]
    )
    axes: list[tuple[int, int]] = field(
        default_factory=lambda: [
            (1, 0),  # Up
            (1, 1),  # Down
            (0, 0),  # Left
            (0, 1),  # Right
            (-1, 0),  # Jump
            (-1, 0),  # Swim
            (-1, 0),  # Fire
            (-1, 0),  # Change
            (-1, 0),  # Enter
            (-1, 0),  # Escape
            (-1, 0),  # Blaster
            (-1, 0),  # Toaster
            (-1, 0),  # Missle
            (-1, 0),  # Bouncer
            (-1, 0),  # TNT
            (-1, 0),  # Stats
            (-1, 0),  # Pause
            (-1, 0),  # Yes
            (-1, 0),  # No
        ]
    )
    hats: list[tuple[int, int]] = field(
        default_factory=lambda: [
            (0, 1),  # Up
            (0, 4),  # Down
            (0, 8),  # Left
            (0, 2),  # Right
            (-1, 0),  # Jump
            (-1, 0),  # Swim
            (-1, 0),  # Fire
            (-1, 0),  # Change
            (-1, 0),  # Enter
            (-1, 0),  # Escape
            (-1, 0),  # Blaster
            (-1, 0),  # Toaster
            (-1, 0),  # Missle
            (-1, 0),  # Bouncer
            (-1, 0),  # TNT
            (-1, 0),  # Stats
            (-1, 0),  # Pause
            (-1, 0),  # Yes
            (-1, 0),  # No
        ]
    )
    character_name: str = 'Jazz'
    character_colors: list[int] = field(default_factory=lambda: [255, 255, 255, 255])
    music_volume: int = 255
    sound_volume: int = 255
    many_birds: bool = False
    leave_unneeded: bool = False
    slow_motion: bool = False
    scale_2x: bool = True

    def save(self) -> None:
        _logger.info('Saving configuration')
        try:
            with self.path.open('wb') as f:
                _write_char(f, 6)

                _write_short(f, self.video_width)
                _write_short(f, self.video_height)
                _write_char(f, (self.video_scale << 1) | self.fullscreen)

                for key in self.keys:
                    _write_int(f, key)

                for button in self.buttons:
                    _write_int(f, button)

                for axis, direction in self.axes:
                    _write_int(f, axis)
                    _write_int(f, direction)

                for hat, direction in self.hats:
                    _write_int(f, hat)
                    _write_int(f, direction)

                name_bytes = self.character_name.encode('utf-8')[:_STRING_LENGTH].ljust(_STRING_LENGTH, b'\x00')
                f.write(name_bytes)

                for color in self.character_colors:
                    _write_char(f, color)

                _write_char(f, self.music_volume)
                _write_char(f, self.sound_volume)
                _write_char(
                    f,
                    self.many_birds | (self.leave_unneeded << 1) | (self.slow_motion << 2) | (self.scale_2x << 3),
                )
        except Exception:
            _logger.exception('Error saving configuration')

    @classmethod
    def create_default(cls, path: Path, /) -> Self:
        _logger.info('Creating default configuration file')
        path.parent.mkdir(parents=True, exist_ok=True)

        cfg = cls(path)
        cfg.save()

        return cfg

    @classmethod
    def load(cls, path: Path, /) -> Self:
        if not path.exists():
            _logger.info('No config file found, creating default configuration')
            return cls.create_default(path)

        try:
            with path.open('rb') as f:
                version = _read_char(f)
                video_width = _read_short(f)
                video_height = _read_short(f)

                video_options = _read_char(f)

                fullscreen = bool(video_options & 1)

                if video_options >= 10:
                    video_options = 2

                video_scale = video_options >> 1

                keys = [_read_int(f) for _ in range(_CONTROLS - 4)]
                buttons = [_read_int(f) for _ in range(_CONTROLS)]
                axes = [(_read_int(f), _read_int(f)) for _ in range(_CONTROLS)]
                hats = [(_read_int(f), _read_int(f)) for _ in range(_CONTROLS)]

                name_bytes = [_read_char(f) for _ in range(_STRING_LENGTH)]
                character_name = ''.join(chr(byte) for byte in name_bytes)
                character_colors = [_read_char(f), _read_char(f), _read_char(f), _read_char(f)]

                music_volume = _read_char(f)
                sound_volume = _read_char(f)

                opts = _read_char(f)
                many_birds = bool(opts & 1)
                leave_unneeded = bool(opts & 2)
                slow_motion = bool(opts & 4)
                scale_2x = not bool(opts & 8)

                return cls(
                    path,
                    version=version,
                    video_width=video_width,
                    video_height=video_height,
                    fullscreen=fullscreen,
                    video_scale=video_scale,
                    keys=keys,
                    buttons=buttons,
                    axes=axes,
                    hats=hats,
                    character_name=character_name,
                    character_colors=character_colors,
                    music_volume=music_volume,
                    sound_volume=sound_volume,
                    many_birds=many_birds,
                    leave_unneeded=leave_unneeded,
                    slow_motion=slow_motion,
                    scale_2x=scale_2x,
                )
        except Exception:
            _logger.exception('Error loading configuration')
            _logger.info('Creating new default configuration')
            return cls.create_default(path)


def _log_config(cfg: _OpenJazzConfig, /) -> None:
    _logger.info('OpenJazz Configuration:')
    _logger.info('Version: %s', cfg.version)
    _logger.info('Resolution: %sx%s', cfg.video_width, cfg.video_height)
    _logger.info('Fullscreen: %s', cfg.fullscreen)
    _logger.info('Video Scale: %s', cfg.video_scale)
    _logger.info('Character Name: %s', cfg.character_name)
    _logger.info('Character Colors: %s', cfg.character_colors)
    _logger.info('Music Volume: %s', cfg.music_volume)
    _logger.info('Sound Volume: %s', cfg.sound_volume)
    _logger.info('Many Birds: %s', cfg.many_birds)
    _logger.info('Leave Unneeded: %s', cfg.leave_unneeded)
    _logger.info('Slow Motion: %s', cfg.slow_motion)
    _logger.info('Scale2x: %s', cfg.scale_2x)
    _logger.info('Controls Configuration:')
    _logger.info('Keys: %s', cfg.keys)
    _logger.info('Buttons: %s', cfg.buttons)
    _logger.info('Axes: %s', cfg.axes)
    _logger.info('Hats: %s', cfg.hats)


@cached_dataclass
class OpenJazz(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'OpenJazz',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @property
    def execution_path(self) -> Path | None:
        return _ROM_DIR

    @cached_property
    def in_game_ratio(self) -> float:
        return 16 / 9

    async def configure(self) -> Command:
        cfg = _OpenJazzConfig.load(self.config_dir / 'openjazz.cfg')
        _log_config(cfg)

        if controller := Controller.find_player_number(self.controllers, 1):
            for input in controller.inputs.values():
                # Hats and axes are already configured correctly by default.
                if input.type == 'button' and (slot := _BUTTON_SLOTS.get(input.name)) is not None:
                    cfg.buttons[slot] = int(input.id)
            _logger.info('Configured Controls - Buttons: %s', cfg.buttons)

        width_str, height_str = self.config.get_str(
            'jazz_resolution',
            f'{self.resolution.width}x{self.resolution.height}',
        ).split('x')
        cfg.video_width = int(width_str)
        cfg.video_height = int(height_str)

        cfg.save()

        return Command(
            ['OpenJazz'],
            env={
                'XDG_CONFIG_HOME': CONFIGS,
                'XDG_CACHE_HOME': CACHE,
                'XDG_DATA_HOME': SAVES,
            },
        )
