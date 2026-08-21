from ctypes import c_int, c_int8, c_int16, c_int32, c_int64, c_uint8, c_uint16, c_uint32, c_uint64

__all__ = [
    'SDL_FALSE',
    'SDL_FLT_EPSILON',
    'SDL_TRUE',
    'SDL_abs',
    'SDL_bool',
    'SDL_calloc',
    'SDL_clamp',
    'SDL_free',
    'SDL_getenv',
    'SDL_malloc',
    'SDL_max',
    'SDL_memcpy',
    'SDL_memset',
    'SDL_min',
    'SDL_realloc',
    'SDL_setenv',
    'Sint8',
    'Sint16',
    'Sint32',
    'Sint64',
    'Uint8',
    'Uint16',
    'Uint32',
    'Uint64',
]

SDL_FLT_EPSILON: float
SDL_bool = c_int
SDL_FALSE: int
SDL_TRUE: int
Sint8 = c_int8
Uint8 = c_uint8
Sint16 = c_int16
Uint16 = c_uint16
Sint32 = c_int32
Uint32 = c_uint32
Sint64 = c_int64
Uint64 = c_uint64
SDL_min = min
SDL_max = max

def SDL_clamp(x: int, a: int, b: int) -> int: ...
def SDL_malloc(size: int, /) -> int | None: ...
def SDL_calloc(nmemb: int, size: int, /) -> int | None: ...
def SDL_realloc(mem: int | None, size: int, /) -> int | None: ...
def SDL_free(mem: int | None, /) -> None: ...
def SDL_getenv(name: bytes | None, /) -> bytes | None: ...
def SDL_setenv(name: bytes | None, value: bytes | None, overwrite: int, /) -> int: ...
def SDL_abs(x: int, /) -> int: ...
def SDL_memset(dst: int | None, c: int, len: int, /) -> int | None: ...
def SDL_memcpy(dst: int | None, src: int | None, len: int, /) -> int | None: ...
