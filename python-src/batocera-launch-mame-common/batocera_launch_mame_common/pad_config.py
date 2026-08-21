from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol

from batocera_launch import cached_property

from .control_config import ControlConfig
from .mame_controls import load_mame_control_mapping
from .mess_controls import (
    MessAnalogMapping,
    MessComboMapping,
    MessControlMapping,
    MessMainMapping,
    load_mess_system_controls,
)

if TYPE_CHECKING:
    from pathlib import Path

    from batocera_launch import Controller, Controllers, Guns, Rom, SystemConfig

    from .control_config import ControlConfig as ControlConfigType
    from .mame_control_scheme import MameControlScheme

_logger = logging.getLogger(__name__)

_UI_PORTS: tuple[tuple[str, str, str], ...] = (
    ('UI_DOWN', 'DOWN', 'JOYSTICK_DOWN'),
    ('UI_LEFT', 'LEFT', 'JOYSTICK_LEFT'),
    ('UI_UP', 'UP', 'JOYSTICK_UP'),
    ('UI_RIGHT', 'RIGHT', 'JOYSTICK_RIGHT'),
)

_BBC_SYSTEMS = frozenset({'bbcb', 'bbcm', 'bbcm512', 'bbcmc'})
_APPLE2_SYSTEMS = frozenset({'apple2p', 'apple2e', 'apple2ee'})


def has_stick(controller: Controller, /) -> bool:
    return 'joystick1up' in controller.inputs


def reverse_mapping(key: str, /) -> str | None:
    if key == 'joystick1down':
        return 'joystick1up'
    if key == 'joystick1right':
        return 'joystick1left'
    if key == 'joystick2down':
        return 'joystick2up'
    if key == 'joystick2right':
        return 'joystick2left'
    return None


def _mess_use_controls(mess_system_name: str, special_controller: str, /) -> str:
    if mess_system_name in _BBC_SYSTEMS:
        return 'bbc' if special_controller == 'none' else f'bbc-{special_controller}'
    if mess_system_name in _APPLE2_SYSTEMS:
        return 'apple2' if special_controller == 'none' else f'apple2-{special_controller}'
    return mess_system_name


class PadConfigHost(Protocol):
    @property
    def controllers(self) -> Controllers: ...

    @property
    def config(self) -> SystemConfig: ...

    @property
    def rom(self) -> Rom: ...

    @property
    def guns(self) -> Guns: ...

    @cached_property
    def mame_control_scheme(self) -> MameControlScheme: ...

    def generate_pad_sequence(
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
    ) -> str: ...

    def should_configure_pads(self) -> bool: ...

    def can_reverse_pad_mapping(self, controller: Controller, reversed_key: str, /) -> bool: ...

    def should_emit_unbound_pad_mapping(self) -> bool: ...

    def adjust_control_mappings(self, controller: Controller, mappings: dict[str, str], /) -> dict[str, str]: ...

    def prepare_control_config(self, config: ControlConfigType, /) -> None: ...

    def prepare_player_config(self, config: ControlConfigType, player_number: int, /) -> None: ...

    def extra_start_coin_port_type(self, mapping: str, player_number: int, /) -> str | None: ...

    def cdi_screen_view(self) -> str: ...

    def should_overwrite_system_cfg(self, cfg_path: Path, mess_system_name: str, alt_cfg_exists: bool, /) -> bool: ...

    def finish_control_config(self, config: ControlConfigType, /) -> None: ...

    def ui_combo_input(self, controller: Controller, ui_type: str, mapped_key: str, /) -> tuple[str, bool]: ...

    def ui_select_key(self) -> str: ...


