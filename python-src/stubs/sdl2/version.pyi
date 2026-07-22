from ctypes import Structure, _Pointer

__all__ = [
    'SDL_COMPILEDVERSION',
    'SDL_MAJOR_VERSION',
    'SDL_MINOR_VERSION',
    'SDL_PATCHLEVEL',
    'SDL_VERSION',
    'SDL_VERSIONNUM',
    'SDL_VERSION_ATLEAST',
    'SDL_GetRevision',
    'SDL_GetRevisionNumber',
    'SDL_GetVersion',
    'SDL_version',
]

SDL_MAJOR_VERSION: int
SDL_MINOR_VERSION: int
SDL_PATCHLEVEL: int

def SDL_VERSION(x: SDL_version) -> None: ...
def SDL_VERSIONNUM(x: int, y: int, z: int) -> int: ...

SDL_COMPILEDVERSION: int

def SDL_VERSION_ATLEAST(X: int, Y: int, Z: int) -> bool: ...

class SDL_version(Structure):
    major: int
    minor: int
    patch: int

def SDL_GetVersion(ver: _Pointer[SDL_version], /) -> None: ...
def SDL_GetRevision() -> bytes | None: ...
def SDL_GetRevisionNumber() -> int: ...
