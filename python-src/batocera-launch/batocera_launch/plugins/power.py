from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.power import apply_power_mode, is_power_connected

from . import Plugin

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ..config.config import SystemConfig
    from . import HookContext


def global_power_mode(global_settings: Mapping[str, str], /) -> str | None:
    return global_settings.get('powermode' if is_power_connected() else 'batterymode')


def resolve_power_mode(config: SystemConfig, /) -> str | None:
    return config.system_settings.get('powermode') or global_power_mode(config.global_settings)


class PowerModePlugin(Plugin):
    def start(self, context: HookContext, /) -> None:
        apply_power_mode(resolve_power_mode(context.config), user_config=context.config.user_config)

    def stop(self, context: HookContext, /) -> None:
        apply_power_mode(global_power_mode(context.config.global_settings), user_config=context.config.user_config)
