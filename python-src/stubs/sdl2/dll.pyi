from collections.abc import Callable
from ctypes import Structure
from typing import Any

__all__ = ['DLL', 'nullfunc']

def nullfunc(*args: Any) -> None: ...

class SDL_version(Structure):
    major: int
    minor: int
    patch: int

class SDLFunc:
    name: str
    args: list[Any] | None
    returns: Any | None
    added: str | None
    def __init__(
        self,
        name: str,
        args: list[Any] | None = None,
        returns: Any | None = None,
        added: str | None = None,
    ) -> None: ...

class DLLWarning(Warning): ...

class DLL:
    def __init__(
        self,
        libinfo: str,
        libnames: list[str],
        path: str | None = None,
    ) -> None: ...
    def bind_function(
        self,
        funcname: str,
        args: list[Any] | None = None,
        returns: Any | None = None,
        added: str | None = None,
    ) -> Callable[..., Any]: ...
    @property
    def libfile(self) -> str: ...
    @property
    def version_tuple(self) -> tuple[int, int, int]: ...
    @property
    def version(self) -> int: ...

def get_dll_file() -> str: ...
