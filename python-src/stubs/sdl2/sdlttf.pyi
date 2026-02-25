from ctypes import _Pointer, c_int, c_void_p

from .error import SDL_GetError, SDL_SetError
from .pixels import SDL_Color
from .rwops import SDL_RWops
from .stdinc import Uint16
from .surface import SDL_Surface
from .version import SDL_version

__all__ = [
    'HB_DIRECTION_BTT',
    'HB_DIRECTION_INVALID',
    'HB_DIRECTION_LTR',
    'HB_DIRECTION_RTL',
    'HB_DIRECTION_TTB',
    'HB_TAG',
    'SDL_TTF_COMPILEDVERSION',
    'SDL_TTF_MAJOR_VERSION',
    'SDL_TTF_MINOR_VERSION',
    'SDL_TTF_PATCHLEVEL',
    'SDL_TTF_VERSION',
    'SDL_TTF_VERSION_ATLEAST',
    'TTF_DIRECTION_BTT',
    'TTF_DIRECTION_LTR',
    'TTF_DIRECTION_RTL',
    'TTF_DIRECTION_TTB',
    'TTF_HINTING_LIGHT',
    'TTF_HINTING_LIGHT_SUBPIXEL',
    'TTF_HINTING_MONO',
    'TTF_HINTING_NONE',
    'TTF_HINTING_NORMAL',
    'TTF_MAJOR_VERSION',
    'TTF_MINOR_VERSION',
    'TTF_PATCHLEVEL',
    'TTF_STYLE_BOLD',
    'TTF_STYLE_ITALIC',
    'TTF_STYLE_NORMAL',
    'TTF_STYLE_STRIKETHROUGH',
    'TTF_STYLE_UNDERLINE',
    'TTF_VERSION',
    'TTF_WRAPPED_ALIGN_CENTER',
    'TTF_WRAPPED_ALIGN_LEFT',
    'TTF_WRAPPED_ALIGN_RIGHT',
    'UNICODE_BOM_NATIVE',
    'UNICODE_BOM_SWAPPED',
    'TTF_ByteSwappedUNICODE',
    'TTF_CloseFont',
    'TTF_Direction',
    'TTF_Font',
    'TTF_FontAscent',
    'TTF_FontDescent',
    'TTF_FontFaceFamilyName',
    'TTF_FontFaceIsFixedWidth',
    'TTF_FontFaceStyleName',
    'TTF_FontFaces',
    'TTF_FontHeight',
    'TTF_FontLineSkip',
    'TTF_GetError',
    'TTF_GetFontHinting',
    'TTF_GetFontKerning',
    'TTF_GetFontKerningSize',
    'TTF_GetFontKerningSizeGlyphs',
    'TTF_GetFontKerningSizeGlyphs32',
    'TTF_GetFontOutline',
    'TTF_GetFontSDF',
    'TTF_GetFontStyle',
    'TTF_GetFontWrappedAlign',
    'TTF_GetFreeTypeVersion',
    'TTF_GetHarfBuzzVersion',
    'TTF_GlyphIsProvided',
    'TTF_GlyphIsProvided32',
    'TTF_GlyphMetrics',
    'TTF_GlyphMetrics32',
    'TTF_Init',
    'TTF_Linked_Version',
    'TTF_MeasureText',
    'TTF_MeasureUNICODE',
    'TTF_MeasureUTF8',
    'TTF_OpenFont',
    'TTF_OpenFontDPI',
    'TTF_OpenFontDPIRW',
    'TTF_OpenFontIndex',
    'TTF_OpenFontIndexDPI',
    'TTF_OpenFontIndexDPIRW',
    'TTF_OpenFontIndexRW',
    'TTF_OpenFontRW',
    'TTF_Quit',
    'TTF_RenderGlyph32_Blended',
    'TTF_RenderGlyph32_LCD',
    'TTF_RenderGlyph32_Shaded',
    'TTF_RenderGlyph32_Solid',
    'TTF_RenderGlyph_Blended',
    'TTF_RenderGlyph_LCD',
    'TTF_RenderGlyph_Shaded',
    'TTF_RenderGlyph_Solid',
    'TTF_RenderText',
    'TTF_RenderText_Blended',
    'TTF_RenderText_Blended_Wrapped',
    'TTF_RenderText_LCD',
    'TTF_RenderText_LCD_Wrapped',
    'TTF_RenderText_Shaded',
    'TTF_RenderText_Shaded_Wrapped',
    'TTF_RenderText_Solid',
    'TTF_RenderText_Solid_Wrapped',
    'TTF_RenderUNICODE',
    'TTF_RenderUNICODE_Blended',
    'TTF_RenderUNICODE_Blended_Wrapped',
    'TTF_RenderUNICODE_LCD',
    'TTF_RenderUNICODE_LCD_Wrapped',
    'TTF_RenderUNICODE_Shaded',
    'TTF_RenderUNICODE_Shaded_Wrapped',
    'TTF_RenderUNICODE_Solid',
    'TTF_RenderUNICODE_Solid_Wrapped',
    'TTF_RenderUTF8',
    'TTF_RenderUTF8_Blended',
    'TTF_RenderUTF8_Blended_Wrapped',
    'TTF_RenderUTF8_LCD',
    'TTF_RenderUTF8_LCD_Wrapped',
    'TTF_RenderUTF8_Shaded',
    'TTF_RenderUTF8_Shaded_Wrapped',
    'TTF_RenderUTF8_Solid',
    'TTF_RenderUTF8_Solid_Wrapped',
    'TTF_SetDirection',
    'TTF_SetError',
    'TTF_SetFontDirection',
    'TTF_SetFontHinting',
    'TTF_SetFontKerning',
    'TTF_SetFontOutline',
    'TTF_SetFontSDF',
    'TTF_SetFontScriptName',
    'TTF_SetFontSize',
    'TTF_SetFontSizeDPI',
    'TTF_SetFontStyle',
    'TTF_SetFontWrappedAlign',
    'TTF_SetScript',
    'TTF_SizeText',
    'TTF_SizeUNICODE',
    'TTF_SizeUTF8',
    'TTF_WasInit',
    'get_dll_file',
    'hb_direction_t',
]

