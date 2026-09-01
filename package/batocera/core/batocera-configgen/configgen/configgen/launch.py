from __future__ import annotations

from collections import ChainMap
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self, cast

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import (
    Command,
    Emulator,
    HotkeysContext,
    SystemConfig,
)

from .config import Config, SystemConfig as _SystemConfig
from .Emulator import Emulator as _System
from .generators.importer import get_generator

if TYPE_CHECKING:
    from collections.abc import Mapping

    from batocera_launch.cli.arguments import Arguments
    from batocera_launch.devices.device import DeviceInfo

    from .generators.Generator import Generator
    from .gun import Guns
    from .types import DeviceInfo as _DeviceInfo

def _convert_device_info(device_info: DeviceInfo, /) -> _DeviceInfo:
    result: _DeviceInfo = {
        'eventId': device_info.event_id,
        'sysfs_path': device_info.sysfs_path,
        'isJoystick': device_info.is_joystick,
        'isWheel': device_info.is_wheel,
        'isMouse': device_info.is_mouse,
        'associatedDevices': device_info.associated_devices,
        'joystick_index': device_info.joystick_index,
        'mouse_index': device_info.mouse_index,
    }

    if device_info.wheel_rotation is not None:
        result['wheel_rotation'] = device_info.wheel_rotation

    return result

@dataclass
class GeneratorSystemConfig(_SystemConfig):
    @classmethod
    def from_launch(cls, config: SystemConfig, /) -> Self:
        overlay: dict[str, Any] = {
            'emulator': config.emulator,
            'emulator-forced': config.emulator_forced,
            'core': config.core,
            'core-forced': config.core_forced,
            'uimode': config.ui_mode,
            'showFPS': config.show_fps,
            'use_guns': config.use_guns,
            'use_wheels': config.use_wheels,
        }

        if config.netplay_mode is not None:
            overlay['netplay.mode'] = config.netplay_mode

        if config.netplay_password is not None:
            overlay['netplay.password'] = config.netplay_password

        if config.netplay_server_ip is not None:
            overlay['netplay.server.ip'] = config.netplay_server_ip

        if config.netplay_server_port is not None:
            overlay['netplay.server.port'] = config.netplay_server_port

        if config.netplay_server_session is not None:
            overlay['netplay.server.session'] = config.netplay_server_session

        if config.state_slot is not None:
            overlay['state_slot'] = config.state_slot

        if config.autosave is not None:
            overlay['autosave'] = config.autosave

        if config.state_filename is not None:
            overlay['state_filename'] = config.state_filename

        return cls(cast('dict[str, Any]', ChainMap(overlay, config.data)), config.cli_args.system)

@dataclass(slots=True)
class GeneratorSystem(_System):
    launch_emulator: Emulator

    @property
    def es_game_info(self) -> Mapping[str, str]:
        return self.launch_emulator.game_info

    def __post_init__(self, args: Arguments, rom: Path, /) -> None:
        self.name = self.launch_emulator.config.cli_args.system
        self.game_info_xml = str(self.launch_emulator.config.cli_args.gameinfoxml)
        self.config = GeneratorSystemConfig.from_launch(self.launch_emulator.config)
        self.renderconfig = Config(dict(self.launch_emulator.config.render_config.data))

    def guns_borders_size_name(self, guns: Guns) -> str | None:
        return self.launch_emulator.guns_borders_size

    def guns_border_ratio_type(self, guns: Guns) -> str | None:
        return self.launch_emulator.guns_border_ratio

@cached_dataclass
class GeneratorEmulator(Emulator):
    # These are set in __aenter__
    generator: Generator = field(init=False)
    configgen_system: GeneratorSystem = field(init=False)

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return self.generator.getHotkeysContext()

    @property
    def execution_path(self) -> Path | None:
        return self.generator.executionDirectory(self.configgen_system.config, self.rom)

    @property
    def target_video_mode(self) -> str:
        return self.generator.getResolutionMode(self.configgen_system.config) or 'default'

    @property
    def needs_mouse(self) -> bool:
        return self.generator.getMouseMode(self.configgen_system.config, self.rom)

    @property
    def handles_bezels(self) -> bool:
        return self.generator.supportsInternalBezels()

    @property
    def handles_hud(self) -> bool:
        return self.generator.hasInternalMangoHUDCall()

    @property
    def needs_overlayfs(self) -> bool:
        return self.generator.writesToRom(self.configgen_system.config)

    @cached_property
    def in_game_ratio(self) -> float:
        return self.generator.getInGameRatio(
            self.configgen_system.config,
            {
                'width': self.resolution.width,
                'height': self.resolution.height,
            },
            self.rom,
        )

    async def __aenter__(self) -> Self:
        self.generator = get_generator(self.config.emulator, self.config.core)
        self.configgen_system = GeneratorSystem(self.config.cli_args, self.config.cli_args.rom, self)

        return await super().__aenter__()

    async def configure(self) -> Command:
        command = self.generator.generate(
            self.configgen_system,
            Path(self.rom),
            self.controllers,
            self.metadata,
            self.guns,
            {key: _convert_device_info(wheel) for key, wheel in self.wheels.items()},
            asdict(self.resolution),  # pyright: ignore
        )

        return Command(
            command.array,
            command.env,
        )
