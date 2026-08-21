from ctypes import Array, Structure, _Pointer, c_int

from .stdinc import Uint8, Uint16, Uint32

__all__ = [
    'ALL_PIXELFORMATS',
    'NAME_MAP',
    'SDL_ALPHA_OPAQUE',
    'SDL_ALPHA_TRANSPARENT',
    'SDL_ARRAYORDER_ABGR',
    'SDL_ARRAYORDER_ARGB',
    'SDL_ARRAYORDER_BGR',
    'SDL_ARRAYORDER_BGRA',
    'SDL_ARRAYORDER_NONE',
    'SDL_ARRAYORDER_RGB',
    'SDL_ARRAYORDER_RGBA',
    'SDL_BITMAPORDER_1234',
    'SDL_BITMAPORDER_4321',
    'SDL_BITMAPORDER_NONE',
    'SDL_BITSPERPIXEL',
    'SDL_BYTESPERPIXEL',
    'SDL_DEFINE_PIXELFORMAT',
    'SDL_DEFINE_PIXELFOURCC',
    'SDL_FOURCC',
    'SDL_ISPIXELFORMAT_ALPHA',
    'SDL_ISPIXELFORMAT_ARRAY',
    'SDL_ISPIXELFORMAT_FOURCC',
    'SDL_ISPIXELFORMAT_INDEXED',
    'SDL_ISPIXELFORMAT_PACKED',
    'SDL_PACKEDLAYOUT_332',
    'SDL_PACKEDLAYOUT_565',
    'SDL_PACKEDLAYOUT_1555',
    'SDL_PACKEDLAYOUT_4444',
    'SDL_PACKEDLAYOUT_5551',
    'SDL_PACKEDLAYOUT_8888',
    'SDL_PACKEDLAYOUT_1010102',
    'SDL_PACKEDLAYOUT_2101010',
    'SDL_PACKEDLAYOUT_NONE',
    'SDL_PACKEDORDER_ABGR',
    'SDL_PACKEDORDER_ARGB',
    'SDL_PACKEDORDER_BGRA',
    'SDL_PACKEDORDER_BGRX',
    'SDL_PACKEDORDER_NONE',
    'SDL_PACKEDORDER_RGBA',
    'SDL_PACKEDORDER_RGBX',
    'SDL_PACKEDORDER_XBGR',
    'SDL_PACKEDORDER_XRGB',
    'SDL_PIXELFLAG',
    'SDL_PIXELFORMAT_ABGR32',
    'SDL_PIXELFORMAT_ABGR1555',
    'SDL_PIXELFORMAT_ABGR4444',
    'SDL_PIXELFORMAT_ABGR8888',
    'SDL_PIXELFORMAT_ARGB32',
    'SDL_PIXELFORMAT_ARGB1555',
    'SDL_PIXELFORMAT_ARGB4444',
    'SDL_PIXELFORMAT_ARGB8888',
    'SDL_PIXELFORMAT_ARGB2101010',
    'SDL_PIXELFORMAT_BGR24',
    'SDL_PIXELFORMAT_BGR444',
    'SDL_PIXELFORMAT_BGR555',
    'SDL_PIXELFORMAT_BGR565',
    'SDL_PIXELFORMAT_BGR888',
    'SDL_PIXELFORMAT_BGRA32',
    'SDL_PIXELFORMAT_BGRA4444',
    'SDL_PIXELFORMAT_BGRA5551',
    'SDL_PIXELFORMAT_BGRA8888',
    'SDL_PIXELFORMAT_BGRX32',
    'SDL_PIXELFORMAT_BGRX8888',
    'SDL_PIXELFORMAT_EXTERNAL_OES',
    'SDL_PIXELFORMAT_INDEX1LSB',
    'SDL_PIXELFORMAT_INDEX1MSB',
    'SDL_PIXELFORMAT_INDEX2LSB',
    'SDL_PIXELFORMAT_INDEX2MSB',
    'SDL_PIXELFORMAT_INDEX4LSB',
    'SDL_PIXELFORMAT_INDEX4MSB',
    'SDL_PIXELFORMAT_INDEX8',
    'SDL_PIXELFORMAT_IYUV',
    'SDL_PIXELFORMAT_NV12',
    'SDL_PIXELFORMAT_NV21',
    'SDL_PIXELFORMAT_RGB24',
    'SDL_PIXELFORMAT_RGB332',
    'SDL_PIXELFORMAT_RGB444',
    'SDL_PIXELFORMAT_RGB555',
    'SDL_PIXELFORMAT_RGB565',
    'SDL_PIXELFORMAT_RGB888',
    'SDL_PIXELFORMAT_RGBA32',
    'SDL_PIXELFORMAT_RGBA4444',
    'SDL_PIXELFORMAT_RGBA5551',
    'SDL_PIXELFORMAT_RGBA8888',
    'SDL_PIXELFORMAT_RGBX32',
    'SDL_PIXELFORMAT_RGBX8888',
    'SDL_PIXELFORMAT_UNKNOWN',
    'SDL_PIXELFORMAT_UYVY',
    'SDL_PIXELFORMAT_XBGR32',
    'SDL_PIXELFORMAT_XBGR1555',
    'SDL_PIXELFORMAT_XBGR4444',
    'SDL_PIXELFORMAT_XBGR8888',
    'SDL_PIXELFORMAT_XRGB32',
    'SDL_PIXELFORMAT_XRGB1555',
    'SDL_PIXELFORMAT_XRGB4444',
    'SDL_PIXELFORMAT_XRGB8888',
    'SDL_PIXELFORMAT_YUY2',
    'SDL_PIXELFORMAT_YV12',
    'SDL_PIXELFORMAT_YVYU',
    'SDL_PIXELLAYOUT',
    'SDL_PIXELORDER',
    'SDL_PIXELTYPE',
    'SDL_PIXELTYPE_ARRAYF16',
    'SDL_PIXELTYPE_ARRAYF32',
    'SDL_PIXELTYPE_ARRAYU8',
    'SDL_PIXELTYPE_ARRAYU16',
    'SDL_PIXELTYPE_ARRAYU32',
    'SDL_PIXELTYPE_INDEX1',
    'SDL_PIXELTYPE_INDEX2',
    'SDL_PIXELTYPE_INDEX4',
    'SDL_PIXELTYPE_INDEX8',
    'SDL_PIXELTYPE_PACKED8',
    'SDL_PIXELTYPE_PACKED16',
    'SDL_PIXELTYPE_PACKED32',
    'SDL_PIXELTYPE_UNKNOWN',
    'SDL_AllocFormat',
    'SDL_AllocPalette',
    'SDL_ArrayOrder',
    'SDL_BitmapOrder',
    'SDL_CalculateGammaRamp',
    'SDL_Color',
    'SDL_Colour',
    'SDL_FreeFormat',
    'SDL_FreePalette',
    'SDL_GetPixelFormatName',
    'SDL_GetRGB',
    'SDL_GetRGBA',
    'SDL_MapRGB',
    'SDL_MapRGBA',
    'SDL_MasksToPixelFormatEnum',
    'SDL_PackedLayout',
    'SDL_PackedOrder',
    'SDL_Palette',
    'SDL_PixelFormat',
    'SDL_PixelFormatEnum',
    'SDL_PixelFormatEnumToMasks',
    'SDL_PixelType',
    'SDL_SetPaletteColors',
    'SDL_SetPixelFormatPalette',
]

