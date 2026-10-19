# This file is part of The Batocera Linux Distribution (https://batocera.org).
# Copyright (c) 2026 The Batocera Team.
#
# The Batocera Linux Distribution is free software: you can redistribute it
# and/or modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# The Batocera Linux Distribution is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with The Batocera Linux Distribution. If not, see
# <https://www.gnu.org/licenses/>.
#
# YOU MUST RETAIN THE LICENSE AND COPYRIGHT NOTICES ABOVE IN ANY
# REDISTRIBUTED VERSION OF THIS FILE.

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
