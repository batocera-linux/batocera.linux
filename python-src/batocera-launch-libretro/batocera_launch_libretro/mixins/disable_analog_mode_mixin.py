from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from batocera_common.dataclasses import cached_dataclass

from ..core import Core

if TYPE_CHECKING:
    from batocera_launch import Controller


@cached_dataclass
class DisableAnalogModeMixin(Core):
    def get_analog_mode(self, controller: Controller, /) -> Literal['0']:
        return '0'