SDL_ALPHA_OPAQUE: int
SDL_ALPHA_TRANSPARENT: int
SDL_PixelType = c_int
SDL_PIXELTYPE_UNKNOWN: int
SDL_PIXELTYPE_INDEX1: int
SDL_PIXELTYPE_INDEX4: int
SDL_PIXELTYPE_INDEX8: int
SDL_PIXELTYPE_PACKED8: int
SDL_PIXELTYPE_PACKED16: int
SDL_PIXELTYPE_PACKED32: int
SDL_PIXELTYPE_ARRAYU8: int
SDL_PIXELTYPE_ARRAYU16: int
SDL_PIXELTYPE_ARRAYU32: int
SDL_PIXELTYPE_ARRAYF16: int
SDL_PIXELTYPE_ARRAYF32: int
SDL_PIXELTYPE_INDEX2: int
SDL_BitmapOrder = c_int
SDL_BITMAPORDER_NONE: int
SDL_BITMAPORDER_4321: int
SDL_BITMAPORDER_1234: int
SDL_PackedOrder = c_int
SDL_PACKEDORDER_NONE: int
SDL_PACKEDORDER_XRGB: int
SDL_PACKEDORDER_RGBX: int
SDL_PACKEDORDER_ARGB: int
SDL_PACKEDORDER_RGBA: int
SDL_PACKEDORDER_XBGR: int
SDL_PACKEDORDER_BGRX: int
SDL_PACKEDORDER_ABGR: int
SDL_PACKEDORDER_BGRA: int
SDL_ArrayOrder = c_int
SDL_ARRAYORDER_NONE: int
SDL_ARRAYORDER_RGB: int
SDL_ARRAYORDER_RGBA: int
SDL_ARRAYORDER_ARGB: int
SDL_ARRAYORDER_BGR: int
SDL_ARRAYORDER_BGRA: int
SDL_ARRAYORDER_ABGR: int
SDL_PackedLayout = c_int
SDL_PACKEDLAYOUT_NONE: int
SDL_PACKEDLAYOUT_332: int
SDL_PACKEDLAYOUT_4444: int
SDL_PACKEDLAYOUT_1555: int
SDL_PACKEDLAYOUT_5551: int
SDL_PACKEDLAYOUT_565: int
SDL_PACKEDLAYOUT_8888: int
SDL_PACKEDLAYOUT_2101010: int
SDL_PACKEDLAYOUT_1010102: int

