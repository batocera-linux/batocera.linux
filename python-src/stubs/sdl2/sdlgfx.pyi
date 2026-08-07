from ctypes import Structure, _Pointer, c_int

from .render import SDL_Renderer
from .stdinc import Sint16
from .surface import SDL_Surface

__all__ = [
    'FPS_DEFAULT',
    'FPS_LOWER_LIMIT',
    'FPS_UPPER_LIMIT',
    'SDL2_GFXPRIMITIVES_MAJOR',
    'SDL2_GFXPRIMITIVES_MICRO',
    'SDL2_GFXPRIMITIVES_MINOR',
    'SMOOTHING_OFF',
    'SMOOTHING_ON',
    'FPSManager',
    'SDL_framerateDelay',
    'SDL_getFramecount',
    'SDL_getFramerate',
    'SDL_initFramerate',
    'SDL_setFramerate',
    'aacircleColor',
    'aacircleRGBA',
    'aaellipseColor',
    'aaellipseRGBA',
    'aalineColor',
    'aalineRGBA',
    'aapolygonColor',
    'aapolygonRGBA',
    'aatrigonColor',
    'aatrigonRGBA',
    'arcColor',
    'arcRGBA',
    'bezierColor',
    'bezierRGBA',
    'boxColor',
    'boxRGBA',
    'characterColor',
    'characterRGBA',
    'circleColor',
    'circleRGBA',
    'ellipseColor',
    'ellipseRGBA',
    'filledCircleColor',
    'filledCircleRGBA',
    'filledEllipseColor',
    'filledEllipseRGBA',
    'filledPieColor',
    'filledPieRGBA',
    'filledPolygonColor',
    'filledPolygonRGBA',
    'filledTrigonColor',
    'filledTrigonRGBA',
    'get_dll_file',
    'gfxPrimitivesSetFont',
    'gfxPrimitivesSetFontRotation',
    'hlineColor',
    'hlineRGBA',
    'lineColor',
    'lineRGBA',
    'pieColor',
    'pieRGBA',
    'pixelColor',
    'pixelRGBA',
    'polygonColor',
    'polygonRGBA',
    'rectangleColor',
    'rectangleRGBA',
    'rotateSurface90Degrees',
    'rotozoomSurface',
    'rotozoomSurfaceSize',
    'rotozoomSurfaceSizeXY',
    'rotozoomSurfaceXY',
    'roundedBoxColor',
    'roundedBoxRGBA',
    'roundedRectangleColor',
    'roundedRectangleRGBA',
    'shrinkSurface',
    'stringColor',
    'stringRGBA',
    'texturedPolygon',
    'thickLineColor',
    'thickLineRGBA',
    'trigonColor',
    'trigonRGBA',
    'vlineColor',
    'vlineRGBA',
    'zoomSurface',
    'zoomSurfaceSize',
]

def get_dll_file() -> str: ...

SDL2_GFXPRIMITIVES_MAJOR: int
SDL2_GFXPRIMITIVES_MINOR: int
SDL2_GFXPRIMITIVES_MICRO: int
FPS_UPPER_LIMIT: int
FPS_LOWER_LIMIT: int
FPS_DEFAULT: int
SMOOTHING_OFF: int
SMOOTHING_ON: int

class FPSManager(Structure):
    framecount: int
    rateticks: float
    baseticks: int
    lastticks: int
    rate: int

# Framerate manager
def SDL_initFramerate(manager: _Pointer[FPSManager], /) -> None: ...
def SDL_setFramerate(manager: _Pointer[FPSManager], rate: int, /) -> int: ...
def SDL_getFramerate(manager: _Pointer[FPSManager], /) -> int: ...
def SDL_getFramecount(manager: _Pointer[FPSManager], /) -> int: ...
def SDL_framerateDelay(manager: _Pointer[FPSManager], /) -> int: ...

# Pixel
def pixelColor(renderer: _Pointer[SDL_Renderer], x: int, y: int, color: int, /) -> int: ...
def pixelRGBA(renderer: _Pointer[SDL_Renderer], x: int, y: int, r: int, g: int, b: int, a: int, /) -> int: ...

# Horizontal / vertical lines
def hlineColor(renderer: _Pointer[SDL_Renderer], x1: int, x2: int, y: int, color: int, /) -> int: ...
def hlineRGBA(renderer: _Pointer[SDL_Renderer], x1: int, x2: int, y: int, r: int, g: int, b: int, a: int, /) -> int: ...
def vlineColor(renderer: _Pointer[SDL_Renderer], x: int, y1: int, y2: int, color: int, /) -> int: ...
def vlineRGBA(renderer: _Pointer[SDL_Renderer], x: int, y1: int, y2: int, r: int, g: int, b: int, a: int, /) -> int: ...