def get_dll_file() -> str: ...

SDL_TTF_MAJOR_VERSION: int
SDL_TTF_MINOR_VERSION: int
SDL_TTF_PATCHLEVEL: int

def SDL_TTF_VERSION(x: object, /) -> None: ...

TTF_MAJOR_VERSION = SDL_TTF_MAJOR_VERSION
TTF_MINOR_VERSION = SDL_TTF_MINOR_VERSION
TTF_PATCHLEVEL = SDL_TTF_PATCHLEVEL
TTF_VERSION = SDL_TTF_VERSION
SDL_TTF_COMPILEDVERSION: int

def SDL_TTF_VERSION_ATLEAST(x: int, y: int, z: int, /) -> bool: ...

UNICODE_BOM_NATIVE: int
UNICODE_BOM_SWAPPED: int
TTF_STYLE_NORMAL: int
TTF_STYLE_BOLD: int
TTF_STYLE_ITALIC: int
TTF_STYLE_UNDERLINE: int
TTF_STYLE_STRIKETHROUGH: int
TTF_HINTING_NORMAL: int
TTF_HINTING_LIGHT: int
TTF_HINTING_MONO: int
TTF_HINTING_NONE: int
TTF_HINTING_LIGHT_SUBPIXEL: int
TTF_WRAPPED_ALIGN_LEFT: int
TTF_WRAPPED_ALIGN_CENTER: int
TTF_WRAPPED_ALIGN_RIGHT: int
TTF_Direction = c_int
TTF_DIRECTION_LTR: int
TTF_DIRECTION_RTL: int
TTF_DIRECTION_TTB: int
TTF_DIRECTION_BTT: int

class TTF_Font(c_void_p): ...

hb_direction_t = c_int
HB_DIRECTION_INVALID: int
HB_DIRECTION_LTR: int
HB_DIRECTION_RTL: int
HB_DIRECTION_TTB: int
HB_DIRECTION_BTT: int

