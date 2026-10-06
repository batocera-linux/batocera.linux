from __future__ import annotations

from typing import Any

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_launch import Config, SystemConfig


@cached_dataclass(frozen=True)
class MockSystemConfig(SystemConfig):
    render_config_data: dict[str, Any]

    @cached_property
    def render_config(self) -> Config:
        return Config(self.render_config_data)