# Rectangles
def rectangleColor(renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, color: int, /) -> int: ...
def rectangleRGBA(
    renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int, a: int, /
) -> int: ...
def roundedRectangleColor(
    renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, rad: int, color: int, /
) -> int: ...
def roundedRectangleRGBA(
    renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, rad: int, r: int, g: int, b: int, a: int, /
) -> int: ...

# Boxes (filled rectangles)
def boxColor(renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, color: int, /) -> int: ...
def boxRGBA(
    renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int, a: int, /
) -> int: ...
def roundedBoxColor(
    renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, rad: int, color: int, /
) -> int: ...
def roundedBoxRGBA(
    renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, rad: int, r: int, g: int, b: int, a: int, /
) -> int: ...

# Lines
def lineColor(renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, color: int, /) -> int: ...
def lineRGBA(
    renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int, a: int, /
) -> int: ...
def aalineColor(renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, color: int, /) -> int: ...
def aalineRGBA(
    renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int, a: int, /
) -> int: ...
def thickLineColor(
    renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, width: int, color: int, /
) -> int: ...
def thickLineRGBA(
    renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, width: int, r: int, g: int, b: int, a: int, /
) -> int: ...

# Circle
def circleColor(renderer: _Pointer[SDL_Renderer], x: int, y: int, rad: int, color: int, /) -> int: ...
def circleRGBA(
    renderer: _Pointer[SDL_Renderer], x: int, y: int, rad: int, r: int, g: int, b: int, a: int, /
) -> int: ...
def arcColor(
    renderer: _Pointer[SDL_Renderer], x: int, y: int, rad: int, start: int, end: int, color: int, /
) -> int: ...
def arcRGBA(
    renderer: _Pointer[SDL_Renderer], x: int, y: int, rad: int, start: int, end: int, r: int, g: int, b: int, a: int, /
) -> int: ...
def aacircleColor(renderer: _Pointer[SDL_Renderer], x: int, y: int, rad: int, color: int, /) -> int: ...
def aacircleRGBA(
    renderer: _Pointer[SDL_Renderer], x: int, y: int, rad: int, r: int, g: int, b: int, a: int, /
) -> int: ...
def filledCircleColor(renderer: _Pointer[SDL_Renderer], x: int, y: int, rad: int, color: int, /) -> int: ...
def filledCircleRGBA(
    renderer: _Pointer[SDL_Renderer], x: int, y: int, rad: int, r: int, g: int, b: int, a: int, /
) -> int: ...

# Ellipse
def ellipseColor(renderer: _Pointer[SDL_Renderer], x: int, y: int, rx: int, ry: int, color: int, /) -> int: ...
def ellipseRGBA(
    renderer: _Pointer[SDL_Renderer], x: int, y: int, rx: int, ry: int, r: int, g: int, b: int, a: int, /
) -> int: ...
def aaellipseColor(renderer: _Pointer[SDL_Renderer], x: int, y: int, rx: int, ry: int, color: int, /) -> int: ...
def aaellipseRGBA(
    renderer: _Pointer[SDL_Renderer], x: int, y: int, rx: int, ry: int, r: int, g: int, b: int, a: int, /
) -> int: ...
def filledEllipseColor(renderer: _Pointer[SDL_Renderer], x: int, y: int, rx: int, ry: int, color: int, /) -> int: ...
def filledEllipseRGBA(
    renderer: _Pointer[SDL_Renderer], x: int, y: int, rx: int, ry: int, r: int, g: int, b: int, a: int, /
) -> int: ...

# Pie
def pieColor(
    renderer: _Pointer[SDL_Renderer], x: int, y: int, rad: int, start: int, end: int, color: int, /
) -> int: ...
def pieRGBA(
    renderer: _Pointer[SDL_Renderer], x: int, y: int, rad: int, start: int, end: int, r: int, g: int, b: int, a: int, /
) -> int: ...
def filledPieColor(
    renderer: _Pointer[SDL_Renderer], x: int, y: int, rad: int, start: int, end: int, color: int, /
) -> int: ...
def filledPieRGBA(
    renderer: _Pointer[SDL_Renderer], x: int, y: int, rad: int, start: int, end: int, r: int, g: int, b: int, a: int, /
) -> int: ...

# Trigon (triangle)
def trigonColor(
    renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, color: int, /
) -> int: ...
def trigonRGBA(
    renderer: _Pointer[SDL_Renderer],
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    x3: int,
    y3: int,
    r: int,
    g: int,
    b: int,
    a: int,
    /,
) -> int: ...
def aatrigonColor(
    renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, color: int, /
) -> int: ...
def aatrigonRGBA(
    renderer: _Pointer[SDL_Renderer],
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    x3: int,
    y3: int,
    r: int,
    g: int,
    b: int,
    a: int,
    /,
) -> int: ...
def filledTrigonColor(
    renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, x3: int, y3: int, color: int, /
) -> int: ...
def filledTrigonRGBA(
    renderer: _Pointer[SDL_Renderer],
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    x3: int,
    y3: int,
    r: int,
    g: int,
    b: int,
    a: int,
    /,
) -> int: ...