def HB_TAG(c1: str, c2: str, c3: str, c4: str, /) -> int: ...
def TTF_Linked_Version() -> _Pointer[SDL_version]: ...
def TTF_GetFreeTypeVersion(major: _Pointer[c_int], minor: _Pointer[c_int], patch: _Pointer[c_int], /) -> None: ...
def TTF_GetHarfBuzzVersion(major: _Pointer[c_int], minor: _Pointer[c_int], patch: _Pointer[c_int], /) -> None: ...
def TTF_ByteSwappedUNICODE(swapped: int, /) -> None: ...
def TTF_Init() -> int: ...
def TTF_OpenFont(file: bytes | None, ptsize: int, /) -> _Pointer[TTF_Font]: ...
def TTF_OpenFontIndex(file: bytes | None, ptsize: int, index: int, /) -> _Pointer[TTF_Font]: ...
def TTF_OpenFontRW(src: _Pointer[SDL_RWops], freesrc: int, ptsize: int, /) -> _Pointer[TTF_Font]: ...
def TTF_OpenFontIndexRW(src: _Pointer[SDL_RWops], freesrc: int, ptsize: int, index: int, /) -> _Pointer[TTF_Font]: ...
def TTF_OpenFontDPI(file: bytes | None, ptsize: int, hdpi: int, vdpi: int, /) -> _Pointer[TTF_Font]: ...
def TTF_OpenFontIndexDPI(
    file: bytes | None, ptsize: int, index: int, hdpi: int, vdpi: int, /
) -> _Pointer[TTF_Font]: ...
def TTF_OpenFontDPIRW(
    src: _Pointer[SDL_RWops], freesrc: int, ptsize: int, hdpi: int, vdpi: int, /
) -> _Pointer[TTF_Font]: ...
def TTF_OpenFontIndexDPIRW(
    src: _Pointer[SDL_RWops],
    freesrc: int,
    ptsize: int,
    index: int,
    hdpi: int,
    vdpi: int,
    /,
) -> _Pointer[TTF_Font]: ...
def TTF_SetFontSize(font: _Pointer[TTF_Font], ptsize: int, /) -> int: ...
def TTF_SetFontSizeDPI(font: _Pointer[TTF_Font], ptsize: int, hdpi: int, vdpi: int, /) -> int: ...
def TTF_GetFontStyle(font: _Pointer[TTF_Font], /) -> int: ...
def TTF_SetFontStyle(font: _Pointer[TTF_Font], style: int, /) -> None: ...
def TTF_GetFontOutline(font: _Pointer[TTF_Font], /) -> int: ...
def TTF_SetFontOutline(font: _Pointer[TTF_Font], outline: int, /) -> None: ...
def TTF_GetFontHinting(font: _Pointer[TTF_Font], /) -> int: ...
def TTF_SetFontHinting(font: _Pointer[TTF_Font], hinting: int, /) -> None: ...
def TTF_GetFontWrappedAlign(font: _Pointer[TTF_Font], /) -> int: ...
def TTF_SetFontWrappedAlign(font: _Pointer[TTF_Font], align: int, /) -> None: ...
def TTF_FontHeight(font: _Pointer[TTF_Font], /) -> int: ...
def TTF_FontAscent(font: _Pointer[TTF_Font], /) -> int: ...
def TTF_FontDescent(font: _Pointer[TTF_Font], /) -> int: ...
def TTF_FontLineSkip(font: _Pointer[TTF_Font], /) -> int: ...
def TTF_GetFontKerning(font: _Pointer[TTF_Font], /) -> int: ...
def TTF_SetFontKerning(font: _Pointer[TTF_Font], allowed: int, /) -> None: ...
def TTF_FontFaces(font: _Pointer[TTF_Font], /) -> int: ...
def TTF_FontFaceIsFixedWidth(font: _Pointer[TTF_Font], /) -> int: ...
def TTF_FontFaceFamilyName(font: _Pointer[TTF_Font], /) -> bytes | None: ...
def TTF_FontFaceStyleName(font: _Pointer[TTF_Font], /) -> bytes | None: ...
def TTF_GlyphIsProvided(font: _Pointer[TTF_Font], ch: int, /) -> int: ...
def TTF_GlyphIsProvided32(font: _Pointer[TTF_Font], ch: int, /) -> int: ...
def TTF_GlyphMetrics(
    font: _Pointer[TTF_Font],
    ch: int,
    minx: _Pointer[c_int],
    maxx: _Pointer[c_int],
    miny: _Pointer[c_int],
    maxy: _Pointer[c_int],
    advance: _Pointer[c_int],
    /,
) -> int: ...
def TTF_GlyphMetrics32(
    font: _Pointer[TTF_Font],
    ch: int,
    minx: _Pointer[c_int],
    maxx: _Pointer[c_int],
    miny: _Pointer[c_int],
    maxy: _Pointer[c_int],
    advance: _Pointer[c_int],
    /,
) -> int: ...
def TTF_SizeText(font: _Pointer[TTF_Font], text: bytes | None, w: _Pointer[c_int], h: _Pointer[c_int], /) -> int: ...
def TTF_SizeUTF8(font: _Pointer[TTF_Font], text: bytes | None, w: _Pointer[c_int], h: _Pointer[c_int], /) -> int: ...
def TTF_SizeUNICODE(
    font: _Pointer[TTF_Font], text: _Pointer[Uint16], w: _Pointer[c_int], h: _Pointer[c_int], /
) -> int: ...
def TTF_MeasureText(
    font: _Pointer[TTF_Font],
    text: bytes | None,
    measure_width: int,
    extent: _Pointer[c_int],
    count: _Pointer[c_int],
    /,
) -> int: ...
def TTF_MeasureUTF8(
    font: _Pointer[TTF_Font],
    text: bytes | None,
    measure_width: int,
    extent: _Pointer[c_int],
    count: _Pointer[c_int],
    /,
) -> int: ...
def TTF_MeasureUNICODE(
    font: _Pointer[TTF_Font],
    text: _Pointer[Uint16],
    measure_width: int,
    extent: _Pointer[c_int],
    count: _Pointer[c_int],
    /,
) -> int: ...
def TTF_RenderText_Solid(font: _Pointer[TTF_Font], text: bytes | None, fg: SDL_Color, /) -> _Pointer[SDL_Surface]: ...
def TTF_RenderUTF8_Solid(font: _Pointer[TTF_Font], text: bytes | None, fg: SDL_Color, /) -> _Pointer[SDL_Surface]: ...
def TTF_RenderUNICODE_Solid(
    font: _Pointer[TTF_Font], text: _Pointer[Uint16], fg: SDL_Color, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderText_Solid_Wrapped(
    font: _Pointer[TTF_Font], text: bytes | None, fg: SDL_Color, wrapLength: int, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderUTF8_Solid_Wrapped(
    font: _Pointer[TTF_Font], text: bytes | None, fg: SDL_Color, wrapLength: int, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderUNICODE_Solid_Wrapped(
    font: _Pointer[TTF_Font], text: _Pointer[Uint16], fg: SDL_Color, wrapLength: int, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderGlyph_Solid(font: _Pointer[TTF_Font], ch: int, fg: SDL_Color, /) -> _Pointer[SDL_Surface]: ...
def TTF_RenderGlyph32_Solid(font: _Pointer[TTF_Font], ch: int, fg: SDL_Color, /) -> _Pointer[SDL_Surface]: ...
def TTF_RenderText_Shaded(
    font: _Pointer[TTF_Font], text: bytes | None, fg: SDL_Color, bg: SDL_Color, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderUTF8_Shaded(
    font: _Pointer[TTF_Font], text: bytes | None, fg: SDL_Color, bg: SDL_Color, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderUNICODE_Shaded(
    font: _Pointer[TTF_Font], text: _Pointer[Uint16], fg: SDL_Color, bg: SDL_Color, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderText_Shaded_Wrapped(
    font: _Pointer[TTF_Font],
    text: bytes | None,
    fg: SDL_Color,
    bg: SDL_Color,
    wrapLength: int,
    /,
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderUTF8_Shaded_Wrapped(
    font: _Pointer[TTF_Font],
    text: bytes | None,
    fg: SDL_Color,
    bg: SDL_Color,
    wrapLength: int,
    /,
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderUNICODE_Shaded_Wrapped(
    font: _Pointer[TTF_Font],
    text: _Pointer[Uint16],
    fg: SDL_Color,
    bg: SDL_Color,
    wrapLength: int,
    /,
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderGlyph_Shaded(
    font: _Pointer[TTF_Font], ch: int, fg: SDL_Color, bg: SDL_Color, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderGlyph32_Shaded(
    font: _Pointer[TTF_Font], ch: int, fg: SDL_Color, bg: SDL_Color, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderText_Blended(font: _Pointer[TTF_Font], text: bytes | None, fg: SDL_Color, /) -> _Pointer[SDL_Surface]: ...
def TTF_RenderUTF8_Blended(font: _Pointer[TTF_Font], text: bytes | None, fg: SDL_Color, /) -> _Pointer[SDL_Surface]: ...
def TTF_RenderUNICODE_Blended(
    font: _Pointer[TTF_Font], text: _Pointer[Uint16], fg: SDL_Color, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderText_Blended_Wrapped(
    font: _Pointer[TTF_Font], text: bytes | None, fg: SDL_Color, wrapLength: int, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderUTF8_Blended_Wrapped(
    font: _Pointer[TTF_Font], text: bytes | None, fg: SDL_Color, wrapLength: int, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderUNICODE_Blended_Wrapped(
    font: _Pointer[TTF_Font], text: _Pointer[Uint16], fg: SDL_Color, wrapLength: int, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderGlyph_Blended(font: _Pointer[TTF_Font], ch: int, fg: SDL_Color, /) -> _Pointer[SDL_Surface]: ...
def TTF_RenderGlyph32_Blended(font: _Pointer[TTF_Font], ch: int, fg: SDL_Color, /) -> _Pointer[SDL_Surface]: ...
def TTF_RenderText_LCD(
    font: _Pointer[TTF_Font], text: bytes | None, fg: SDL_Color, bg: SDL_Color, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderUTF8_LCD(
    font: _Pointer[TTF_Font], text: bytes | None, fg: SDL_Color, bg: SDL_Color, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderUNICODE_LCD(
    font: _Pointer[TTF_Font], text: _Pointer[Uint16], fg: SDL_Color, bg: SDL_Color, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderText_LCD_Wrapped(
    font: _Pointer[TTF_Font],
    text: bytes | None,
    fg: SDL_Color,
    bg: SDL_Color,
    wrapLength: int,
    /,
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderUTF8_LCD_Wrapped(
    font: _Pointer[TTF_Font],
    text: bytes | None,
    fg: SDL_Color,
    bg: SDL_Color,
    wrapLength: int,
    /,
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderUNICODE_LCD_Wrapped(
    font: _Pointer[TTF_Font],
    text: _Pointer[Uint16],
    fg: SDL_Color,
    bg: SDL_Color,
    wrapLength: int,
    /,
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderGlyph_LCD(
    font: _Pointer[TTF_Font], ch: int, fg: SDL_Color, bg: SDL_Color, /
) -> _Pointer[SDL_Surface]: ...
def TTF_RenderGlyph32_LCD(
    font: _Pointer[TTF_Font], ch: int, fg: SDL_Color, bg: SDL_Color, /
) -> _Pointer[SDL_Surface]: ...
def TTF_SetDirection(direction: int, /) -> int: ...
def TTF_SetScript(script: int, /) -> int: ...
def TTF_SetFontDirection(font: _Pointer[TTF_Font], direction: int, /) -> int: ...
def TTF_SetFontScriptName(font: _Pointer[TTF_Font], script: bytes | None, /) -> int: ...
def TTF_CloseFont(font: _Pointer[TTF_Font], /) -> None: ...
def TTF_Quit() -> None: ...
def TTF_WasInit() -> int: ...
def TTF_GetFontKerningSize(font: _Pointer[TTF_Font], prev_index: int, index: int, /) -> int: ...
def TTF_GetFontKerningSizeGlyphs(font: _Pointer[TTF_Font], previous_ch: int, ch: int, /) -> int: ...
def TTF_GetFontKerningSizeGlyphs32(font: _Pointer[TTF_Font], previous_ch: int, ch: int, /) -> int: ...
def TTF_SetFontSDF(font: _Pointer[TTF_Font], on_off: int, /) -> int: ...
def TTF_GetFontSDF(font: _Pointer[TTF_Font], /) -> int: ...

TTF_RenderText = TTF_RenderText_Shaded
TTF_RenderUTF8 = TTF_RenderUTF8_Shaded
TTF_RenderUNICODE = TTF_RenderUNICODE_Shaded

TTF_SetError = SDL_SetError
TTF_GetError = SDL_GetError
