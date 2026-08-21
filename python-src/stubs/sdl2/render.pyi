from ctypes import Array, Structure, _Pointer, c_float, c_int, c_void_p

from .pixels import SDL_Color
from .rect import SDL_FPoint, SDL_FRect, SDL_Point, SDL_Rect
from .stdinc import Uint8, Uint32
from .surface import SDL_Surface
from .video import SDL_Window

__all__ = [
    'SDL_FLIP_HORIZONTAL',
    'SDL_FLIP_NONE',
    'SDL_FLIP_VERTICAL',
    'SDL_RENDERER_ACCELERATED',
    'SDL_RENDERER_PRESENTVSYNC',
    'SDL_RENDERER_SOFTWARE',
    'SDL_RENDERER_TARGETTEXTURE',
    'SDL_TEXTUREACCESS_STATIC',
    'SDL_TEXTUREACCESS_STREAMING',
    'SDL_TEXTUREACCESS_TARGET',
    'SDL_TEXTUREMODULATE_ALPHA',
    'SDL_TEXTUREMODULATE_COLOR',
    'SDL_TEXTUREMODULATE_NONE',
    'SDL_CreateRenderer',
    'SDL_CreateSoftwareRenderer',
    'SDL_CreateTexture',
    'SDL_CreateTextureFromSurface',
    'SDL_CreateWindowAndRenderer',
    'SDL_DestroyRenderer',
    'SDL_DestroyTexture',
    'SDL_GL_BindTexture',
    'SDL_GL_UnbindTexture',
    'SDL_GetNumRenderDrivers',
    'SDL_GetRenderDrawBlendMode',
    'SDL_GetRenderDrawColor',
    'SDL_GetRenderDriverInfo',
    'SDL_GetRenderTarget',
    'SDL_GetRenderer',
    'SDL_GetRendererInfo',
    'SDL_GetRendererOutputSize',
    'SDL_GetTextureAlphaMod',
    'SDL_GetTextureBlendMode',
    'SDL_GetTextureColorMod',
    'SDL_GetTextureScaleMode',
    'SDL_GetTextureUserData',
    'SDL_LockTexture',
    'SDL_LockTextureToSurface',
    'SDL_QueryTexture',
    'SDL_RenderClear',
    'SDL_RenderCopy',
    'SDL_RenderCopyEx',
    'SDL_RenderCopyExF',
    'SDL_RenderCopyF',
    'SDL_RenderDrawLine',
    'SDL_RenderDrawLineF',
    'SDL_RenderDrawLines',
    'SDL_RenderDrawLinesF',
    'SDL_RenderDrawPoint',
    'SDL_RenderDrawPointF',
    'SDL_RenderDrawPoints',
    'SDL_RenderDrawPointsF',
    'SDL_RenderDrawRect',
    'SDL_RenderDrawRectF',
    'SDL_RenderDrawRects',
    'SDL_RenderDrawRectsF',
    'SDL_RenderFillRect',
    'SDL_RenderFillRectF',
    'SDL_RenderFillRects',
    'SDL_RenderFillRectsF',
    'SDL_RenderFlush',
    'SDL_RenderGeometry',
    'SDL_RenderGeometryRaw',
    'SDL_RenderGetClipRect',
    'SDL_RenderGetIntegerScale',
    'SDL_RenderGetLogicalSize',
    'SDL_RenderGetMetalCommandEncoder',
    'SDL_RenderGetMetalLayer',
    'SDL_RenderGetScale',
    'SDL_RenderGetViewport',
    'SDL_RenderGetWindow',
    'SDL_RenderIsClipEnabled',
    'SDL_RenderLogicalToWindow',
    'SDL_RenderPresent',
    'SDL_RenderReadPixels',
    'SDL_RenderSetClipRect',
    'SDL_RenderSetIntegerScale',
    'SDL_RenderSetLogicalSize',
    'SDL_RenderSetScale',
    'SDL_RenderSetVSync',
    'SDL_RenderSetViewport',
    'SDL_RenderTargetSupported',
    'SDL_RenderWindowToLogical',
    'SDL_Renderer',
    'SDL_RendererFlags',
    'SDL_RendererFlip',
    'SDL_RendererInfo',
    'SDL_ScaleMode',
    'SDL_ScaleModeBest',
    'SDL_ScaleModeLinear',
    'SDL_ScaleModeNearest',
    'SDL_SetRenderDrawBlendMode',
    'SDL_SetRenderDrawColor',
    'SDL_SetRenderTarget',
    'SDL_SetTextureAlphaMod',
    'SDL_SetTextureBlendMode',
    'SDL_SetTextureColorMod',
    'SDL_SetTextureScaleMode',
    'SDL_SetTextureUserData',
    'SDL_Texture',
    'SDL_TextureAccess',
    'SDL_TextureModulate',
    'SDL_UnlockTexture',
    'SDL_UpdateNVTexture',
    'SDL_UpdateTexture',
    'SDL_UpdateYUVTexture',
    'SDL_Vertex',
]

