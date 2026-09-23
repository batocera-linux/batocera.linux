from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.power import apply_power_mode, is_power_connected

from . import Hook

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..config.config import SystemConfig


def global_power_mode(global_settings: Mapping[str, str], /) -> str | None:
    return global_settings.get('powermode' if is_power_connected() else 'batterymode')


def resolve_power_mode(config: SystemConfig, /) -> str | None:
    """A game, folder or system power mode wins; the global one depends on whether a charger is connected."""
    return config.system_settings.get('powermode') or global_power_mode(config.global_settings)


class PowerModeHook(Hook):
    def start(self, config: SystemConfig, /) -> None:
        apply_power_mode(resolve_power_mode(config), user_config=config.user_config)

    def stop(self, config: SystemConfig, /) -> None:
        apply_power_mode(global_power_mode(config.global_settings), user_config=config.user_config)