def SDL_FOURCC(a: str, b: str, c: str, d: str) -> int: ...
def SDL_DEFINE_PIXELFORMAT(ptype: int, order: int, layout: int, bits: int, pbytes: int) -> int: ...

SDL_DEFINE_PIXELFOURCC = SDL_FOURCC

def SDL_PIXELFLAG(X: int, /) -> int: ...
def SDL_PIXELTYPE(X: int, /) -> int: ...
def SDL_PIXELORDER(X: int, /) -> int: ...
def SDL_PIXELLAYOUT(X: int, /) -> int: ...
def SDL_BITSPERPIXEL(X: int, /) -> int: ...
def SDL_ISPIXELFORMAT_FOURCC(fmt: int, /) -> int: ...
def SDL_BYTESPERPIXEL(x: int) -> int: ...
def SDL_ISPIXELFORMAT_INDEXED(pformat: int) -> bool: ...
def SDL_ISPIXELFORMAT_PACKED(pformat: int) -> bool: ...
def SDL_ISPIXELFORMAT_ARRAY(pformat: int) -> bool: ...
def SDL_ISPIXELFORMAT_ALPHA(pformat: int) -> bool: ...

SDL_PixelFormatEnum = c_int
SDL_PIXELFORMAT_UNKNOWN: int
SDL_PIXELFORMAT_INDEX1LSB: int
SDL_PIXELFORMAT_INDEX1MSB: int
SDL_PIXELFORMAT_INDEX2LSB: int
SDL_PIXELFORMAT_INDEX2MSB: int
SDL_PIXELFORMAT_INDEX4LSB: int
SDL_PIXELFORMAT_INDEX4MSB: int
SDL_PIXELFORMAT_INDEX8: int
SDL_PIXELFORMAT_RGB332: int
SDL_PIXELFORMAT_XRGB4444: int
SDL_PIXELFORMAT_RGB444 = SDL_PIXELFORMAT_XRGB4444
SDL_PIXELFORMAT_XBGR4444: int
SDL_PIXELFORMAT_BGR444 = SDL_PIXELFORMAT_XBGR4444
SDL_PIXELFORMAT_XRGB1555: int
SDL_PIXELFORMAT_RGB555 = SDL_PIXELFORMAT_XRGB1555
SDL_PIXELFORMAT_XBGR1555: int
SDL_PIXELFORMAT_BGR555 = SDL_PIXELFORMAT_XBGR1555
SDL_PIXELFORMAT_ARGB4444: int
SDL_PIXELFORMAT_RGBA4444: int
SDL_PIXELFORMAT_ABGR4444: int
SDL_PIXELFORMAT_BGRA4444: int
SDL_PIXELFORMAT_ARGB1555: int
SDL_PIXELFORMAT_RGBA5551: int
SDL_PIXELFORMAT_ABGR1555: int
SDL_PIXELFORMAT_BGRA5551: int
SDL_PIXELFORMAT_RGB565: int
SDL_PIXELFORMAT_BGR565: int
SDL_PIXELFORMAT_RGB24: int
SDL_PIXELFORMAT_BGR24: int
SDL_PIXELFORMAT_XRGB8888: int
SDL_PIXELFORMAT_RGB888 = SDL_PIXELFORMAT_XRGB8888
SDL_PIXELFORMAT_RGBX8888: int
SDL_PIXELFORMAT_XBGR8888: int
SDL_PIXELFORMAT_BGR888 = SDL_PIXELFORMAT_XBGR8888
SDL_PIXELFORMAT_BGRX8888: int
SDL_PIXELFORMAT_ARGB8888: int
SDL_PIXELFORMAT_RGBA8888: int
SDL_PIXELFORMAT_ABGR8888: int
SDL_PIXELFORMAT_BGRA8888: int
SDL_PIXELFORMAT_ARGB2101010: int
SDL_PIXELFORMAT_RGBA32: int
SDL_PIXELFORMAT_ARGB32: int
SDL_PIXELFORMAT_BGRA32: int
SDL_PIXELFORMAT_ABGR32: int
SDL_PIXELFORMAT_RGBX32: int
SDL_PIXELFORMAT_XRGB32: int
SDL_PIXELFORMAT_BGRX32: int
SDL_PIXELFORMAT_XBGR32: int
SDL_PIXELFORMAT_YV12: int
SDL_PIXELFORMAT_IYUV: int
SDL_PIXELFORMAT_YUY2: int
SDL_PIXELFORMAT_UYVY: int
SDL_PIXELFORMAT_YVYU: int
SDL_PIXELFORMAT_NV12: int
SDL_PIXELFORMAT_NV21: int
SDL_PIXELFORMAT_EXTERNAL_OES: int
NAME_MAP: dict[str, int]
ALL_PIXELFORMATS: tuple[int, ...]

