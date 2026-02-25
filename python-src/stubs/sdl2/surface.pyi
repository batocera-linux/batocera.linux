from ctypes import Structure, _CFuncPtr, _Pointer, c_int, c_void_p

from .pixels import SDL_Palette, SDL_PixelFormat
from .rect import SDL_Rect
from .rwops import SDL_RWops
from .stdinc import Uint8, Uint32

__all__ = [
    'SDL_DONTFREE',
    'SDL_MUSTLOCK',
    'SDL_PREALLOC',
    'SDL_RLEACCEL',
    'SDL_SIMD_ALIGNED',
    'SDL_SWSURFACE',
    'SDL_Blit',
    'SDL_BlitMap',
    'SDL_BlitScaled',
    'SDL_BlitSurface',
    'SDL_ConvertPixels',
    'SDL_ConvertSurface',
    'SDL_ConvertSurfaceFormat',
    'SDL_CreateRGBSurface',
    'SDL_CreateRGBSurfaceFrom',
    'SDL_CreateRGBSurfaceWithFormat',
    'SDL_CreateRGBSurfaceWithFormatFrom',
    'SDL_DuplicateSurface',
    'SDL_FillRect',
    'SDL_FillRects',
    'SDL_FreeSurface',
    'SDL_GetClipRect',
    'SDL_GetColorKey',
    'SDL_GetSurfaceAlphaMod',
    'SDL_GetSurfaceBlendMode',
    'SDL_GetSurfaceColorMod',
    'SDL_GetYUVConversionMode',
    'SDL_GetYUVConversionModeForResolution',
    'SDL_HasColorKey',
    'SDL_HasSurfaceRLE',
    'SDL_LoadBMP',
    'SDL_LoadBMP_RW',
    'SDL_LockSurface',
    'SDL_LowerBlit',
    'SDL_LowerBlitScaled',
    'SDL_PremultiplyAlpha',
    'SDL_SaveBMP',
    'SDL_SaveBMP_RW',
    'SDL_SetClipRect',
    'SDL_SetColorKey',
    'SDL_SetSurfaceAlphaMod',
    'SDL_SetSurfaceBlendMode',
    'SDL_SetSurfaceColorMod',
    'SDL_SetSurfacePalette',
    'SDL_SetSurfaceRLE',
    'SDL_SetYUVConversionMode',
    'SDL_SoftStretch',
    'SDL_SoftStretchLinear',
    'SDL_Surface',
    'SDL_UnlockSurface',
    'SDL_UpperBlit',
    'SDL_UpperBlitScaled',
    'SDL_blit',
]

SDL_SWSURFACE: int
SDL_PREALLOC: int
SDL_RLEACCEL: int
SDL_DONTFREE: int
SDL_SIMD_ALIGNED: int
SDL_YUV_CONVERSION_MODE = c_int
SDL_YUV_CONVERSION_JPEG: int
SDL_YUV_CONVERSION_BT601: int
SDL_YUV_CONVERSION_BT709: int
SDL_YUV_CONVERSION_AUTOMATIC: int

def SDL_MUSTLOCK(surf: object) -> bool: ...

class SDL_BlitMap(c_void_p): ...

class SDL_Surface(Structure):
    flags: int
    format: _Pointer[SDL_PixelFormat]
    w: int
    h: int
    pitch: int
    pixels: int | None
    userdata: int | None
    locked: int
    list_blitmap: int | None
    clip_rect: SDL_Rect
    map: _Pointer[SDL_BlitMap]
    refcount: int

SDL_blit: type[_CFuncPtr]
SDL_Blit = SDL_blit

