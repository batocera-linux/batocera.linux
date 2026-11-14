"""QR code rendered straight to a pygame surface (no image library needed)."""

from __future__ import annotations

import pygame
import qrcode
import qrcode.constants


def qr_matrix(text: str, /) -> list[list[bool]]:
    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0)
    code.add_data(text)
    code.make(fit=True)
    return [[bool(cell) for cell in row] for row in code.get_matrix()]


def qr_surface(text: str, size: int, /, *, quiet_zone: int = 2) -> pygame.Surface:
    """Black on white QR code of about ``size`` pixels, with a white quiet zone of ``quiet_zone`` modules."""
    matrix = qr_matrix(text)
    modules = len(matrix) + quiet_zone * 2
    cell = max(1, size // modules)
    surface = pygame.Surface((cell * modules, cell * modules))
    surface.fill((255, 255, 255))
    for y, row in enumerate(matrix):
        for x, dark in enumerate(row):
            if dark:
                surface.fill((0, 0, 0), ((x + quiet_zone) * cell, (y + quiet_zone) * cell, cell, cell))
    return surface
