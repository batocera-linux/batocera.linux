from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Sequence

    from batocera_launch import Controller
    from batocera_launch.devices.gun import Gun

# xemu-chihiro's JVS binding namespaces (ui/xemu-input.h)
_MOUSE_BUTTON: Final = 1001
_PAD_BUTTON: Final = 2001
_PAD_AXIS: Final = 3001
_JOY_BUTTON: Final = 4001
_JOY_HALFAXIS: Final = 5001
_JOY_PEDAL: Final = 6001
_JOY_PORT_STRIDE: Final = 10000

# SDL_GamepadButton / SDL_GamepadAxis
_SOUTH: Final = 0
_EAST: Final = 1
_WEST: Final = 2
_NORTH: Final = 3
_BACK: Final = 4
_START: Final = 6
_LEFT_STICK: Final = 7
_RIGHT_STICK: Final = 8
_LEFT_SHOULDER: Final = 9
_RIGHT_SHOULDER: Final = 10
_LEFTX: Final = 0
_LEFTY: Final = 1
_RIGHTX: Final = 2
_RIGHTY: Final = 3
_LEFT_TRIGGER: Final = 4
_RIGHT_TRIGGER: Final = 5

# the pointer's buttons in SDL order, then BTN_1..BTN_8
_GUN_BUTTONS: Final = {'left': 0, 'middle': 1, 'right': 2, **{str(n): 4 + n for n in range(1, 9)}}

_GEAR_UP_INPUTS: Final = ['pagedown', 'r1']
_GEAR_DOWN_INPUTS: Final = ['pageup', 'l1']

# keys the fork moves onto the new ones at every load when they are not default
DEPRECATED: Final = {
    'chihiro.jvs.or2': ('gear_up', 'gear_down'),
    'chihiro.jvs.gs': ('card',),
    'chihiro.jvs.wmmt2': ('card',),
    'chihiro.jvs.gundam': ('card',),
    'chihiro.jvs_p2': ('gs_card',),
}


def _button(button: int, /) -> int:
    return _PAD_BUTTON + button


def _axis(axis: int, positive: bool, /) -> int:
    return _PAD_AXIS + axis * 2 + int(positive)


def _mouse(name: str, /) -> int:
    return _MOUSE_BUTTON + _GUN_BUTTONS[name]


def _update(bindings: dict[str, dict[str, int]], path: str, /, **values: int | None) -> None:
    # a button the device lacks keeps the pad's binding
    bindings[path].update({key: value for key, value in values.items() if value is not None})


_PAD: Final[dict[str, dict[str, int]]] = {
    'chihiro.jvs': {
        'start': _button(_START),
        'coin': _button(_BACK),
        'service': _button(_LEFT_STICK),
        'test': _button(_RIGHT_STICK),
        'steer_left': _axis(_LEFTX, False),
        'steer_right': _axis(_LEFTX, True),
        'gas': _axis(_RIGHT_TRIGGER, True),
        'brake': _axis(_LEFT_TRIGGER, True),
        'gear_up': _button(_RIGHT_SHOULDER),
        'gear_down': _button(_LEFT_SHOULDER),
        'card_in': _button(_NORTH),
    },
    # a pad cannot aim: the gun games stay on the mouse
    'chihiro.jvs.hotd3': {'trigger': _mouse('left'), 'body_button': _mouse('right')},
    'chihiro.jvs.vc3': {
        'trigger': _mouse('left'),
        'body_button': _mouse('right'),
        'pedal': _mouse('middle'),
        'reload': 0,
    },
    'chihiro.jvs.gs': {
        'trigger': _mouse('left'),
        'body_button': _mouse('right'),
        'change': _mouse('middle'),
        'reload': 0,
    },
    'chihiro.jvs.ctx': {
        'drive_gear': _button(_RIGHT_SHOULDER),
        'reverse': _button(_LEFT_SHOULDER),
        'jump': _button(_SOUTH),
    },
    'chihiro.jvs.or2': {'view_change': _button(_WEST)},
    'chihiro.jvs.wmmt2': {
        **{f'gear{n}': 0 for n in range(1, 7)},
        'view_change': _button(_WEST),
        'intrude_change': _button(_EAST),
    },
    'chihiro.jvs.ok': {
        'swing_left': _axis(_LEFTX, False),
        'swing_right': _axis(_LEFTX, True),
        'board_front': _axis(_LEFTY, False),
        'board_rear': _axis(_LEFTY, True),
        'left_grab': _button(_LEFT_SHOULDER),
        'right_grab': _button(_RIGHT_SHOULDER),
    },
    'chihiro.jvs.gundam': {
        'l_up': _axis(_LEFTY, False),
        'l_down': _axis(_LEFTY, True),
        'l_left': _axis(_LEFTX, False),
        'l_right': _axis(_LEFTX, True),
        'l_trigger': _axis(_LEFT_TRIGGER, True),
        'l_button': _button(_LEFT_SHOULDER),
        'r_up': _axis(_RIGHTY, False),
        'r_down': _axis(_RIGHTY, True),
        'r_left': _axis(_RIGHTX, False),
        'r_right': _axis(_RIGHTX, True),
        'r_trigger': _axis(_RIGHT_TRIGGER, True),
        'r_button': _button(_RIGHT_SHOULDER),
        'pedal': _button(_SOUTH),
    },
    # player 2 only plays the gun games, with a second gun
    'chihiro.jvs_p2': {
        'start': 0,
        'coin': 0,
        'card_in': 0,
        **{
            f'{game}_{key}': 0
            for game, keys in (
                ('hotd3', ('trigger', 'body_button')),
                ('vc3', ('trigger', 'body_button', 'pedal', 'reload')),
                ('gs', ('trigger', 'body_button', 'change', 'reload')),
            )
            for key in keys
        },
    },
}