# Polygon
def polygonColor(
    renderer: _Pointer[SDL_Renderer], vx: _Pointer[Sint16], vy: _Pointer[Sint16], n: int, color: int, /
) -> int: ...
def polygonRGBA(
    renderer: _Pointer[SDL_Renderer],
    vx: _Pointer[Sint16],
    vy: _Pointer[Sint16],
    n: int,
    r: int,
    g: int,
    b: int,
    a: int,
    /,
) -> int: ...
def aapolygonColor(
    renderer: _Pointer[SDL_Renderer], vx: _Pointer[Sint16], vy: _Pointer[Sint16], n: int, color: int, /
) -> int: ...
def aapolygonRGBA(
    renderer: _Pointer[SDL_Renderer],
    vx: _Pointer[Sint16],
    vy: _Pointer[Sint16],
    n: int,
    r: int,
    g: int,
    b: int,
    a: int,
    /,
) -> int: ...
def filledPolygonColor(
    renderer: _Pointer[SDL_Renderer], vx: _Pointer[Sint16], vy: _Pointer[Sint16], n: int, color: int, /
) -> int: ...
def filledPolygonRGBA(
    renderer: _Pointer[SDL_Renderer],
    vx: _Pointer[Sint16],
    vy: _Pointer[Sint16],
    n: int,
    r: int,
    g: int,
    b: int,
    a: int,
    /,
) -> int: ...
def texturedPolygon(
    renderer: _Pointer[SDL_Renderer],
    vx: _Pointer[Sint16],
    vy: _Pointer[Sint16],
    n: int,
    texture: _Pointer[SDL_Surface],
    texture_dx: int,
    texture_dy: int,
    /,
) -> int: ...

# Bezier
def bezierColor(
    renderer: _Pointer[SDL_Renderer], vx: _Pointer[Sint16], vy: _Pointer[Sint16], n: int, s: int, color: int, /
) -> int: ...
def bezierRGBA(
    renderer: _Pointer[SDL_Renderer],
    vx: _Pointer[Sint16],
    vy: _Pointer[Sint16],
    n: int,
    s: int,
    r: int,
    g: int,
    b: int,
    a: int,
    /,
) -> int: ...

# Font / text
def gfxPrimitivesSetFont(fontdata: int | None, cw: int, ch: int, /) -> None: ...
def gfxPrimitivesSetFontRotation(rotation: int, /) -> None: ...
def characterColor(renderer: _Pointer[SDL_Renderer], x: int, y: int, c: bytes, color: int, /) -> int: ...
def characterRGBA(
    renderer: _Pointer[SDL_Renderer], x: int, y: int, c: bytes, r: int, g: int, b: int, a: int, /
) -> int: ...
def stringColor(renderer: _Pointer[SDL_Renderer], x: int, y: int, s: bytes | None, color: int, /) -> int: ...
def stringRGBA(
    renderer: _Pointer[SDL_Renderer], x: int, y: int, s: bytes | None, r: int, g: int, b: int, a: int, /
) -> int: ...

# Rotozoom / zoom / shrink / rotate
def rotozoomSurface(src: _Pointer[SDL_Surface], angle: float, zoom: float, smooth: int, /) -> _Pointer[SDL_Surface]: ...
def rotozoomSurfaceXY(
    src: _Pointer[SDL_Surface], angle: float, zoomx: float, zoomy: float, smooth: int, /
) -> _Pointer[SDL_Surface]: ...
def rotozoomSurfaceSize(
    width: int, height: int, angle: float, zoom: float, dstwidth: _Pointer[c_int], dstheight: _Pointer[c_int], /
) -> None: ...
def rotozoomSurfaceSizeXY(
    width: int,
    height: int,
    angle: float,
    zoomx: float,
    zoomy: float,
    dstwidth: _Pointer[c_int],
    dstheight: _Pointer[c_int],
    /,
) -> None: ...
def zoomSurface(src: _Pointer[SDL_Surface], zoomx: float, zoomy: float, smooth: int, /) -> _Pointer[SDL_Surface]: ...
def zoomSurfaceSize(
    width: int, height: int, zoomx: float, zoomy: float, dstwidth: _Pointer[c_int], dstheight: _Pointer[c_int], /
) -> None: ...
def shrinkSurface(src: _Pointer[SDL_Surface], factorx: int, factory: int, /) -> _Pointer[SDL_Surface]: ...
def rotateSurface90Degrees(src: _Pointer[SDL_Surface], numClockwiseTurns: int, /) -> _Pointer[SDL_Surface]: ...
