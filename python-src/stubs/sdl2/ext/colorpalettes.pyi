from .color import Color

__all__ = [
    'CGAPALETTE',
    'EGAPALETTE',
    'GRAY2PALETTE',
    'GRAY4PALETTE',
    'MONOPALETTE',
    'RGB3PALETTE',
    'VGAPALETTE',
    'WEBPALETTE',
]

MONOPALETTE: tuple[Color, ...]
GRAY2PALETTE: tuple[Color, ...]
GRAY4PALETTE: tuple[Color, ...]
CGAPALETTE: tuple[Color, ...]
EGAPALETTE: tuple[Color, ...]
WEBPALETTE: tuple[Color, ...]
RGB3PALETTE: tuple[Color, ...]
VGAPALETTE: tuple[Color, ...]