class PadConfigMixin:
    def should_configure_pads(self) -> bool:
        return True

    def can_reverse_pad_mapping(self, controller: Controller, reversed_key: str, /) -> bool:
        raise NotImplementedError

    def should_emit_unbound_pad_mapping(self) -> bool:
        return False

    def adjust_control_mappings(self, controller: Controller, mappings: dict[str, str], /) -> dict[str, str]:
        return mappings

    def prepare_control_config(self, config: ControlConfig, /) -> None: ...

    def prepare_player_config(self, config: ControlConfig, player_number: int, /) -> None: ...

    def extra_start_coin_port_type(self, mapping: str, player_number: int, /) -> str | None:
        return None

    def cdi_screen_view(self) -> str:
        return 'Main Screen Standard (4:3)'

    def should_overwrite_system_cfg(
        self: PadConfigHost, cfg_path: Path, mess_system_name: str, alt_cfg_exists: bool, /
    ) -> bool:
        raise NotImplementedError

    def finish_control_config(self, config: ControlConfig, /) -> None: ...

    def ui_combo_input(self, controller: Controller, ui_type: str, mapped_key: str, /) -> tuple[str, bool]:
        return mapped_key, False

    def ui_select_key(self) -> str:
        return 'b'


def _resolve_pad_key(
    source: PadConfigHost,
    controller: Controller,
    key: str,
    /,
    *,
    allow_unbound: bool = False,
) -> tuple[str, bool] | None:
    if key in controller.inputs:
        return key, False

    if allow_unbound and source.should_emit_unbound_pad_mapping():
        return key, False

    reversed_key = reverse_mapping(key)

    if reversed_key is not None and source.can_reverse_pad_mapping(controller, reversed_key):
        return key, True

    return None


def _add_mess_controls(
    source: PadConfigHost,
    control_config: ControlConfig,
    config_alt: ControlConfig,
    controller: Controller,
    player_number: int,
    mappings_use: dict[str, str],
    mess_controls: dict[str, MessControlMapping],
    /,
) -> None:
    joycode = controller.index + 1
    for mess_control in mess_controls.values():
        if player_number != mess_control.player:
            continue

        if isinstance(mess_control, MessAnalogMapping):
            inc_key = mappings_use.get(mess_control.incMapping)
            dec_key = mappings_use.get(mess_control.decMapping)
            inc_use = mappings_use.get(mess_control.incUseMapping)
            dec_use = mappings_use.get(mess_control.decUseMapping)
            if inc_key is None or dec_key is None or inc_use is None or dec_use is None:
                continue

            inc_resolved = _resolve_pad_key(source, controller, inc_use, allow_unbound=True)
            dec_resolved = _resolve_pad_key(source, controller, dec_use, allow_unbound=True)
            if inc_resolved is None or dec_resolved is None:
                continue

            _, inc_reversed = inc_resolved
            _, dec_reversed = dec_resolved
            config_alt.add_sequence_port(
                mess_control.key,
                tag=mess_control.tag,
                mask=str(mess_control.mask),
                defvalue=str(mess_control.default),
                key_delta=str(mess_control.delta),
                sequences=[
                    (
                        'increment',
                        source.generate_pad_sequence(
                            controller,
                            inc_key,
                            reversed=inc_reversed,
                            ignore_axis=True,
                            input_key=inc_use,
                        ),
                    ),
                    (
                        'decrement',
                        source.generate_pad_sequence(
                            controller,
                            dec_key,
                            reversed=dec_reversed,
                            ignore_axis=True,
                            input_key=dec_use,
                        ),
                    ),
                    ('standard', 'NONE' if not mess_control.axis else f'JOYCODE_{joycode}_{mess_control.axis}'),
                ],
            )
            continue

        mapped_key = mappings_use.get(mess_control.useMapping)
        if mapped_key is None:
            continue

        resolved = _resolve_pad_key(source, controller, mapped_key, allow_unbound=True)
        if resolved is None:
            continue

        _, reversed_flag = resolved
        sequence = source.generate_pad_sequence(
            controller,
            mess_control.mapping,
            reversed=reversed_flag,
            input_key=mapped_key,
        )
        target = control_config if isinstance(mess_control, MessMainMapping) else config_alt

        if isinstance(mess_control, MessComboMapping):
            sequence = f'KEYCODE_{mess_control.kbMapping} OR {sequence}'

        target.add_sequence_port(
            mess_control.key,
            sequence=sequence,
            tag=mess_control.tag,
            mask=str(mess_control.mask),
            defvalue=str(mess_control.default),
        )


