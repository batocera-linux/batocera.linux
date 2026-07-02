from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Self

from batocera_launch.command import Command
from batocera_launch.emulator import Emulator
from batocera_launch.functools import cached_property
from configgen.config import Config as _ConfiggenConfig, SystemConfig as _ConfiggenSystemConfig
from configgen.Emulator import Emulator as _ConfiggenEmulator
from configgen.generators.importer import get_generator

if TYPE_CHECKING:
    from argparse import Namespace
    from pathlib import Path

    from batocera_launch.config.config import SystemConfig
    from batocera_launch.devices.controller import Controllers
    from batocera_launch.devices.device import DeviceInfo, DeviceInfoMapping
    from batocera_launch.devices.gun import Guns
    from batocera_launch.types import HotkeysContext, Resolution
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


@dataclass(slots=True)
class Configgen(Emulator):
    generator: Generator
    configgen_emulator: ConfiggenEmulator

    @property
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
    def needs_bezels(self) -> bool:
        return not self.generator.supportsInternalBezels()

    @cached_property
    def guns_borders_size(self) -> str | None:
        return self.configgen_emulator.guns_borders_size_name(self.guns)

    def configure(self, prepared_rom: Path, /) -> Command:
        configgen_command = self.generator.generate(
            self.configgen_emulator,
            prepared_rom,
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
    def create(
        cls,
        args: Namespace,
        system_config: SystemConfig,
        metadata: dict[str, str],
        controllers: Controllers,
        guns: Guns,
        wheels: DeviceInfoMapping,
        resolution: Resolution,
        /,
    ) -> Self:
        generator = get_generator(system_config.emulator, system_config.core)
        emulator = ConfiggenEmulator(args, args.rom, system_config)

        return cls(
            args.system,
            args.systemname,
            system_config,
            metadata,
            controllers,
            guns,
            wheels,
            resolution,
            generator,
            emulator,
        )
