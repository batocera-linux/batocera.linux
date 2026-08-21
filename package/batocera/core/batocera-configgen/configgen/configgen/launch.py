from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Self

from batocera_launch import (
    Command,
    Emulator,
    HotkeysContext,
    SystemConfig,
    cached_dataclass,
    cached_property,
)

from .config import Config as _ConfiggenConfig, SystemConfig as _ConfiggenSystemConfig
from .Emulator import Emulator as _ConfiggenEmulator
from .generators.importer import get_generator

if TYPE_CHECKING:
    from argparse import Namespace
    from collections.abc import AsyncGenerator
    from pathlib import Path

    from batocera_launch.devices.device import DeviceInfo
    from configgen.generators.Generator import Generator
    from configgen.types import DeviceInfo as _ConfiggenDeviceInfo


def _convert_device_info(device_info: DeviceInfo, /) -> _ConfiggenDeviceInfo:
    result: _ConfiggenDeviceInfo = {
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


@dataclass(slots=True)
class ConfiggenEmulator(_ConfiggenEmulator):
    system_config: SystemConfig

    def __post_init__(self, args: Namespace, rom: Path, /) -> None:
        self.name = args.system
        self.game_info_xml = str(args.gameinfoxml)
        self.config = _ConfiggenSystemConfig(dict(self.system_config.data))
        self.renderconfig = _ConfiggenConfig(dict(self.system_config.render_config.data))


@cached_dataclass
class Configgen(Emulator):
    generator: Generator
    configgen_emulator: ConfiggenEmulator

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return self.generator.getHotkeysContext()

    @property
    def execution_path(self) -> Path | None:
        return self.generator.executionDirectory(self.configgen_emulator.config, self.rom)

    @property
    def video_mode(self) -> str:
        return self.generator.getResolutionMode(self.configgen_emulator.config)

    @property
    def needs_mouse(self) -> bool:
        return self.generator.getMouseMode(self.configgen_emulator.config, self.rom)

    @property
    def handles_bezels(self) -> bool:
        return self.generator.supportsInternalBezels()

    @property
    def handles_hud(self) -> bool:
        return self.generator.hasInternalMangoHUDCall()

    @property
    def needs_overlayfs(self) -> bool:
        return self.generator.writesToRom(self.configgen_emulator.config)

    @cached_property
    def in_game_ratio(self) -> float:
        return self.generator.getInGameRatio(
            self.configgen_emulator.config,
            {
                'width': self.resolution.width,
                'height': self.resolution.height,
            },
            self.rom,
        )

    @cached_property
    def guns_borders_size(self) -> str | None:
        return self.configgen_emulator.guns_borders_size_name(self.guns)  # pyright: ignore[reportArgumentType]

    async def configure(self) -> Command:
        configgen_command = self.generator.generate(
            self.configgen_emulator,
            self.rom,
            self.controllers,  # pyright: ignore
            self.metadata,
            self.guns,  # pyright: ignore
            {key: _convert_device_info(wheel) for key, wheel in self.wheels.items()},
            asdict(self.resolution),  # pyright: ignore
        )

        return Command(
            configgen_command.array,
            configgen_command.env,
        )

    @classmethod
    @asynccontextmanager
    async def prepare_emulator(cls, args: Namespace, max_players: int, /) -> AsyncGenerator[Self]:
        system_config = SystemConfig.load(args)

        generator = get_generator(system_config.emulator, system_config.core)
        configgen_emulator = ConfiggenEmulator(args, args.rom, system_config)
        emulator = cls(
            args.system, args.systemname, system_config, args.gameinfoxml, generator, configgen_emulator
        )

        async with emulator._prepare_devices_and_data(args, max_players) as emulator:
            yield emulator