SDL_RendererFlags = c_int
SDL_RENDERER_SOFTWARE: int
SDL_RENDERER_ACCELERATED: int
SDL_RENDERER_PRESENTVSYNC: int
SDL_RENDERER_TARGETTEXTURE: int
SDL_ScaleMode = c_int
SDL_ScaleModeNearest: int
SDL_ScaleModeLinear: int
SDL_ScaleModeBest: int
SDL_TextureAccess = c_int
SDL_TEXTUREACCESS_STATIC: int
SDL_TEXTUREACCESS_STREAMING: int
SDL_TEXTUREACCESS_TARGET: int
SDL_TextureModulate = c_int
SDL_TEXTUREMODULATE_NONE: int
SDL_TEXTUREMODULATE_COLOR: int
SDL_TEXTUREMODULATE_ALPHA: int
SDL_RendererFlip = c_int
SDL_FLIP_NONE: int
SDL_FLIP_HORIZONTAL: int
SDL_FLIP_VERTICAL: int

class SDL_RendererInfo(Structure):
    name: bytes | None
    flags: int
    num_texture_formats: int
    texture_formats: Array[Uint32]
    max_texture_width: int
    max_texture_height: int

class SDL_Vertex(Structure):
    position: SDL_FPoint
    color: SDL_Color
    tex_coord: SDL_FPoint
    def __init__(self, position: object = ..., color: object = ..., tex_coord: object = ...) -> None: ...
    def __copy__(self) -> SDL_Vertex: ...
    def __deepcopy__(self, memo: object) -> SDL_Vertex: ...

class SDL_Renderer(c_void_p): ...
class SDL_Texture(c_void_p): ...

