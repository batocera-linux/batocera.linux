from collections.abc import Callable
from typing import Any

__all__ = [
    'ISPYTHON2',
    'ISPYTHON3',
    'ExperimentalWarning',
    'UnsupportedError',
    'byteify',
    'callable',
    'deprecated',
    'deprecation',
    'experimental',
    'isiterable',
    'long',
    'platform_is_64bit',
    'stringify',
    'unichr',
    'unicode',
    'utf8',
]

ISPYTHON2: bool
ISPYTHON3: bool
long = int
unichr = chr
unicode = str

def callable(x: Any) -> bool: ...
def utf8(x: Any) -> str: ...
def stringify(x: Any, enc: str = 'utf-8') -> str: ...
def byteify(x: Any, enc: str = 'utf-8') -> bytes: ...
def isiterable(x: Any) -> bool: ...
def platform_is_64bit() -> bool: ...
def deprecated[F: Callable[..., Any]](func: F) -> F: ...
def deprecation(message: str) -> None: ...

class UnsupportedError(RuntimeError): ...

class ExperimentalWarning(Warning):
    obj: object
    msg: str | None
    def __init__(self, obj: object, msg: str | None = None) -> None: ...

def experimental[F: Callable[..., Any]](func: F) -> F: ...
