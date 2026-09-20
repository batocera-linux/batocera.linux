from __future__ import annotations

import lazy_loader

# All exports are lazy loaded to improve startup time. Exports are defined
# in the sibling `__init__.pyi` file, which not only helps type checking
# and IDE autocompletion, but also is parsed by lazy_loader to define
# the exported attributes of this module.

# DO NOT add imports to this module. Update the `__init__.pyi` file instead.
__getattr__, __dir__, __all__ = lazy_loader.attach_stub(__name__, __file__)