class ControlsBuilder:
    def __init__(self, controllers: Sequence[Controller], wheel: Controller | None, guns: Sequence[Gun], /) -> None:
        self._controllers = controllers
        self._wheel = wheel
        self._guns = guns

    def build(self) -> dict[str, dict[str, int]]:
        bindings = {path: dict(values) for path, values in _PAD.items()}
        if self._wheel is not None:
            self._bind_wheel(bindings, self._wheel)
        for player, gun in enumerate(self._guns[:2]):
            self._bind_gun(bindings, player, gun)
        return bindings

    def _bind_wheel(self, bindings: dict[str, dict[str, int]], wheel: Controller, /) -> None:
        port = self._controllers.index(wheel) * _JOY_PORT_STRIDE

        def button(names: str | list[str]) -> int | None:
            for name in [names] if isinstance(names, str) else names:
                if (input := wheel.inputs.get(name)) is not None and input.type == 'button':
                    return port + _JOY_BUTTON + int(input.id)
            return None

        def pedal(name: str) -> int | None:
            if (input := wheel.inputs.get(name)) is None:
                return None
            if input.type == 'button':
                return port + _JOY_BUTTON + int(input.id)
            if input.type == 'axis':
                return port + _JOY_PEDAL + int(input.id) * 2 + int(int(input.value) > 0)
            return None

        if (steer := wheel.inputs.get('joystick1left')) is not None and steer.type == 'axis':
            left_positive = int(steer.value) > 0
            _update(
                bindings,
                'chihiro.jvs',
                steer_left=port + _JOY_HALFAXIS + int(steer.id) * 2 + int(left_positive),
                steer_right=port + _JOY_HALFAXIS + int(steer.id) * 2 + int(not left_positive),
            )

        gear_up = button(_GEAR_UP_INPUTS)
        gear_down = button(_GEAR_DOWN_INPUTS)
        _update(
            bindings,
            'chihiro.jvs',
            gas=pedal('r2'),
            brake=pedal('l2'),
            gear_up=gear_up,
            gear_down=gear_down,
            start=button('start'),
            coin=button('select'),
            card_in=button('x'),
        )
        _update(bindings, 'chihiro.jvs.ctx', drive_gear=gear_up, reverse=gear_down, jump=button('b'))
        _update(bindings, 'chihiro.jvs.or2', view_change=button('y'))
        _update(bindings, 'chihiro.jvs.wmmt2', view_change=button('y'), intrude_change=button('a'))

    def _bind_gun(self, bindings: dict[str, dict[str, int]], player: int, gun: Gun, /) -> None:
        # trigger and body button on the gun's first two, start on middle and coin on 1, as the evmapy gun keys
        def mouse(name: str) -> int | None:
            return _mouse(name) if name in gun.buttons else None

        trigger = mouse('left')
        body = mouse('right')
        start = mouse('middle')
        coin = mouse('1')
        extra = mouse('2')
        card = mouse('3')

        if player == 0:
            _update(bindings, 'chihiro.jvs', start=start, coin=coin, card_in=card)
            _update(bindings, 'chihiro.jvs.hotd3', trigger=trigger, body_button=body)
            _update(bindings, 'chihiro.jvs.vc3', trigger=trigger, body_button=body, pedal=extra)
            _update(bindings, 'chihiro.jvs.gs', trigger=trigger, body_button=body, change=extra)
        else:
            _update(
                bindings,
                'chihiro.jvs_p2',
                start=start,
                coin=coin,
                card_in=card,
                hotd3_trigger=trigger,
                hotd3_body_button=body,
                vc3_trigger=trigger,
                vc3_body_button=body,
                vc3_pedal=extra,
                gs_trigger=trigger,
                gs_body_button=body,
                gs_change=extra,
            )
