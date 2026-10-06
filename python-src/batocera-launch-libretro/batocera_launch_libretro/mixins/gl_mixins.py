from __future__ import annotations

from batocera_common.dataclasses import cached_dataclass

from ..core import Core


@cached_dataclass
class GLCoreOverrideMixin(Core):
    def override_default_gfx_backend(self, default_gfx_backend: str, /) -> str | None:
        if default_gfx_backend == 'gl':
            return 'glcore'

        return super().override_default_gfx_backend(default_gfx_backend)


@cached_dataclass
class GLOverrideMixin(Core):
    def override_default_gfx_backend(self, default_gfx_backend: str, /) -> str | None:
        if default_gfx_backend == 'glcore':
            return 'gl'

        return super().override_default_gfx_backend(default_gfx_backend)


@cached_dataclass
class GLCoreForceMixin(Core):
    def force_gfx_backend(self, default_gfx_backend: str, /) -> str | None:
        if default_gfx_backend == 'gl':
            return 'glcore'

        return super().force_gfx_backend(default_gfx_backend)


@cached_dataclass
class GLForceMixin(Core):
    def force_gfx_backend(self, default_gfx_backend: str, /) -> str | None:
        if default_gfx_backend == 'glcore':
            return 'gl'

        return super().force_gfx_backend(default_gfx_backend)
