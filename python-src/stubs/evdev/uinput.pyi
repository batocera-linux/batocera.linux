import ctypes
from _typeshed import StrOrBytesPath
from collections.abc import Iterable, Mapping, Sequence
from typing import Literal, Self, Unpack, overload
from typing_extensions import TypedDict

from . import ff
from .device import AbsInfo, InputDevice, _AbsInfoCapabilities, _VerboseAbsInfoCapabilities
from .eventio_async import EventIO
from .events import InputEvent as InputEvent

class _FromDeviceKwargs(TypedDict, total=False):
    name: str
    vendor: int
    product: int
    version: int
    bustype: int
    devnode: str
    phys: str
    input_props: Iterable[int] | None
    max_effects: int

class UInputError(Exception): ...

class UInput(EventIO):
    @classmethod
    def from_device(
        cls,
        *devices: InputDevice[str] | InputDevice[bytes] | StrOrBytesPath,
        filtered_types: Iterable[int] = ...,
        **kwargs: Unpack[_FromDeviceKwargs],
    ) -> Self: ...
    name: str
    vendor: int
    product: int
    version: int
    bustype: int
    phys: str
    devnode: str
    fd: int
    dll: ctypes.CDLL
    device: InputDevice[str] | None
    def __init__(
        self,
        events: Mapping[int, Iterable[int | tuple[int, AbsInfo | Sequence[int]]]] | None = None,
        name: str = 'py-evdev-uinput',
        vendor: int = 1,
        product: int = 1,
        version: int = 1,
        bustype: int = 3,
        devnode: str = '/dev/uinput',
        phys: str = 'py-evdev-uinput',
        input_props: Iterable[int] | None = None,
        max_effects: int = ...,
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, type: object, value: object, tb: object) -> None: ...
    def close(self) -> None: ...
    @overload
    def capabilities(self, verbose: Literal[False] = False, absinfo: Literal[True] = True) -> _AbsInfoCapabilities: ...
    @overload
    def capabilities(self, verbose: Literal[False], absinfo: Literal[False]) -> dict[int, list[int]]: ...
    @overload
    def capabilities(self, verbose: Literal[True], absinfo: Literal[True] = True) -> _VerboseAbsInfoCapabilities: ...
    @overload
    def capabilities(
        self, verbose: Literal[True], absinfo: Literal[False]
    ) -> dict[tuple[str, int], list[tuple[str, int]]]: ...
    @overload
    def capabilities(
        self, verbose: bool = False, absinfo: bool = True
    ) -> (
        _AbsInfoCapabilities
        | dict[int, list[int]]
        | _VerboseAbsInfoCapabilities
        | dict[tuple[str, int], list[tuple[str, int]]]
    ): ...
    def begin_upload(self, effect_id: int) -> ff.UInputUpload: ...
    def end_upload(self, upload: ff.UInputUpload) -> None: ...
    def begin_erase(self, effect_id: int) -> ff.UInputErase: ...
    def end_erase(self, erase: ff.UInputErase) -> None: ...
