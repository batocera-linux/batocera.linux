from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_launch import cached_dataclass, cached_property
from batocera_launch_libretro import Core, DisableRewindMixin, DisableRunaheadMixin, GLOverrideMixin, LibretroConfig

if TYPE_CHECKING:
    from batocera_launch import Controller


@cached_dataclass
class YabaSanshiro(GLOverrideMixin, DisableRewindMixin, DisableRunaheadMixin, Core):
    @cached_property
    def player1_device_type(self) -> str | None:
        if self.system != 'saturn':
            return None

        return self.config.get_str('controller1_saturn', '1')

    @cached_property
    def player2_device_type(self) -> str | None:
        if self.system != 'saturn':
            return None

        return self.config.get_str('controller2_saturn', '1')

    def set_button_mappings(self, controller: Controller, button_mappings: dict[str, str], /) -> None:
        # Fix for reversed inputs in Yabasanshiro core which is unmaintained by retroarch
        button_mappings['pageup'] = 'r'
        button_mappings['pagedown'] = 'l'

    def set_core_options(self, core_options: LibretroConfig, /) -> None:
        # Video Resolution
        core_options.set_from_config('yabasanshiro_resolution_mode', 'resolution_mode', default='original')

        # Multitap
        port1 = 'disabled'
        port2 = 'disabled'

        match self.config.get('multitap_yabasanshiro'):
            case 'port1':
                port1 = 'enabled'
            case 'port2':
                port2 = 'enabled'
            case 'port12':
                port1 = 'enabled'
                port2 = 'enabled'
            case _:
                pass

        core_options.set('yabasanshiro_multitap_port1', port1)
        core_options.set('yabasanshiro_multitap_port2', port2)

        # Language
        core_options.set_from_config('yabasanshiro_system_language', 'yabasanshiro_language', default='english')
