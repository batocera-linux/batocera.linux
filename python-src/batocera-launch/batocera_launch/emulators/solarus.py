from __future__ import annotations

from typing import TYPE_CHECKING, Final

from batocera_launch import Command, Controller, Emulator, HotkeysContext, cached_dataclass, cached_property

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch import Controllers, Input

_KEYMAPPING: Final = {
    'action': 'a',
    'attack': 'b',
    'item1': 'y',
    'item2': 'x',
    'pause': 'start',
    'right': 'right',
    'up': 'up',
    'left': 'left',
    'down': 'down',
}

_REVERSE_AXIS: Final = {
    'up': 'down',
    'left': 'right',
}


def _key2val(input: Input, reverse: bool, /) -> str | None:
    if input.type == 'button':
        return f'button {input.id}'
    if input.type == 'hat':
        if input.value == '1':
            return 'hat 0 up'
        if input.value == '2':
            return 'hat 0 right'
        if input.value == '4':
            return 'hat 0 down'
        if input.value == '8':
            return 'hat 0 left'
        return None
    if input.type == 'axis':
        if (reverse and input.value == '-1') or (not reverse and input.value == '1'):
            return f'axis {input.id} +'
        return f'axis {input.id} -'
    return None


def _write_pad_config(config_dir: Path, controllers: Controllers, joystick: str | None, /) -> None:
    keymapping = dict(_KEYMAPPING)
    if joystick in {'joystick1', 'joystick2'}:
        keymapping['up'] = f'{joystick}up'
        keymapping['down'] = f'{joystick}down'
        keymapping['left'] = f'{joystick}left'
        keymapping['right'] = f'{joystick}right'

    config_dir.mkdir(parents=True, exist_ok=True)
    with (config_dir / 'pads.ini').open('w', encoding='ascii') as f:
        if pad := Controller.find_player_number(controllers, 1):
            for key, mapped in keymapping.items():
                if mapped not in pad.inputs:
                    continue
                if (value := _key2val(pad.inputs[mapped], False)) is not None:
                    f.write(f'{key}={value}\n')
                if (
                    key in _REVERSE_AXIS
                    and pad.inputs[mapped].type == 'axis'
                    and (value := _key2val(pad.inputs[mapped], True)) is not None
                ):
                    f.write(f'{_REVERSE_AXIS[key]}={value}\n')


@cached_dataclass
class Solarus(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'solarus',
            'keys': {'exit': ['KEY_LEFTALT', 'KEY_F4']},
        }

    async def configure(self) -> Command:
        args: list[str | Path] = ['solarus-run', '-fullscreen=yes', '-cursor-visible=no', '-lua-console=no']

        for nplayer, pad in enumerate(self.controllers, start=1):
            if nplayer == 1 and 'hotkey' in pad.inputs and 'start' in pad.inputs:
                args.append(f'-quit-combo={pad.inputs["hotkey"].id}+{pad.inputs["start"].id}')
            args.append(f'-joypad-num{nplayer}={pad.index}')

        _write_pad_config(self.config_dir, self.controllers, self.config.get_str('joystick'))

        args.append(self.rom)

        return Command(
            args,
            env={
                'SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS': '0',
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )
