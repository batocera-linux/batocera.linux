__all__ = ['clipline', 'cohensutherland', 'liangbarsky', 'point_on_line']

def cohensutherland(
    left: float,
    top: float,
    right: float,
    bottom: float,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> tuple[float, float, float, float] | tuple[None, None, None, None]: ...
def liangbarsky(
    left: float,
    top: float,
    right: float,
    bottom: float,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
) -> tuple[float, float, float, float] | tuple[None, None, None, None]: ...
def clipline(
    l: float,
    t: float,
    r: float,
    b: float,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    method: str = 'liangbarsky',
) -> tuple[float, float, float, float] | tuple[None, None, None, None]: ...
def point_on_line(
    p1: tuple[float, float],
    p2: tuple[float, float],
    point: tuple[float, float],
) -> bool: ...
