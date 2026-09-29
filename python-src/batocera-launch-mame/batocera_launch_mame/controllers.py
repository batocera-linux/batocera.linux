from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from batocera_common.dataclasses import cached_dataclass
from batocera_launch_mame_common import (
    ControlConfig,
    MessAnalogMapping,
    MessComboMapping,
    MessMainMapping,
    get_input_definition,
    has_stick,
    load_mame_control_mapping,
    load_mess_system_controls,
    reverse_mapping,
)

from .base import MAMEBase

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch import Controller

_logger: Final = logging.getLogger(__name__)

_BBC_SYSTEMS: Final = frozenset({'bbcb', 'bbcm', 'bbcm512', 'bbcmc'})
_APPLE2_SYSTEMS: Final = frozenset({'apple2p', 'apple2e', 'apple2ee'})

_PEDAL_KEYS: Final = {1: 'c', 2: 'v', 3: 'b', 4: 'n'}
_UI_PORTS: tuple[tuple[str, str, str], ...] = (
    ('UI_DOWN', 'DOWN', 'JOYSTICK_DOWN'),
    ('UI_LEFT', 'LEFT', 'JOYSTICK_LEFT'),
    ('UI_UP', 'UP', 'JOYSTICK_UP'),
    ('UI_RIGHT', 'RIGHT', 'JOYSTICK_RIGHT'),
)


def _mess_use_controls(mess_system_name: str, special_controller: str, /) -> str:
    if mess_system_name in _BBC_SYSTEMS:
        return 'bbc' if special_controller == 'none' else f'bbc-{special_controller}'
    if mess_system_name in _APPLE2_SYSTEMS:
        return 'apple2' if special_controller == 'none' else f'apple2-{special_controller}'
    return mess_system_name


def _resolve_pad_key(controller: Controller, key: str, /) -> tuple[str, bool] | None:
    if key in controller.inputs:
        return key, False

    reversed_key = reverse_mapping(key)

    if reversed_key is not None and reversed_key in controller.inputs:
        return key, True

    return None


