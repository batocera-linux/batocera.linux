from __future__ import annotations

import ctypes
import ctypes.util
import os
from dataclasses import InitVar, dataclass
from enum import IntFlag
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final, Never, NewType

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

# A small ctypes wrapper for SDL3, providing access to some of its functions and constants.
# pysdl3 is poorly typed and a very thin wrapper over ctypes. This module provides a more
# Pythonic interface to SDL3, with proper type hints and enums.

_sdl3 = ctypes.CDLL(ctypes.util.find_library('SDL3') or 'libSDL3.so')


@dataclass(slots=True, frozen=True)
class _function[**P, R]:
    func: ctypes._NamedFuncPointer

    argtypes: InitVar[Sequence[type[ctypes._CDataType]]]
    restype: InitVar[type[ctypes._CDataType] | Callable[[int], Any] | None]

    def __post_init__(
        self,
        argtypes: Sequence[type[ctypes._CDataType]],
        restype: type[ctypes._CDataType] | Callable[[int], Any] | None,
    ) -> None:
        self.func.argtypes = argtypes
        self.func.restype = restype

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.func(*args, **kwargs)


_SDL_InitFlags: Final = ctypes.c_uint32
_SDL_JoystickID: Final = ctypes.c_uint32


class _SDL_GUID(ctypes.Structure):
    _fields_ = [
        ('data', ctypes.c_uint8 * 16),
    ]


_SDL_free: Final = _function[[Any], None](_sdl3.SDL_free, argtypes=[ctypes.c_void_p], restype=None)
_SDL_GetError: Final = _function[[], bytes | None](_sdl3.SDL_GetError, argtypes=[], restype=ctypes.c_char_p)
_SDL_ClearError: Final = _function[[], bool](_sdl3.SDL_ClearError, argtypes=[], restype=ctypes.c_bool)
_SDL_Init: Final = _function[[int], bool](_sdl3.SDL_Init, argtypes=[_SDL_InitFlags], restype=ctypes.c_bool)
_SDL_WasInit: Final = _function[[int], int](_sdl3.SDL_WasInit, argtypes=[_SDL_InitFlags], restype=_SDL_InitFlags)
_SDL_QuitSubSystem: Final = _function[[int], None](_sdl3.SDL_QuitSubSystem, argtypes=[_SDL_InitFlags], restype=None)
_SDL_Quit: Final = _function[[], None](_sdl3.SDL_Quit, argtypes=[], restype=None)
_SDL_UpdateJoysticks: Final = _function[[], None](_sdl3.SDL_UpdateJoysticks, argtypes=[], restype=None)
_SDL_GetJoysticks: Final = _function[
    ['ctypes._CArgObject'],  # pyright: ignore[reportGeneralTypeIssues]
    'ctypes._Pointer[_SDL_JoystickID]',
](
    _sdl3.SDL_GetJoysticks,
    argtypes=[ctypes.POINTER(ctypes.c_int)],
    restype=ctypes.POINTER(_SDL_JoystickID),
)
_SDL_GUIDToString: Final = _function[[_SDL_GUID, ctypes.Array[ctypes.c_char], int], None](
    _sdl3.SDL_GUIDToString, argtypes=[_SDL_GUID, ctypes.c_char_p, ctypes.c_int], restype=None
)
_SDL_GetJoystickGUIDForID: Final = _function[[int], _SDL_GUID](
    _sdl3.SDL_GetJoystickGUIDForID, argtypes=[_SDL_JoystickID], restype=_SDL_GUID
)
_SDL_GetJoystickPathForID: Final = _function[[int], bytes | None](
    _sdl3.SDL_GetJoystickPathForID, argtypes=[_SDL_JoystickID], restype=ctypes.c_char_p
)


class SDLError(Exception):
    """Exception raised for SDL errors."""

    def __init__(self, message: bytes):
        super().__init__(message.decode('utf-8'))


def _raise_sdl_error() -> Never:
    error = _SDL_GetError() or b'Unknown SDL error'
    _SDL_ClearError()
    raise SDLError(error)


class InitFlags(IntFlag):
    NONE = 0
    AUDIO = 0x00000010
    VIDEO = 0x00000020
    JOYSTICK = 0x00000200
    HAPTIC = 0x00001000
    GAMEPAD = 0x00002000
    EVENTS = 0x00004000
    SENSOR = 0x00008000
    CAMERA = 0x00010000


JoystickID = NewType('JoystickID', int)


def was_init(flags: InitFlags, /) -> InitFlags:
    result = _SDL_WasInit(int(flags))
    return InitFlags(result)


def init(flags: InitFlags, /) -> None:
    if not _SDL_Init(int(flags)):
        _raise_sdl_error()


def quit_subsystem(flags: InitFlags, /) -> None:
    _SDL_QuitSubSystem(int(flags))


def quit() -> None:
    _SDL_Quit()


def update_joysticks() -> None:
    _SDL_UpdateJoysticks()


def get_joystick_ids() -> list[JoystickID]:
    count = ctypes.c_int()
    joysticks_ptr = _SDL_GetJoysticks(ctypes.byref(count))

    if not joysticks_ptr:
        _raise_sdl_error()

    try:
        return [JoystickID(joystick_id) for joystick_id in joysticks_ptr[: count.value]]
    finally:
        _SDL_free(joysticks_ptr)


def get_joystick_guid(joystick_id: JoystickID, /) -> str:
    guid_struct = _SDL_GetJoystickGUIDForID(int(joystick_id))
    buffer = (ctypes.c_char * 33)()  # 32 characters + null terminator
    _SDL_GUIDToString(guid_struct, buffer, 33)

    return buffer.value.decode('ascii')


def get_joystick_path(joystick_id: JoystickID, /) -> Path:
    path_ptr = _SDL_GetJoystickPathForID(int(joystick_id))

    if path_ptr is None:
        _raise_sdl_error()

    return Path(os.fsdecode(path_ptr))