class SDL_Color(Structure):
    r: int
    g: int
    b: int
    a: int
    def __init__(self, r: int = 255, g: int = 255, b: int = 255, a: int = 255) -> None: ...
    def __copy__(self) -> SDL_Color: ...
    def __deepcopy__(self, memo: object) -> SDL_Color: ...
    def __eq__(self, color: object) -> bool: ...
    def __ne__(self, color: object) -> bool: ...

SDL_Colour = SDL_Color

class SDL_Palette(Structure):
    ncolors: int
    colors: _Pointer[SDL_Color]
    version: int
    refcount: int

class SDL_PixelFormat(Structure):
    format: int
    palette: _Pointer[SDL_Palette]
    BitsPerPixel: int
    BytesPerPixel: int
    padding: Array[Uint8]
    Rmask: int
    Gmask: int
    Bmask: int
    Amask: int
    Rloss: int
    Gloss: int
    Bloss: int
    Aloss: int
    Rshift: int
    Gshift: int
    Bshift: int
    Ashift: int
    refcount: int
    next: _Pointer[SDL_PixelFormat]

def SDL_GetPixelFormatName(format: int, /) -> bytes | None: ...
def SDL_PixelFormatEnumToMasks(
    format: int,
    bpp: _Pointer[c_int],
    Rmask: _Pointer[Uint32],
    Gmask: _Pointer[Uint32],
    Bmask: _Pointer[Uint32],
    Amask: _Pointer[Uint32],
    /,
) -> int: ...
def SDL_MasksToPixelFormatEnum(bpp: int, Rmask: int, Gmask: int, Bmask: int, Amask: int, /) -> int: ...
def SDL_AllocFormat(pixel_format: int, /) -> _Pointer[SDL_PixelFormat]: ...
def SDL_FreeFormat(format: _Pointer[SDL_PixelFormat], /) -> None: ...
def SDL_AllocPalette(ncolors: int, /) -> _Pointer[SDL_Palette]: ...
def SDL_SetPixelFormatPalette(format: _Pointer[SDL_PixelFormat], palette: _Pointer[SDL_Palette], /) -> int: ...
def SDL_SetPaletteColors(
    palette: _Pointer[SDL_Palette], colors: _Pointer[SDL_Color], firstcolor: int, ncolors: int, /
) -> int: ...
def SDL_FreePalette(palette: _Pointer[SDL_Palette], /) -> None: ...
def SDL_MapRGB(format: _Pointer[SDL_PixelFormat], r: int, g: int, b: int, /) -> int: ...
def SDL_MapRGBA(format: _Pointer[SDL_PixelFormat], r: int, g: int, b: int, a: int, /) -> int: ...
def SDL_GetRGB(
    pixel: int,
    format: _Pointer[SDL_PixelFormat],
    r: _Pointer[Uint8],
    g: _Pointer[Uint8],
    b: _Pointer[Uint8],
    /,
) -> None: ...
def SDL_GetRGBA(
    pixel: int,
    format: _Pointer[SDL_PixelFormat],
    r: _Pointer[Uint8],
    g: _Pointer[Uint8],
    b: _Pointer[Uint8],
    a: _Pointer[Uint8],
    /,
) -> None: ...
def SDL_CalculateGammaRamp(gamma: float, ramp: _Pointer[Uint16], /) -> None: ...