@cached_dataclass
class MAMEControllers(MAMEBase):
    def write_control_config(
        self, config_dir: Path, mess_system_name: str, special_controller: str, custom_cfg: bool, /
    ) -> None:
        default_control_config = ControlConfig(config_dir / 'default.cfg')
        overwrite_mame = not (default_control_config.exists() and custom_cfg)

        use_controls = _mess_use_controls(mess_system_name, special_controller)
        _logger.debug('Using %s for controller config.', use_controls)

        default_control_config.initialize_crosshairs(self.config.get_str('mame_crosshair'))

        mappings = load_mame_control_mapping(self.mame_control_scheme)
        mess_controls = load_mess_system_controls(mess_system_name, use_controls)

        system_control_config: ControlConfig | None = None
        overwrite_system = True

        if mess_controls is not None:
            system_control_config = ControlConfig(config_dir / f'{mess_system_name}.cfg', mess_system_name)
            custom_config = self.config.get_bool('customcfg')
            per_game_config = config_dir != (self.config_dir / mess_system_name)
            overwrite_system = not (system_control_config.exists() and (custom_config or per_game_config))

            # Hide the LCD display on CD-i
            if use_controls == 'cdimono1':
                system_control_config.remove_system_elements('video')
                system_video = system_control_config.add_system_element('video')
                system_control_config.create_child_element(
                    system_video,
                    'target',
                    index='0',
                    view='Main Screen Standard (4:3)' if self.bezel_set == 'none' else 'Upright_Artwork',
                )

            # If using BBC keyboard controls, enable keyboard to gamepad
            if use_controls == 'bbc':
                system_control_config.add_input_element('keyboard', tag=':', enabled='1')

        for nplayer, controller in enumerate(self.controllers, start=1):
            mappings_use = mappings.copy()

            if not has_stick(controller):
                mappings_use['JOYSTICK_UP'] = 'up'
                mappings_use['JOYSTICK_DOWN'] = 'down'
                mappings_use['JOYSTICK_LEFT'] = 'left'
                mappings_use['JOYSTICK_RIGHT'] = 'right'

            if self.config.use_wheels and any(
                wheel.joystick_index == controller.index for wheel in self.wheels.values()
            ):
                _logger.debug('controller %s has a wheel', controller.index + 1)
                mappings_use = {
                    name: key for name, key in mappings_use.items() if key not in {'l2', 'r2', 'joystick1left'}
                }
                mappings_use['PEDAL'] = 'r2'
                mappings_use['PEDAL2'] = 'l2'
                mappings_use['PADDLE'] = 'joystick1left'

            default_control_config.add_common_player_ports(nplayer)

            for mapping, mapped_key in mappings_use.items():
                resolved = _resolve_pad_key(controller, mapped_key)
                if resolved is None:
                    continue

                _, is_mapping_reversed = resolved

                sequence = self.__generate_pad_sequence(
                    controller,
                    mapped_key,
                    reversed=is_mapping_reversed,
                    mapping=mapping,
                    player_number=nplayer,
                    use_mame_control_scheme=True,
                    include_coin=mapping == 'COIN' and nplayer <= 4,
                )

                if mapping in ('START', 'COIN'):
                    default_control_config.add_sequence_port(
                        f'{mapping}{nplayer}', sequence=sequence, tag='standard', mask='', defvalue=''
                    )
                    default_control_config.add_sequence_port(
                        f'P{nplayer}_{"START" if mapping == "START" else "SELECT"}',
                        sequence=sequence,
                        tag='standard',
                        mask='',
                        defvalue='',
                    )
                else:
                    default_control_config.add_sequence_port(f'P{nplayer}_{mapping}', sequence=sequence)

            # UI Mappings
            if nplayer == 1:
                for ui_type, kb_key, mapping_name in _UI_PORTS:
                    default_control_config.add_sequence_port(
                        ui_type,
                        sequence=(
                            f'KEYCODE_{kb_key} OR '
                            f'{
                                self.__generate_pad_sequence(
                                    controller,
                                    mappings_use[mapping_name],
                                    reversed=has_stick(controller) and ui_type in {"UI_DOWN", "UI_RIGHT"},
                                )
                            }'
                        ),
                        tag='standard',
                        mask='',
                        defvalue='',
                    )

                default_control_config.add_sequence_port(
                    'UI_SELECT',
                    sequence=(f'KEYCODE_ENTER OR {self.__generate_pad_sequence(controller, "b")}'),
                    tag='standard',
                    mask='',
                    defvalue='',
                )

            if mess_controls is not None and system_control_config is not None:
                joycode = controller.index + 1

                for mess_control in mess_controls.values():
                    if nplayer != mess_control.player:
                        continue

                    if isinstance(mess_control, MessAnalogMapping):
                        inc_key = mappings_use.get(mess_control.incMapping)
                        dec_key = mappings_use.get(mess_control.decMapping)
                        inc_use = mappings_use.get(mess_control.incUseMapping)
                        dec_use = mappings_use.get(mess_control.decUseMapping)

                        if inc_key is None or dec_key is None or inc_use is None or dec_use is None:
                            continue

                        inc_resolved = _resolve_pad_key(controller, inc_key)
                        dec_resolved = _resolve_pad_key(controller, dec_key)

                        if inc_resolved is None or dec_resolved is None:
                            continue

                        _, inc_reversed = inc_resolved
                        _, dec_reversed = dec_resolved

                        system_control_config.add_sequence_port(
                            mess_control.key,
                            tag=mess_control.tag,
                            mask=str(mess_control.mask),
                            defvalue=str(mess_control.default),
                            key_delta=str(mess_control.delta),
                            sequences=[
                                (
                                    'increment',
                                    self.__generate_pad_sequence(
                                        controller,
                                        inc_key,
                                        reversed=inc_reversed,
                                        ignore_axis=True,
                                        input_key=inc_use,
                                    ),
                                ),
                                (
                                    'decrement',
                                    self.__generate_pad_sequence(
                                        controller,
                                        dec_key,
                                        reversed=dec_reversed,
                                        ignore_axis=True,
                                        input_key=dec_use,
                                    ),
                                ),
                                (
                                    'standard',
                                    'NONE' if not mess_control.axis else f'JOYCODE_{joycode}_{mess_control.axis}',
                                ),
                            ],
                        )
                        continue

                    mapped_key = mappings_use.get(mess_control.useMapping)
                    if mapped_key is None:
                        continue

                    resolved = _resolve_pad_key(controller, mapped_key)
                    if resolved is None:
                        continue

                    _, reversed_flag = resolved
                    sequence = self.__generate_pad_sequence(
                        controller,
                        mess_control.mapping,
                        reversed=reversed_flag,
                        input_key=mapped_key,
                    )

                    if isinstance(mess_control, MessComboMapping):
                        sequence = f'KEYCODE_{mess_control.kbMapping} OR {sequence}'

                    target = (
                        default_control_config if isinstance(mess_control, MessMainMapping) else system_control_config
                    )

                    target.add_sequence_port(
                        mess_control.key,
                        sequence=sequence,
                        tag=mess_control.tag,
                        mask=str(mess_control.mask),
                        defvalue=str(mess_control.default),
                    )

        if self.config.use_guns and len(self.guns) > len(self.controllers):
            for gun_number in range(len(self.controllers) + 1, len(self.guns) + 1):
                pedal_key = self.__pedal_key(gun_number)
                default_control_config.add_common_player_ports(gun_number)

                gun_mappings = self.all_mame_control_mappings[1]

                for mapping in gun_mappings:
                    default_control_config.add_gun_port(gun_number, mapping, gun_mappings, pedal_key)

        if overwrite_mame:
            _logger.debug('Saving %s', default_control_config.path)
            default_control_config.save()

        if mess_controls is not None and overwrite_system and system_control_config is not None:
            _logger.debug('Saving %s', system_control_config.path)
            system_control_config.save()

    def __generate_pad_sequence(
        self,
        controller: Controller,
        key: str,
        /,
        *,
        reversed: bool = False,
        ignore_axis: bool = False,
        mapping: str = '',
        player_number: int = 1,
        input_key: str | None = None,
        use_mame_control_scheme: bool = False,
        include_coin: bool = False,
    ) -> str:
        lookup = input_key if input_key is not None else key

        if reversed:
            lookup = reverse_mapping(lookup) or lookup

        if lookup not in controller.inputs:
            return 'unknown'

        is_wheel = (
            use_mame_control_scheme
            and self.config.use_wheels
            and any(wheel.joystick_index == controller.index for wheel in self.wheels.values())
        )
        sequence = get_input_definition(
            controller,
            controller.inputs[lookup],
            key,
            reversed,
            control_scheme=self.mame_control_scheme if use_mame_control_scheme else None,
            ignore_axis=ignore_axis,
            is_wheel=is_wheel,
        )

        _mappings, gun_mappings, mouse_mappings = self.all_mame_control_mappings

        if mapping in gun_mappings:
            sequence += f' OR GUNCODE_{player_number}_{gun_mappings[mapping]}'
            if gun_mappings[mapping] == 'BUTTON2' and (pedal_key := self.__pedal_key(player_number)) is not None:
                sequence += f' OR KEYCODE_{pedal_key.upper()}'

        if mapping in mouse_mappings:
            mouse_player = player_number if self.config.get_bool('multimouse') else 1
            sequence += f' OR MOUSECODE_{mouse_player}_{mouse_mappings[mapping]}'

        if include_coin:
            sequence += f' OR KEYCODE_{player_number}_{player_number + 4}'

        return sequence

    def __pedal_key(self, player_number: int, /) -> str | None:
        return self.config.get_str(f'controllers.pedals{player_number}', _PEDAL_KEYS.get(player_number))
