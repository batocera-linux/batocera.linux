from ctypes import Structure

__all__ = ['SDL_GetPreferredLocales', 'SDL_Locale']

class SDL_Locale(Structure):
    language: bytes | None
    country: bytes | None

def SDL_GetPreferredLocales() -> list[SDL_Locale]: ...
