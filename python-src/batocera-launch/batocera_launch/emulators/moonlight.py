from __future__ import annotations

import shutil
from configparser import ConfigParser
from pathlib import Path
from typing import Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.key_value_config import KeyValueConfig
from batocera_common.paths import CONFIGS, HOME
from batocera_launch import BatoceraException, Command, Emulator, HotkeysContext

# moonlight is split across two upstream clients that batocera may ship: moonlight-qt
# (a Qt GUI, preferred when present) and moonlight-embedded (a lightweight CLI client,
# built for boards without Qt). Only one of the two binaries is ever actually installed
# on a given image, so which code path runs below is decided purely by which binary
# exists on disk at launch time.
_MOONLIGHT_QT_EXECUTABLE: Final = Path('/usr/bin/moonlight-qt')
_MOONLIGHT_EMBEDDED_EXECUTABLE: Final = Path('/usr/bin/moonlight')

# moonlight-qt stores the paired host address here once paired through its own UI.
_MOONLIGHT_QT_HOST_CONFIG: Final = HOME / '.config' / 'Moonlight Game Streaming Project' / 'Moonlight.conf'

# moonlight-embedded looks for its SDL controller mapping database at this fixed path.
_MOONLIGHT_EMBEDDED_CONTROLLER_DB: Final = Path('/usr/share/moonlight/gamecontrollerdb.txt')


@cached_dataclass
class Moonlight(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'moonlight',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @property
    def target_video_mode(self) -> str:
        return 'default'

    @cached_property
    def sdl_controller_db_path(self) -> Path:
        return _MOONLIGHT_EMBEDDED_CONTROLLER_DB

    async def configure(self) -> Command:
        args = self._configure_qt() if _MOONLIGHT_QT_EXECUTABLE.is_file() else self._configure_embedded()

        return Command(
            args,
            env={
                'XDG_DATA_DIRS': CONFIGS,
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )

    def _get_moonlight_qt_host(self) -> str | None:
        # We should move this...
        if not _MOONLIGHT_QT_HOST_CONFIG.exists():
            return None

        try:
            config = ConfigParser()
            config.read(_MOONLIGHT_QT_HOST_CONFIG)
            if config.has_section('hosts') and '1\\manualaddress' in config['hosts']:
                return config['hosts']['1\\manualaddress']
        except Exception:
            return None

        return None

    def _configure_qt(self) -> list[str | Path]:
        args: list[str | Path] = [str(_MOONLIGHT_QT_EXECUTABLE)]

        host = self._get_moonlight_qt_host()
        if not host:
            return args

        # resolution
        match self.config.get_str('moonlight_resolution'):
            case '1':
                args.append('--1080')
            case '2':
                args.append('--4K')
            case _:
                args.append('--720')

        # framerate
        match self.config.get_str('moonlight_framerate'):
            case '0':
                framerate = '30'
            case '2':
                framerate = '120'
            case _:
                framerate = '60'
        args.append('--fps')
        args.append(framerate)

        # bitrate
        match self.config.get_str('moonlight_bitrate'):
            case '0':
                bitrate = '5000'
            case '1':
                bitrate = '10000'
            case '2':
                bitrate = '20000'
            case '3':
                bitrate = '50000'
            case _:
                bitrate = None  # Moonlight default
        if bitrate is not None:
            args.append('--bitrate')
            args.append(bitrate)

        # quit remote app on exit
        # NOTE: mirrors the old generator's truthiness check verbatim - any non-empty
        # stored value (including the literal string "false") is treated as enabled.
        if self.config.get_str('moonlight_quitapp'):
            args.append('--quit-after')
        else:
            args.append('--no-quit-after')

        # host
        args.append('stream')
        args.append(host)

        # app
        args.append(self.rom.read_text().rstrip())

        return args

    def _configure_embedded(self) -> list[str | Path]:
        self._generate_moonlight_config()
        game_name, conf_file = self._get_real_game_name_and_config_file()

        args: list[str | Path] = [
            str(_MOONLIGHT_EMBEDDED_EXECUTABLE),
            'stream',
            '-config',
            conf_file,
            '-app',
            game_name,
            '-debug',
        ]

        # write our own gamecontrollerdb.txt file before launching the game
        self.write_sdl_controller_db()

        return args

    def _get_real_game_name_and_config_file(self) -> tuple[str, Path]:
        game_list = self.config_dir / 'gamelist.txt'
        staging_config = self.config_dir / 'staging' / 'moonlight.conf'

        # find the real game name
        with game_list.open() as f:
            for line in f:
                try:
                    gfe_rom, gfe_game, conf_file_string = line.rstrip().split(';')
                    conf_file = Path(conf_file_string)
                except ValueError:
                    gfe_rom, gfe_game = line.rstrip().split(';')
                    conf_file = staging_config

                # If found
                if gfe_rom == self.rom.id:
                    return gfe_game, conf_file

        raise BatoceraException(f'{self.rom.id} was not found in the Moonlight game list')

    def _generate_moonlight_config(self) -> None:
        config_file = self.config_dir / 'moonlight.conf'
        staging_dir = self.config_dir / 'staging'
        staging_config = staging_dir / 'moonlight.conf'

        staging_dir.mkdir(parents=True, exist_ok=True)

        # If user made config file exists, copy to staging directory for use
        if config_file.exists():
            shutil.copy(config_file, staging_config)
            return

        # truncate existing config and create new one
        staging_config.open('w').close()

        moonlight_config = KeyValueConfig(staging_config, separator=' ')

        # resolution
        match self.config.get_str('moonlight_resolution'):
            case '1':
                width, height = '1920', '1080'
            case '2':
                width, height = '3840', '2160'
            case _:
                width, height = '1280', '720'

        moonlight_config['width'] = width
        moonlight_config['height'] = height

        # rotate
        moonlight_config['rotate'] = self.config.get_str('moonlight_rotate', '0')

        # framerate
        match self.config.get_str('moonlight_framerate'):
            case '0':
                framerate = '30'
            case '2':
                framerate = '120'
            case _:
                framerate = '60'
        moonlight_config['fps'] = framerate

        # bitrate
        match self.config.get_str('moonlight_bitrate'):
            case '0':
                bitrate = '5000'
            case '1':
                bitrate = '10000'
            case '2':
                bitrate = '20000'
            case '3':
                bitrate = '50000'
            case _:
                bitrate = '-1'  # Moonlight default
        moonlight_config['bitrate'] = bitrate

        # codec
        moonlight_config['codec'] = self.config.get_str('moonlight_codec', 'auto')

        # sops (Streaming Optimal Playable Settings)
        moonlight_config['sops'] = self.config.get_bool('moonlight_sops', True, return_values=('true', 'false'))

        # quit remote app on exit
        moonlight_config['quitappafter'] = self.config.get_bool('moonlight_quitapp', return_values=('true', 'false'))

        # view only
        moonlight_config['viewonly'] = self.config.get_bool('moonlight_viewonly', return_values=('true', 'false'))

        # platform - we only select sdl (best compatibility)
        # required for controllers to work
        moonlight_config['platform'] = 'sdl'

        # Directory to store encryption keys
        moonlight_config['keydir'] = str(self.config_dir / 'keydir')

        # lan or wan streaming - ideally lan
        moonlight_config['remote'] = self.config.get_str('moonlight_remote', 'no')

        # Enable 5.1/7.1 surround sound
        if surround := self.config.get_str('moonlight_surround'):
            moonlight_config['surround'] = surround
        else:
            moonlight_config['#surround'] = '5.1'

        moonlight_config.write()