def SDL_CreateRGBSurface(
    flags: int,
    width: int,
    height: int,
    depth: int,
    Rmask: int,
    Gmask: int,
    Bmask: int,
    Amask: int,
    /,
) -> _Pointer[SDL_Surface]: ...
def SDL_CreateRGBSurfaceFrom(
    pixels: c_void_p | int | None,
    width: int,
    height: int,
    depth: int,
    pitch: int,
    Rmask: int,
    Gmask: int,
    Bmask: int,
    Amask: int,
    /,
) -> _Pointer[SDL_Surface]: ...
def SDL_CreateRGBSurfaceWithFormat(
    flags: int, width: int, height: int, depth: int, format: int, /
) -> _Pointer[SDL_Surface]: ...
def SDL_CreateRGBSurfaceWithFormatFrom(
    pixels: c_void_p | int | None,
    width: int,
    height: int,
    depth: int,
    pitch: int,
    format: int,
    /,
) -> _Pointer[SDL_Surface]: ...
def SDL_FreeSurface(surface: _Pointer[SDL_Surface], /) -> None: ...
def SDL_SetSurfacePalette(surface: _Pointer[SDL_Surface], palette: _Pointer[SDL_Palette], /) -> int: ...
def SDL_LockSurface(surface: _Pointer[SDL_Surface], /) -> int: ...
def SDL_UnlockSurface(surface: _Pointer[SDL_Surface], /) -> None: ...
def SDL_DuplicateSurface(surface: _Pointer[SDL_Surface], /) -> _Pointer[SDL_Surface]: ...
def SDL_LoadBMP_RW(src: _Pointer[SDL_RWops], freesrc: int, /) -> _Pointer[SDL_Surface]: ...
def SDL_LoadBMP(fname: bytes | None) -> _Pointer[SDL_Surface]: ...
def SDL_SaveBMP_RW(surface: _Pointer[SDL_Surface], dst: _Pointer[SDL_RWops], freedst: int, /) -> int: ...
def SDL_SaveBMP(surface: _Pointer[SDL_Surface], fname: bytes | None) -> int: ...
def SDL_SetSurfaceRLE(surface: _Pointer[SDL_Surface], flag: int, /) -> int: ...
def SDL_HasSurfaceRLE(surface: _Pointer[SDL_Surface], /) -> int: ...
def SDL_HasColorKey(surface: _Pointer[SDL_Surface], /) -> int: ...
def SDL_SetColorKey(surface: _Pointer[SDL_Surface], flag: int, key: int, /) -> int: ...
def SDL_GetColorKey(surface: _Pointer[SDL_Surface], key: _Pointer[Uint32], /) -> int: ...
def SDL_SetSurfaceColorMod(surface: _Pointer[SDL_Surface], r: int, g: int, b: int, /) -> int: ...
def SDL_GetSurfaceColorMod(
    surface: _Pointer[SDL_Surface],
    r: _Pointer[Uint8],
    g: _Pointer[Uint8],
    b: _Pointer[Uint8],
    /,
) -> int: ...
def SDL_SetSurfaceAlphaMod(surface: _Pointer[SDL_Surface], alpha: int, /) -> int: ...
def SDL_GetSurfaceAlphaMod(surface: _Pointer[SDL_Surface], alpha: _Pointer[Uint8], /) -> int: ...
def SDL_SetSurfaceBlendMode(surface: _Pointer[SDL_Surface], blendMode: int, /) -> int: ...
def SDL_GetSurfaceBlendMode(surface: _Pointer[SDL_Surface], blendMode: _Pointer[c_int], /) -> int: ...
def SDL_SetClipRect(surface: _Pointer[SDL_Surface], rect: _Pointer[SDL_Rect], /) -> int: ...
def SDL_GetClipRect(surface: _Pointer[SDL_Surface], rect: _Pointer[SDL_Rect], /) -> None: ...
def SDL_ConvertSurface(
    src: _Pointer[SDL_Surface], fmt: _Pointer[SDL_PixelFormat], flags: int, /
) -> _Pointer[SDL_Surface]: ...
def SDL_ConvertSurfaceFormat(src: _Pointer[SDL_Surface], pixel_format: int, flags: int, /) -> _Pointer[SDL_Surface]: ...
def SDL_ConvertPixels(
    width: int,
    height: int,
    src_format: int,
    src: c_void_p | int | None,
    src_pitch: int,
    dst_format: int,
    dst: c_void_p | int | None,
    dst_pitch: int,
    /,
) -> int: ...
def SDL_PremultiplyAlpha(
    width: int,
    height: int,
    src_format: int,
    src: c_void_p | int | None,
    src_pitch: int,
    dst_format: int,
    dst: c_void_p | int | None,
    dst_pitch: int,
    /,
) -> int: ...
def SDL_FillRect(dst: _Pointer[SDL_Surface], rect: _Pointer[SDL_Rect], color: int, /) -> int: ...
def SDL_FillRects(dst: _Pointer[SDL_Surface], rects: _Pointer[SDL_Rect], count: int, color: int, /) -> int: ...
def SDL_UpperBlit(
    src: _Pointer[SDL_Surface],
    srcrect: _Pointer[SDL_Rect],
    dst: _Pointer[SDL_Surface],
    dstrect: _Pointer[SDL_Rect],
    /,
) -> int: ...

SDL_BlitSurface = SDL_UpperBlit

def SDL_LowerBlit(
    src: _Pointer[SDL_Surface],
    srcrect: _Pointer[SDL_Rect],
    dst: _Pointer[SDL_Surface],
    dstrect: _Pointer[SDL_Rect],
    /,
) -> int: ...
def SDL_SoftStretch(
    src: _Pointer[SDL_Surface],
    srcrect: _Pointer[SDL_Rect],
    dst: _Pointer[SDL_Surface],
    dstrect: _Pointer[SDL_Rect],
    /,
) -> int: ...
def SDL_SoftStretchLinear(
    src: _Pointer[SDL_Surface],
    srcrect: _Pointer[SDL_Rect],
    dst: _Pointer[SDL_Surface],
    dstrect: _Pointer[SDL_Rect],
    /,
) -> int: ...
def SDL_UpperBlitScaled(
    src: _Pointer[SDL_Surface],
    srcrect: _Pointer[SDL_Rect],
    dst: _Pointer[SDL_Surface],
    dstrect: _Pointer[SDL_Rect],
    /,
) -> int: ...

SDL_BlitScaled = SDL_UpperBlitScaled

def SDL_LowerBlitScaled(
    src: _Pointer[SDL_Surface],
    srcrect: _Pointer[SDL_Rect],
    dst: _Pointer[SDL_Surface],
    dstrect: _Pointer[SDL_Rect],
    /,
) -> int: ...
def SDL_SetYUVConversionMode(mode: int, /) -> None: ...
def SDL_GetYUVConversionMode() -> int: ...
def SDL_GetYUVConversionModeForResolution(width: int, height: int, /) -> int: ...
