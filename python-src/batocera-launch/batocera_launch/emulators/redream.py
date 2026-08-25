from __future__ import annotations

import filecmp
import shutil
from pathlib import Path
from typing import Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import ROMS
from batocera_launch import Command, Emulator, HotkeysContext

_BINARY_SRC: Final = Path('/usr/bin/redream')

_BUTTON_MAP: Final = {
    'a': 'b',
    'b': 'a',
    'x': 'y',
    'y': 'x',
    'start': 'start',
    'select': 'menu',
    'pageup': 'turbo',
}
_HAT_MAP: Final = {'up': 0, 'down': 1, 'left': 2, 'right': 3}
_AXIS_MAP: Final = {
    'joystick1left': 0,
    'joystick1up': 1,
    # use input.id for l2/r2
    'l2': 2,
    'r2': 3,
}
_NINTENDO_GUID: Final = '030000007e0500000920000011810000'
_NINTENDO_PROFILE: Final = (
    'b:joy1,a:joy0,dpad_down:hat1,ljoy_left:-axis0,ljoy_right:+axis0,ljoy_up:-axis1,'
    'ljoy_down:+axis1,ltrig:joy6,dpad_left:hat2,rtrig:joy7,dpad_right:hat3,turbo:joy8,'
    'start:joy9,dpad_up:hat0,y:joy2,x:joy3,'
)


@cached_dataclass
class Redream(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'redream',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    @cached_property
    def roms_dir(self) -> Path:
        return ROMS / 'dreamcast'

    @cached_property
    def in_game_ratio(self) -> float:
        ratio = self.config.get_str('redreamRatio')
        return 16 / 9 if ratio in {'16:9', 'stretch'} else 4 / 3

    async def configure(self) -> Command:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        redream_exec = self.config_dir / 'redream'

        if not redream_exec.exists() or not filecmp.cmp(_BINARY_SRC, redream_exec):
            shutil.copyfile(_BINARY_SRC, redream_exec)
            redream_exec.chmod(0o0775)

        lines: list[str] = []

        # set the roms path
        lines.append(f'gamedir={self.roms_dir}')
        # force fullscreen
        lines.append('mode=exclusive fullscreen')
        lines.append('fullmode=exclusive fullscreen')

        # configure controller
        written_guids: set[str] = set()
        for controller in self.controllers[:4]:
            lines.append(f'port{controller.index}=dev:{4 + controller.index},desc:{controller.guid},type:controller')
            ctrl_profile = f'profile{controller.index}=name:{controller.guid},type:controller,deadzone:12,crosshair:1,'
            full_profile = ctrl_profile

            for input in controller.inputs.values():
                # [buttons]
                if input.type == 'button' and input.name in _BUTTON_MAP:
                    full_profile += f'{_BUTTON_MAP[input.name]}:joy{input.id},'
                # on rare occassions when triggers are buttons
                if input.type == 'button' and input.name == 'l2':
                    full_profile += f'ltrig:joy{input.id},'
                if input.type == 'button' and input.name == 'r2':
                    full_profile += f'rtrig:joy{input.id},'
                # on occassions when dpad directions are buttons
                if input.type == 'button' and input.name in {'up', 'down', 'left', 'right'}:
                    full_profile += f'dpad_{input.name}:joy{input.id},'
                # [hats]
                if input.type == 'hat' and input.name in _HAT_MAP:
                    full_profile += f'dpad_{input.name}:hat{_HAT_MAP[input.name]},'
                # [axis]
                if input.type == 'axis' and input.name in _AXIS_MAP:
                    axis_id = _AXIS_MAP[input.name]
                    # l2/r2 as axis triggers
                    if input.name == 'l2':
                        full_profile += f'ltrig:+axis{input.id},'
                    if input.name == 'r2':
                        full_profile += f'rtrig:+axis{input.id},'
                    # handle axis l,r,u,d
                    if input.name == 'joystick1left':
                        full_profile += f'ljoy_left:-axis{axis_id},'
                        full_profile += f'ljoy_right:+axis{axis_id},'
                    if input.name == 'joystick1up':
                        full_profile += f'ljoy_up:-axis{axis_id},'
                        full_profile += f'ljoy_down:+axis{axis_id},'

            # special nintendo workaround since redream makes no sense...
            if controller.guid == _NINTENDO_GUID:
                full_profile = ctrl_profile + _NINTENDO_PROFILE
            # add key to exit for evmapy to the end
            full_profile += 'exit:f10'
            # check if we have already writtent the profile, if so, we don't save it
            if controller.guid not in written_guids:
                written_guids.add(controller.guid)
                lines.append(full_profile)

        # change settings as per users options
        # [video]
        lines.extend(
            [
                f'width={self.resolution.width}',
                f'height={self.resolution.height}',
                f'fullwidth={self.resolution.width}',
                f'fullheight={self.resolution.height}',
                f'res={self.config.get_str("redreamResolution", "2")}',
                f'aspect={self.config.get_str("redreamRatio", "4:3")}',
                f'frameskip={self.config.get_str("redreamFrameSkip", "0")}',
                f'vsync={self.config.get_str("redreamVsync", "0")}',
                f'renderer={self.config.get_str("redreamRender", "hle_perstrip")}',
            ]
        )
        # [system]
        lines.extend(
            [
                f'region={self.config.get_str("redreamRegion", "usa")}',
                f'language={self.config.get_str("redreamLanguage", "english")}',
                f'broadcast={self.config.get_str("redreamBroadcast", "ntsc")}',
                f'cable={self.config.get_str("redreamCable", "vga")}',
            ]
        )

        (self.config_dir / 'redream.cfg').write_text('\n'.join(lines) + '\n')

        return Command(
            [redream_exec, self.rom],
            env={'SDL_JOYSTICK_HIDAPI': '0', 'SDL_AUDIODRIVER': 'alsa'},
        )
