from __future__ import annotations

from typing import TYPE_CHECKING

from batocera_common.dataclasses import cached_dataclass

from ..core import Core

if TYPE_CHECKING:
    from batocera_launch import Controller


@cached_dataclass
class AssociatedMouseMixin(Core):
    def get_mouse_index(self, controller: Controller, /) -> str:
        from batocera_launch import get_associated_mouse, get_device_info

        associated_mouse = get_associated_mouse(get_device_info(), controller.device_path)

        if associated_mouse is not None:
            return associated_mouse

        return super().get_mouse_index(controller)
