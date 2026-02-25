from __future__ import annotations

from batocera_common.asyncio import run
from batocera_launch import Command, Emulator, HotkeysContext, cached_dataclass, cached_property


@cached_dataclass
class Flatpak(Emulator):
    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'flatpak',
            'keys': {'exit': 'flatpak kill $(flatpak ps --columns=application | head -n 1)'},
        }

    @property
    def needs_mouse(self) -> bool:
        return True

    async def configure(self) -> Command:
        rom_id = self.rom.read_text().strip()

        # bad hack in a first time to get audio for user batocera
        await run('chown', '-R', 'root:audio', '/var/run/pulse', check=False)
        await run('chmod', '-R', 'g+rwX', '/var/run/pulse', check=False)

        return Command(
            ['/usr/bin/flatpak', 'run', '-v', rom_id],
            env={'SDL_JOYSTICK_HIDAPI_XBOX': '0'},
        )