def SDL_GetNumRenderDrivers() -> int: ...
def SDL_GetRenderDriverInfo(index: int, info: _Pointer[SDL_RendererInfo], /) -> int: ...
def SDL_CreateWindowAndRenderer(
    width: int,
    height: int,
    window_flags: int,
    window: _Pointer[_Pointer[SDL_Window]],
    renderer: _Pointer[_Pointer[SDL_Renderer]],
    /,
) -> int: ...
def SDL_CreateRenderer(window: _Pointer[SDL_Window], index: int, flags: int, /) -> _Pointer[SDL_Renderer]: ...
def SDL_CreateSoftwareRenderer(surface: _Pointer[SDL_Surface], /) -> _Pointer[SDL_Renderer]: ...
def SDL_GetRenderer(window: _Pointer[SDL_Window], /) -> _Pointer[SDL_Renderer]: ...
def SDL_RenderGetWindow(renderer: _Pointer[SDL_Renderer], /) -> _Pointer[SDL_Window]: ...
def SDL_GetRendererInfo(renderer: _Pointer[SDL_Renderer], info: _Pointer[SDL_RendererInfo], /) -> int: ...
def SDL_GetRendererOutputSize(renderer: _Pointer[SDL_Renderer], w: _Pointer[c_int], h: _Pointer[c_int], /) -> int: ...
def SDL_CreateTexture(
    renderer: _Pointer[SDL_Renderer], format: int, access: int, w: int, h: int, /
) -> _Pointer[SDL_Texture]: ...
def SDL_CreateTextureFromSurface(
    renderer: _Pointer[SDL_Renderer], surface: _Pointer[SDL_Surface], /
) -> _Pointer[SDL_Texture]: ...
def SDL_QueryTexture(
    texture: _Pointer[SDL_Texture],
    format: _Pointer[Uint32],
    access: _Pointer[c_int],
    w: _Pointer[c_int],
    h: _Pointer[c_int],
    /,
) -> int: ...
def SDL_SetTextureColorMod(texture: _Pointer[SDL_Texture], r: int, g: int, b: int, /) -> int: ...
def SDL_GetTextureColorMod(
    texture: _Pointer[SDL_Texture], r: _Pointer[Uint8], g: _Pointer[Uint8], b: _Pointer[Uint8], /
) -> int: ...
def SDL_SetTextureAlphaMod(texture: _Pointer[SDL_Texture], alpha: int, /) -> int: ...
def SDL_GetTextureAlphaMod(texture: _Pointer[SDL_Texture], alpha: _Pointer[Uint8], /) -> int: ...
def SDL_SetTextureBlendMode(texture: _Pointer[SDL_Texture], blendMode: int, /) -> int: ...
def SDL_GetTextureBlendMode(texture: _Pointer[SDL_Texture], blendMode: _Pointer[c_int], /) -> int: ...
def SDL_SetTextureScaleMode(texture: _Pointer[SDL_Texture], scaleMode: int, /) -> int: ...
def SDL_GetTextureScaleMode(texture: _Pointer[SDL_Texture], scaleMode: _Pointer[c_int], /) -> int: ...
def SDL_SetTextureUserData(texture: _Pointer[SDL_Texture], userdata: c_void_p | int | None, /) -> int: ...
def SDL_GetTextureUserData(texture: _Pointer[SDL_Texture], /) -> int | None: ...
def SDL_UpdateTexture(
    texture: _Pointer[SDL_Texture], rect: _Pointer[SDL_Rect], pixels: c_void_p | int | None, pitch: int, /
) -> int: ...
def SDL_UpdateYUVTexture(
    texture: _Pointer[SDL_Texture],
    rect: _Pointer[SDL_Rect],
    Yplane: _Pointer[Uint8],
    Ypitch: int,
    Uplane: _Pointer[Uint8],
    Upitch: int,
    Vplane: _Pointer[Uint8],
    Vpitch: int,
    /,
) -> int: ...
def SDL_UpdateNVTexture(
    texture: _Pointer[SDL_Texture],
    rect: _Pointer[SDL_Rect],
    Yplane: _Pointer[Uint8],
    Ypitch: int,
    UVplane: _Pointer[Uint8],
    UVpitch: int,
    /,
) -> int: ...
def SDL_LockTexture(
    texture: _Pointer[SDL_Texture],
    rect: _Pointer[SDL_Rect],
    pixels: _Pointer[c_void_p],
    pitch: _Pointer[c_int],
    /,
) -> int: ...
def SDL_LockTextureToSurface(
    texture: _Pointer[SDL_Texture], rect: _Pointer[SDL_Rect], surface: _Pointer[_Pointer[SDL_Surface]], /
) -> int: ...
def SDL_UnlockTexture(texture: _Pointer[SDL_Texture], /) -> None: ...
def SDL_RenderTargetSupported(renderer: _Pointer[SDL_Renderer], /) -> int: ...
def SDL_SetRenderTarget(renderer: _Pointer[SDL_Renderer], texture: _Pointer[SDL_Texture], /) -> int: ...
def SDL_GetRenderTarget(renderer: _Pointer[SDL_Renderer], /) -> _Pointer[SDL_Texture]: ...
def SDL_RenderSetLogicalSize(renderer: _Pointer[SDL_Renderer], w: int, h: int, /) -> int: ...
def SDL_RenderGetLogicalSize(renderer: _Pointer[SDL_Renderer], w: _Pointer[c_int], h: _Pointer[c_int], /) -> None: ...
def SDL_RenderSetIntegerScale(renderer: _Pointer[SDL_Renderer], enable: int, /) -> int: ...
def SDL_RenderGetIntegerScale(renderer: _Pointer[SDL_Renderer], /) -> int: ...
def SDL_RenderSetViewport(renderer: _Pointer[SDL_Renderer], rect: _Pointer[SDL_Rect], /) -> int: ...
def SDL_RenderGetViewport(renderer: _Pointer[SDL_Renderer], rect: _Pointer[SDL_Rect], /) -> None: ...
def SDL_RenderGetClipRect(renderer: _Pointer[SDL_Renderer], rect: _Pointer[SDL_Rect], /) -> None: ...
def SDL_RenderSetClipRect(renderer: _Pointer[SDL_Renderer], rect: _Pointer[SDL_Rect], /) -> int: ...
def SDL_RenderIsClipEnabled(renderer: _Pointer[SDL_Renderer], /) -> int: ...
def SDL_RenderSetScale(renderer: _Pointer[SDL_Renderer], scaleX: float, scaleY: float, /) -> int: ...
def SDL_RenderGetScale(
    renderer: _Pointer[SDL_Renderer], scaleX: _Pointer[c_float], scaleY: _Pointer[c_float], /
) -> None: ...
def SDL_RenderWindowToLogical(
    renderer: _Pointer[SDL_Renderer],
    windowX: int,
    windowY: int,
    logicalX: _Pointer[c_float],
    logicalY: _Pointer[c_float],
    /,
) -> None: ...
def SDL_RenderLogicalToWindow(
    renderer: _Pointer[SDL_Renderer],
    logicalX: float,
    logicalY: float,
    windowX: _Pointer[c_int],
    windowY: _Pointer[c_int],
    /,
) -> None: ...
def SDL_SetRenderDrawColor(renderer: _Pointer[SDL_Renderer], r: int, g: int, b: int, a: int, /) -> int: ...
def SDL_GetRenderDrawColor(
    renderer: _Pointer[SDL_Renderer],
    r: _Pointer[Uint8],
    g: _Pointer[Uint8],
    b: _Pointer[Uint8],
    a: _Pointer[Uint8],
    /,
) -> int: ...
def SDL_SetRenderDrawBlendMode(renderer: _Pointer[SDL_Renderer], blendMode: int, /) -> int: ...
def SDL_GetRenderDrawBlendMode(renderer: _Pointer[SDL_Renderer], blendMode: _Pointer[c_int], /) -> int: ...
def SDL_RenderClear(renderer: _Pointer[SDL_Renderer], /) -> int: ...
def SDL_RenderDrawPoint(renderer: _Pointer[SDL_Renderer], x: int, y: int, /) -> int: ...
def SDL_RenderDrawPoints(renderer: _Pointer[SDL_Renderer], points: _Pointer[SDL_Point], count: int, /) -> int: ...
def SDL_RenderDrawLine(renderer: _Pointer[SDL_Renderer], x1: int, y1: int, x2: int, y2: int, /) -> int: ...
def SDL_RenderDrawLines(renderer: _Pointer[SDL_Renderer], points: _Pointer[SDL_Point], count: int, /) -> int: ...
def SDL_RenderDrawRect(renderer: _Pointer[SDL_Renderer], rect: _Pointer[SDL_Rect], /) -> int: ...
def SDL_RenderDrawRects(renderer: _Pointer[SDL_Renderer], rects: _Pointer[SDL_Rect], count: int, /) -> int: ...
def SDL_RenderFillRect(renderer: _Pointer[SDL_Renderer], rect: _Pointer[SDL_Rect], /) -> int: ...
def SDL_RenderFillRects(renderer: _Pointer[SDL_Renderer], rects: _Pointer[SDL_Rect], count: int, /) -> int: ...
def SDL_RenderCopy(
    renderer: _Pointer[SDL_Renderer],
    texture: _Pointer[SDL_Texture],
    srcrect: _Pointer[SDL_Rect],
    dstrect: _Pointer[SDL_Rect],
    /,
) -> int: ...
def SDL_RenderCopyEx(
    renderer: _Pointer[SDL_Renderer],
    texture: _Pointer[SDL_Texture],
    srcrect: _Pointer[SDL_Rect],
    dstrect: _Pointer[SDL_Rect],
    angle: float,
    center: _Pointer[SDL_Point],
    flip: int,
    /,
) -> int: ...
def SDL_RenderDrawPointF(renderer: _Pointer[SDL_Renderer], x: float, y: float, /) -> int: ...
def SDL_RenderDrawPointsF(renderer: _Pointer[SDL_Renderer], points: _Pointer[SDL_FPoint], count: int, /) -> int: ...
def SDL_RenderDrawLineF(renderer: _Pointer[SDL_Renderer], x1: float, y1: float, x2: float, y2: float, /) -> int: ...
def SDL_RenderDrawLinesF(renderer: _Pointer[SDL_Renderer], points: _Pointer[SDL_FPoint], count: int, /) -> int: ...
def SDL_RenderDrawRectF(renderer: _Pointer[SDL_Renderer], rect: _Pointer[SDL_FRect], /) -> int: ...
def SDL_RenderDrawRectsF(renderer: _Pointer[SDL_Renderer], rects: _Pointer[SDL_FRect], count: int, /) -> int: ...
def SDL_RenderFillRectF(renderer: _Pointer[SDL_Renderer], rect: _Pointer[SDL_FRect], /) -> int: ...
def SDL_RenderFillRectsF(renderer: _Pointer[SDL_Renderer], rects: _Pointer[SDL_FRect], count: int, /) -> int: ...
def SDL_RenderCopyF(
    renderer: _Pointer[SDL_Renderer],
    texture: _Pointer[SDL_Texture],
    srcrect: _Pointer[SDL_Rect],
    dstrect: _Pointer[SDL_FRect],
    /,
) -> int: ...
def SDL_RenderCopyExF(
    renderer: _Pointer[SDL_Renderer],
    texture: _Pointer[SDL_Texture],
    srcrect: _Pointer[SDL_Rect],
    dstrect: _Pointer[SDL_FRect],
    angle: float,
    center: _Pointer[SDL_FPoint],
    flip: int,
    /,
) -> int: ...
def SDL_RenderGeometry(
    renderer: _Pointer[SDL_Renderer],
    texture: _Pointer[SDL_Texture],
    vertices: _Pointer[SDL_Vertex],
    num_vertices: int,
    indices: _Pointer[c_int],
    num_indices: int,
    /,
) -> int: ...
def SDL_RenderGeometryRaw(
    renderer: _Pointer[SDL_Renderer],
    texture: _Pointer[SDL_Texture],
    xy: _Pointer[c_float],
    xy_stride: int,
    color: _Pointer[SDL_Color],
    color_stride: int,
    uv: _Pointer[c_float],
    uv_stride: int,
    num_vertices: int,
    indices: c_void_p | int | None,
    num_indices: int,
    size_indices: int,
    /,
) -> int: ...
def SDL_RenderReadPixels(
    renderer: _Pointer[SDL_Renderer],
    rect: _Pointer[SDL_Rect],
    format: int,
    pixels: c_void_p | int | None,
    pitch: int,
    /,
) -> int: ...
def SDL_RenderPresent(renderer: _Pointer[SDL_Renderer], /) -> None: ...
def SDL_DestroyTexture(texture: _Pointer[SDL_Texture], /) -> None: ...
def SDL_DestroyRenderer(renderer: _Pointer[SDL_Renderer], /) -> None: ...
def SDL_RenderFlush(renderer: _Pointer[SDL_Renderer], /) -> int: ...
def SDL_GL_BindTexture(texture: _Pointer[SDL_Texture], texw: _Pointer[c_float], texh: _Pointer[c_float], /) -> int: ...
def SDL_GL_UnbindTexture(texture: _Pointer[SDL_Texture], /) -> int: ...
def SDL_RenderGetMetalLayer(renderer: _Pointer[SDL_Renderer], /) -> int | None: ...
def SDL_RenderGetMetalCommandEncoder(renderer: _Pointer[SDL_Renderer], /) -> int | None: ...
def SDL_RenderSetVSync(renderer: _Pointer[SDL_Renderer], vsync: int, /) -> int: ...