def write_pad_config(
    source: PadConfigHost,
    cfg_path: Path,
    mess_system_name: str,
    special_controller: str,
    /,
) -> None:
    config_file = cfg_path / 'default.cfg'
    custom_cfg = source.config.get_bool('customcfg')
    overwrite_mame = not (config_file.exists() and custom_cfg)

    control_config = ControlConfig.load(config_file) if config_file.exists() else ControlConfig()
    source.prepare_control_config(control_config)

    alt_buttons = source.mame_control_scheme
    mappings = load_mame_control_mapping(alt_buttons)
    use_controls = _mess_use_controls(mess_system_name, special_controller)
    _logger.debug('Using %s for controller config.', use_controls)

    mess_controls = load_mess_system_controls(mess_system_name, use_controls)
    config_alt: ControlConfig | None = None
    config_alt_file: Path | None = None
    overwrite_system = True

    if mess_controls is not None:
        config_alt_file = cfg_path / f'{mess_system_name}.cfg'
        overwrite_system = source.should_overwrite_system_cfg(cfg_path, mess_system_name, config_alt_file.exists())

        if config_alt_file.exists():
            config_alt = ControlConfig.load(config_alt_file, system_name=mess_system_name)
        else:
            config_alt = ControlConfig(system_name=mess_system_name)

        if use_controls == 'cdimono1':
            config_alt.remove_system_elements('video')
            video_alt = config_alt.add_system_element('video')
            config_alt.create_child_element(video_alt, 'target', index='0', view=source.cdi_screen_view())

        if use_controls == 'bbc':
            config_alt.add_input_element('keyboard', tag=':', enabled='1')

    if source.should_configure_pads():
        for nplayer, controller in enumerate(source.controllers, start=1):
            mappings_use = mappings.copy()
            if not has_stick(controller):
                mappings_use['JOYSTICK_UP'] = 'up'
                mappings_use['JOYSTICK_DOWN'] = 'down'
                mappings_use['JOYSTICK_LEFT'] = 'left'
                mappings_use['JOYSTICK_RIGHT'] = 'right'

            mappings_use = source.adjust_control_mappings(controller, mappings_use)
            source.prepare_player_config(control_config, nplayer)

            for mapping, mapped_key in mappings_use.items():
                resolved = _resolve_pad_key(source, controller, mapped_key)
                if resolved is None:
                    continue

                _, reversed_flag = resolved
                sequence = source.generate_pad_sequence(
                    controller,
                    mapped_key,
                    reversed=reversed_flag,
                    mapping=mapping,
                    player_number=nplayer,
                )
                if mapping in {'START', 'COIN'}:
                    control_config.add_sequence_port(
                        f'{mapping}{nplayer}',
                        sequence=sequence,
                        tag='standard',
                        mask='',
                        defvalue='',
                    )
                    extra_type = source.extra_start_coin_port_type(mapping, nplayer)
                    if extra_type is not None:
                        control_config.add_sequence_port(
                            extra_type,
                            sequence=sequence,
                            tag='standard',
                            mask='',
                            defvalue='',
                        )
                else:
                    control_config.add_sequence_port(f'P{nplayer}_{mapping}', sequence=sequence)

            if nplayer == 1:
                for ui_type, kb_key, mapping_name in _UI_PORTS:
                    mapped_key = mappings_use[mapping_name]
                    combo_key, combo_reversed = source.ui_combo_input(controller, ui_type, mapped_key)
                    control_config.add_sequence_port(
                        ui_type,
                        sequence=(
                            f'KEYCODE_{kb_key} OR '
                            f'{source.generate_pad_sequence(controller, combo_key, reversed=combo_reversed)}'
                        ),
                        tag='standard',
                        mask='',
                        defvalue='',
                    )
                control_config.add_sequence_port(
                    'UI_SELECT',
                    sequence=(f'KEYCODE_ENTER OR {source.generate_pad_sequence(controller, source.ui_select_key())}'),
                    tag='standard',
                    mask='',
                    defvalue='',
                )

            if mess_controls is not None and config_alt is not None:
                _add_mess_controls(source, control_config, config_alt, controller, nplayer, mappings_use, mess_controls)

        source.finish_control_config(control_config)

    if overwrite_mame:
        _logger.debug('Saving %s', config_file)
        control_config.save(config_file)

    if mess_controls is not None and overwrite_system and config_alt is not None and config_alt_file is not None:
        _logger.debug('Saving %s', config_alt_file)
        config_alt.save(config_alt_file)
