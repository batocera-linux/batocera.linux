from __future__ import annotations

import tomllib
from dataclasses import dataclass
from importlib import resources
from typing import Self


@dataclass(slots=True)
class MessSystemInfo:
    name: str
    rom_type: str
    auto_run: str | None

    @classmethod
    def load(cls, system_name: str, /) -> Self | None:
        mess_systems = tomllib.loads(resources.files().joinpath('data', 'mess_systems.toml').read_text())
        mess_system = mess_systems.get(system_name, None)

        # This must be an `is not None` check because the dictionary could be empty
        if mess_system is not None:
            return cls(
                mess_system.get('name', system_name),
                mess_system.get('rom_type', ''),
                mess_system.get('auto_run'),
            )

        return None
