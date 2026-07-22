__all__ = ['SDLError', 'raise_sdl_err']

class SDLError(Exception):
    msg: str | bytes | None
    def __init__(self, msg: str | bytes | None = None) -> None: ...

def raise_sdl_err(desc: str | None = None) -> None: ...
