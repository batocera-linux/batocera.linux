from ctypes import _Pointer, c_char, c_int

__all__ = [
    'SDL_EFREAD',
    'SDL_EFSEEK',
    'SDL_EFWRITE',
    'SDL_ENOMEM',
    'SDL_LASTERROR',
    'SDL_UNSUPPORTED',
    'SDL_ClearError',
    'SDL_Error',
    'SDL_GetError',
    'SDL_GetErrorMsg',
    'SDL_InvalidParamError',
    'SDL_OutOfMemory',
    'SDL_SetError',
    'SDL_Unsupported',
    'SDL_errorcode',
]

SDL_errorcode = c_int
SDL_ENOMEM: int
SDL_EFREAD: int
SDL_EFWRITE: int
SDL_EFSEEK: int
SDL_UNSUPPORTED: int
SDL_LASTERROR: int

def SDL_SetError(fmt: bytes | None, /) -> int: ...
def SDL_GetError() -> bytes | None: ...
def SDL_GetErrorMsg(errstr: _Pointer[c_char], maxlen: int, /) -> bytes | None: ...
def SDL_ClearError() -> None: ...
def SDL_Error(code: int, /) -> int: ...

SDL_OutOfMemory: int
SDL_Unsupported: int

def SDL_InvalidParamError(x: str | bytes) -> int: ...
