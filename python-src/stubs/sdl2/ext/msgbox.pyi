from collections.abc import Iterable, Sequence

from sdl2.video import SDL_Window

from .color import Color
from .window import Window

__all__ = ['MessageBox', 'MessageBoxTheme', 'show_alert', 'show_messagebox']

type _ColorLike = Color | tuple[int, int, int] | Iterable[int]

class MessageBoxTheme:
    def __init__(
        self,
        bg: _ColorLike | None = None,
        text: _ColorLike | None = None,
        btn: _ColorLike | None = None,
        btn_border: _ColorLike | None = None,
        btn_selected: _ColorLike | None = None,
    ) -> None: ...

class MessageBox:
    def __init__(
        self,
        title: str,
        msg: str,
        buttons: Sequence[str],
        default: str | None = None,
        msgtype: str | None = None,
        theme: MessageBoxTheme | None = None,
    ) -> None: ...

def show_messagebox(
    msgbox: MessageBox,
    window: Window | SDL_Window | None = None,
) -> str: ...
def show_alert(
    title: str,
    msg: str,
    msgtype: str | None = None,
    window: Window | SDL_Window | None = None,
) -> None: ...
