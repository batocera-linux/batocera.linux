"""Drawing primitives for the overlay: colors, fonts with fallbacks, anti-aliased shapes, icons."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Final

import pygame
import pygame.gfxdraw

from .. import paths
from ..controls import Action, Family

if TYPE_CHECKING:
    from pathlib import Path

type RGB = tuple[int, int, int]
type RGBA = tuple[int, int, int, int]
type Color = RGB | RGBA

BG_TOP: Final[RGB] = (34, 36, 48)
BG_BOTTOM: Final[RGB] = (14, 15, 19)
CARD: Final[RGB] = (37, 40, 50)
CARD_HI: Final[RGB] = (46, 50, 62)
ACCENT: Final[RGB] = (88, 101, 242)  # Discord blurple
ACCENT_HI: Final[RGB] = (121, 132, 255)
TEXT: Final[RGB] = (240, 242, 246)
DIM: Final[RGB] = (150, 157, 172)
FAINT: Final[RGB] = (98, 104, 118)
GREEN: Final[RGB] = (35, 165, 90)
GREEN_HI: Final[RGB] = (67, 214, 128)
RED: Final[RGB] = (237, 66, 69)
WARN: Final[RGB] = (240, 190, 90)
WHITE: Final[RGB] = (255, 255, 255)

PAD: Final = 28  # horizontal margin of the panel

BOLD: Final = 'bold'
REGULAR: Final = 'regular'

_font_cache: dict[tuple[int, str, int], pygame.font.Font] = {}
_text_cache: dict[tuple[str, int, Color, str], pygame.Surface] = {}
_shape_cache: dict[tuple[object, ...], pygame.Surface] = {}
_TEXT_CACHE_MAX: Final = 800


def clear_caches() -> None:
    """Surfaces depend on the display format: drop them when the window is closed."""
    _text_cache.clear()
    _shape_cache.clear()


def _first_existing(candidates: tuple[Path, ...], /) -> str | None:
    return next((str(path) for path in candidates if path.is_file()), None)


def font(size: int, weight: str = REGULAR, fallback: int = 0, /) -> pygame.font.Font:
    """``fallback`` 0 is the UI font, 1 a symbol font, 2 a CJK font."""
    key = (size, weight, fallback)
    if key not in _font_cache:
        if fallback == 1:
            path = _first_existing(paths.FONT_SYMBOLS)
        elif fallback == 2:
            path = _first_existing(paths.FONT_CJK)
        else:
            path = _first_existing(paths.FONT_BOLD if weight == BOLD else paths.FONT_REGULAR)
        _font_cache[key] = pygame.font.Font(path, size)
    return _font_cache[key]


def _fallback_for(char: str, /) -> int:
    code = ord(char)
    if 0x2E80 <= code <= 0x9FFF or 0xF900 <= code <= 0xFAFF or 0xFF00 <= code <= 0xFFEF:
        return 2
    if code >= 0x2190:  # arrows, shapes, dingbats...
        return 1
    return 0


def _render_uncached(text: str, size: int, color: Color, weight: str, /) -> pygame.Surface:
    runs: list[tuple[int, str]] = []
    for char in text:
        index = _fallback_for(char)
        if runs and runs[-1][0] == index:
            runs[-1] = (index, runs[-1][1] + char)
        else:
            runs.append((index, char))
    if len(runs) <= 1:
        return font(size, weight, runs[0][0] if runs else 0).render(text, True, color)
    parts = [font(size, weight, index).render(chunk, True, color) for index, chunk in runs]
    height = max(part.get_height() for part in parts)
    surface = pygame.Surface((sum(part.get_width() for part in parts), height), pygame.SRCALPHA)
    x = 0
    for part in parts:
        surface.blit(part, (x, (height - part.get_height()) // 2))
        x += part.get_width()
    return surface


def render(text: str, size: int, color: Color, weight: str = REGULAR, /) -> pygame.Surface:
    key = (text, size, color, weight)
    if (surface := _text_cache.get(key)) is None:
        if len(_text_cache) > _TEXT_CACHE_MAX:
            _text_cache.clear()
        surface = _text_cache[key] = _render_uncached(text, size, color, weight)
    return surface


def draw_text(
    surface: pygame.Surface,
    text: str,
    pos: tuple[float, float],
    size: int = 24,
    color: Color = TEXT,
    weight: str = REGULAR,
    *,
    max_width: int | None = None,
    anchor: str = 'topleft',
) -> pygame.Rect:
    image = render(text, size, color, weight)
    if max_width is not None and image.get_width() > max_width:
        while len(text) > 1 and image.get_width() > max_width:
            text = text[:-1]
            image = render(text.rstrip() + '…', size, color, weight)
    rect = image.get_rect()
    setattr(rect, anchor, (int(pos[0]), int(pos[1])))
    surface.blit(image, rect)
    return rect


def wrap(text: str, size: int, width: int, weight: str = REGULAR, /) -> list[str]:
    lines: list[str] = []
    line = ''
    for word in text.split():
        candidate = f'{line} {word}'.strip()
        if line and font(size, weight).size(candidate)[0] > width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def rounded(width: int, height: int, radius: int, color: Color, top: RGB | None = None, /) -> pygame.Surface:
    """Anti-aliased rounded rectangle (drawn at 2x then smooth-scaled), optional vertical gradient."""
    key = ('rr', width, height, radius, color, top)
    if (cached := _shape_cache.get(key)) is not None:
        return cached
    big = pygame.Surface((width * 2, height * 2), pygame.SRCALPHA)
    alpha = color[3] if len(color) == 4 else 255
    if top is None:
        pygame.draw.rect(big, color, (0, 0, width * 2, height * 2), border_radius=radius * 2)
    else:
        bottom = color[:3]
        for y in range(height * 2):
            t = y / max(1, height * 2 - 1)
            row = (*(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)), alpha)
            pygame.draw.line(big, row, (0, y), (width * 2, y))
        mask = pygame.Surface((width * 2, height * 2), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, width * 2, height * 2), border_radius=radius * 2)
        big.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surface = _shape_cache[key] = pygame.transform.smoothscale(big, (width, height))
    return surface


def glow(width: int, height: int, radius: int, color: RGB, spread: int = 14, /) -> pygame.Surface:
    key = ('glow', width, height, radius, color, spread)
    if (cached := _shape_cache.get(key)) is not None:
        return cached
    surface = pygame.Surface((width + spread * 2, height + spread * 2), pygame.SRCALPHA)
    for step in range(spread, 0, -2):
        alpha = int(38 * (1 - step / spread) ** 2)
        pygame.draw.rect(
            surface,
            (*color, alpha),
            (spread - step, spread - step, width + step * 2, height + step * 2),
            border_radius=radius + step,
        )
    _shape_cache[key] = surface
    return surface


def circle(surface: pygame.Surface, color: Color, center: tuple[float, float], radius: int, width: int = 0, /) -> None:
    x, y = int(center[0]), int(center[1])
    if width:
        for k in range(width):
            pygame.gfxdraw.aacircle(surface, x, y, radius - k, color)
    else:
        pygame.gfxdraw.aacircle(surface, x, y, radius, color)
        pygame.gfxdraw.filled_circle(surface, x, y, radius, color)


_PALETTE: Final[tuple[RGB, ...]] = (
    (88, 101, 242),
    (235, 69, 158),
    (59, 165, 93),
    (250, 166, 26),
    (237, 66, 69),
    (69, 160, 230),
)


def picture(
    path: Path, size: int, letter: str, /, *, squircle: bool = False, color: RGB | None = None
) -> pygame.Surface:
    """Round avatar (or rounded-square server icon) from a cached image, or a colored initial."""
    exists = path.is_file()
    key = ('pic', str(path), size, squircle, exists)
    if (cached := _shape_cache.get(key)) is not None:
        return cached
    big = size * 2
    source = pygame.Surface((big, big), pygame.SRCALPHA)
    loaded = False
    if exists:
        try:
            source = pygame.transform.smoothscale(pygame.image.load(str(path)).convert_alpha(), (big, big))
            loaded = True
        except pygame.error:
            pass
    if not loaded:
        initial = (letter.strip()[:1] or '?').upper()
        source.fill(color or _PALETTE[sum(map(ord, letter or '?')) % len(_PALETTE)])
        glyph = render(initial, big // 2, TEXT, BOLD)
        source.blit(glyph, glyph.get_rect(center=(big // 2, big // 2)))
    mask = pygame.Surface((big, big), pygame.SRCALPHA)
    if squircle:
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, big, big), border_radius=int(big * 0.3))
    else:
        pygame.draw.circle(mask, (255, 255, 255, 255), (big // 2, big // 2), big // 2)
    source.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    surface = _shape_cache[key] = pygame.transform.smoothscale(source, (size, size))
    return surface


# -- vector icons --
def icon_mic(surface: pygame.Surface, cx: int, cy: int, s: int, color: Color, off: bool = False, /) -> None:
    w, h, lw = int(s * 0.34), int(s * 0.52), max(2, s // 12)
    pygame.draw.rect(surface, color, (cx - w // 2, cy - s // 2, w, h), border_radius=w // 2)
    pygame.draw.arc(
        surface, color, (cx - int(s * 0.33), cy - int(s * 0.3), int(s * 0.66), int(s * 0.58)), math.pi, 2 * math.pi, lw
    )
    pygame.draw.line(surface, color, (cx, cy + int(s * 0.28)), (cx, cy + int(s * 0.44)), lw)
    pygame.draw.line(
        surface, color, (cx - int(s * 0.18), cy + int(s * 0.44)), (cx + int(s * 0.18), cy + int(s * 0.44)), lw
    )
    if off:
        pygame.draw.line(surface, color, (cx - s // 2, cy - s // 2), (cx + s // 2, cy + s // 2), max(3, s // 9))


def icon_headset(surface: pygame.Surface, cx: int, cy: int, s: int, color: Color, off: bool = False, /) -> None:
    pygame.draw.arc(surface, color, (cx - s // 2, cy - s // 2, s, s), 0, math.pi, max(2, s // 10))
    cw, ch = int(s * 0.24), int(s * 0.42)
    pygame.draw.rect(surface, color, (cx - s // 2, cy - 2, cw, ch), border_radius=cw // 2)
    pygame.draw.rect(surface, color, (cx + s // 2 - cw, cy - 2, cw, ch), border_radius=cw // 2)
    if off:
        pygame.draw.line(surface, color, (cx - s // 2, cy - s // 2), (cx + s // 2, cy + s // 2), max(3, s // 9))


def icon_speaker(surface: pygame.Surface, cx: int, cy: int, s: int, color: Color, /) -> None:
    pygame.draw.rect(surface, color, (cx - s // 2, cy - s // 6, s // 4, s // 3))
    pygame.draw.polygon(
        surface,
        color,
        [
            (cx - s // 4, cy - s // 6),
            (cx + s // 10, cy - s // 2 + 2),
            (cx + s // 10, cy + s // 2 - 2),
            (cx - s // 4, cy + s // 6),
        ],
    )
    pygame.draw.arc(surface, color, (cx, cy - s // 3, s // 2, int(s * 0.66)), -1.0, 1.0, max(2, s // 12))


def icon_chevron(surface: pygame.Surface, cx: int, cy: int, s: int, color: Color, /) -> None:
    pygame.draw.lines(
        surface,
        color,
        False,
        [(cx - s // 4, cy - s // 2), (cx + s // 4, cy), (cx - s // 4, cy + s // 2)],
        max(2, s // 6),
    )


def icon_phone(surface: pygame.Surface, cx: int, cy: int, s: int, color: Color, /) -> None:
    pygame.draw.arc(surface, color, (cx - s // 2, cy - s // 2, s, s), math.pi * 0.75, math.pi * 1.75, max(3, s // 6))
    pygame.draw.circle(surface, color, (int(cx - s * 0.36), int(cy - s * 0.3)), max(3, s // 6))
    pygame.draw.circle(surface, color, (int(cx + s * 0.3), int(cy + s * 0.36)), max(3, s // 6))


def icon_cross(surface: pygame.Surface, cx: int, cy: int, s: int, color: Color, /) -> None:
    lw = max(3, s // 7)
    pygame.draw.line(surface, color, (cx - s // 2, cy - s // 2), (cx + s // 2, cy + s // 2), lw)
    pygame.draw.line(surface, color, (cx - s // 2, cy + s // 2), (cx + s // 2, cy - s // 2), lw)


def icon_gear(surface: pygame.Surface, cx: int, cy: int, s: int, color: Color, /) -> None:
    for k in range(8):
        angle = k * math.pi / 4
        pygame.draw.line(
            surface,
            color,
            (cx + math.cos(angle) * s * 0.3, cy + math.sin(angle) * s * 0.3),
            (cx + math.cos(angle) * s * 0.5, cy + math.sin(angle) * s * 0.5),
            max(3, s // 6),
        )
    circle(surface, color, (cx, cy), int(s * 0.34))
    circle(surface, CARD, (cx, cy), int(s * 0.14))


# -- controller button glyphs, per family --
_GLYPHS: Final[dict[Action, dict[Family, tuple[str, RGB | None]]]] = {
    Action.CONFIRM: {
        Family.XBOX: ('A', (35, 165, 90)),
        Family.PLAYSTATION: ('cross', (124, 178, 232)),
        Family.NINTENDO: ('A', None),
    },
    Action.BACK: {
        Family.XBOX: ('B', (218, 55, 60)),
        Family.PLAYSTATION: ('circle', (255, 102, 102)),
        Family.NINTENDO: ('B', None),
    },
    Action.MUTE: {
        Family.XBOX: ('X', (64, 140, 255)),
        Family.PLAYSTATION: ('square', (232, 154, 199)),
        Family.NINTENDO: ('Y', None),
    },
    Action.DEAFEN: {
        Family.XBOX: ('Y', (240, 178, 50)),
        Family.PLAYSTATION: ('triangle', (64, 224, 176)),
        Family.NINTENDO: ('X', None),
    },
}
_SHAPE_NAMES: Final = {'cross': '✕', 'circle': '○', 'square': '□', 'triangle': '△'}
BUMPERS: Final = {Family.XBOX: ('LB', 'RB'), Family.PLAYSTATION: ('L1', 'R1'), Family.NINTENDO: ('L', 'R')}
START_NAMES: Final = {Family.XBOX: 'Menu', Family.PLAYSTATION: 'Options', Family.NINTENDO: '+'}


def button_label(action: Action, family: Family, /) -> str:
    """Short button name for inline help texts (A, ✕, B...)."""
    glyph = _GLYPHS[action][family][0]
    return _SHAPE_NAMES.get(glyph, glyph)


def button(surface: pygame.Surface, cx: int, cy: int, action: Action, family: Family, radius: int = 15, /) -> None:
    glyph, color = _GLYPHS[action][family]
    if family is Family.XBOX and color is not None:
        circle(surface, color, (cx, cy), radius)
        draw_text(surface, glyph, (cx, cy), int(radius * 1.05), WHITE, BOLD, anchor='center')
        return
    circle(surface, (58, 61, 74), (cx, cy), radius)
    circle(surface, (255, 255, 255, 40), (cx, cy), radius, 1)
    if color is None:
        draw_text(surface, glyph, (cx, cy), int(radius * 1.05), (235, 235, 240), BOLD, anchor='center')
        return
    s, lw = int(radius * 0.48), max(2, radius // 6)
    if glyph == 'cross':
        pygame.draw.line(surface, color, (cx - s, cy - s), (cx + s, cy + s), lw + 1)
        pygame.draw.line(surface, color, (cx - s, cy + s), (cx + s, cy - s), lw + 1)
    elif glyph == 'circle':
        circle(surface, color, (cx, cy), s + 1, lw)
    elif glyph == 'square':
        pygame.draw.rect(surface, color, (cx - s, cy - s, s * 2, s * 2), lw)
    else:
        pygame.draw.polygon(surface, color, [(cx, cy - s - 1), (cx + s + 1, cy + s - 1), (cx - s - 1, cy + s - 1)], lw)


def bumper(surface: pygame.Surface, x: int, y: int, label: str, /) -> None:
    surface.blit(rounded(46, 26, 9, (255, 255, 255, 22)), (x, y))
    draw_text(surface, label, (x + 23, y + 13), 15, DIM, BOLD, anchor='center')


def guide_button(surface: pygame.Surface, cx: int, cy: int, family: Family, radius: int = 14, /) -> None:
    circle(surface, (255, 255, 255, 40), (cx, cy), radius)
    if family is Family.PLAYSTATION:
        draw_text(surface, 'PS', (cx, cy), 13, TEXT, BOLD, anchor='center')
    elif family is Family.NINTENDO:
        pygame.draw.polygon(surface, TEXT, [(cx, cy - 7), (cx + 7, cy), (cx - 7, cy)])
        pygame.draw.rect(surface, TEXT, (cx - 5, cy, 10, 7))
    else:
        icon_cross(surface, cx, cy, 10, TEXT)
