from _typeshed import StrOrBytesPath
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import Literal, NamedTuple, overload

from .eventio_async import EventIO

class AbsInfo(NamedTuple):
    value: int
    min: int
    max: int
    fuzz: int
    flat: int
    resolution: int

class KbdInfo(NamedTuple):
    repeat: int
    delay: int

class DeviceInfo(NamedTuple):
    bustype: int
    vendor: int
    product: int
    version: int

class _Capabilities[KT, VT, AKT, AVT](Mapping[KT | AKT, VT | AVT]):
    @overload
    def __getitem__(self, key: AKT, /) -> AVT: ...
    @overload
    def __getitem__(self, key: KT, /) -> VT: ...
    @overload
    def __getitem__(self, key: KT | AKT, /) -> AVT | VT: ...
    @overload
    def get(self, key: AKT, /) -> AVT | None: ...
    @overload
    def get(self, key: KT, /) -> VT | None: ...
    @overload
    def get(self, key: KT | AKT, /) -> AVT | VT | None: ...
    @overload
    def get[T](self, key: AKT, /, default: AVT | T) -> AVT | T: ...
    @overload
    def get[T](self, key: KT, /, default: VT | T) -> VT | T: ...
    @overload
    def get[T](self, key: KT | AKT, /, default: AVT | VT | T) -> AVT | VT | T: ...  # pyright: ignore[reportIncompatibleMethodOverride]

class _CapabilitiesWithAbsInfo(
    _Capabilities[Literal[0, 1, 2, 4, 5, 17, 18, 20, 21, 22, 23], list[int], Literal[3], list[tuple[int, AbsInfo]]]
): ...
class _VerboseCapabilitiesWithAbsInfo(
    _Capabilities[
        tuple[Literal['EV_SYN'], Literal[0]]
        | tuple[Literal['EV_KEY'], Literal[1]]
        | tuple[Literal['EV_REL'], Literal[2]]
        | tuple[Literal['EV_MSC'], Literal[4]]
        | tuple[Literal['EV_SW'], Literal[5]]
        | tuple[Literal['EV_LED'], Literal[17]]
        | tuple[Literal['EV_SND'], Literal[18]]
        | tuple[Literal['EV_REP'], Literal[20]]
        | tuple[Literal['EV_FF'], Literal[21]]
        | tuple[Literal['EV_PWR'], Literal[22]]
        | tuple[Literal['EV_FF_STATUS'], Literal[23]],
        list[tuple[str, int]],
        tuple[Literal['EV_ABS'], Literal[3]],
        list[tuple[tuple[str, int], AbsInfo]],
    ]
): ...

class InputDevice(EventIO):
    path: str | bytes
    fd: int
    info: DeviceInfo
    name: str
    phys: str
    uniq: str
    def __init__(self, dev: StrOrBytesPath) -> None: ...
    def __del__(self) -> None: ...
    @overload
    def capabilities(self, verbose: Literal[False] = ..., absinfo: Literal[True] = ...) -> _CapabilitiesWithAbsInfo: ...
    @overload
    def capabilities(self, verbose: Literal[False], absinfo: Literal[False]) -> dict[int, list[int]]: ...
    @overload
    def capabilities(self, verbose: Literal[True], absinfo: Literal[True] = ...) -> _VerboseCapabilitiesWithAbsInfo: ...
    @overload
    def capabilities(
        self, verbose: Literal[True], absinfo: Literal[False]
    ) -> dict[tuple[str, int], list[tuple[str, int]]]: ...
    @overload
    def input_props(self, verbose: Literal[False] = ...) -> list[int]: ...
    @overload
    def input_props(self, verbose: Literal[True]) -> list[tuple[str, int]]: ...
    @overload
    def input_props(self, verbose: bool) -> list[int] | list[tuple[str, int]]: ...
    @overload
    def leds(self, verbose: Literal[False] = ...) -> list[int]: ...
    @overload
    def leds(self, verbose: Literal[True]) -> list[tuple[str, int]]: ...
    @overload
    def leds(self, verbose: bool) -> list[int] | list[tuple[str, int]]: ...
    def set_led(self, led_num: int, value: int) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __fspath__(self) -> str | bytes: ...
    def close(self) -> None: ...
    def grab(self) -> None: ...
    def ungrab(self) -> None: ...
    @contextmanager
    def grab_context(self) -> Iterator[None]: ...
    def upload_effect(self, effect: object) -> int: ...
    def erase_effect(self, ff_id: int) -> None: ...
    repeat: KbdInfo
    @overload
    def active_keys(self, verbose: Literal[False] = ...) -> list[int]: ...
    @overload
    def active_keys(self, verbose: Literal[True]) -> list[tuple[str, int]]: ...
    @overload
    def active_keys(self, verbose: bool) -> list[int] | list[tuple[str, int]]: ...
    def absinfo(self, axis_num: int) -> AbsInfo: ...
    def set_absinfo(
        self,
        axis_num: int,
        value: int | None = None,
        min: int | None = None,
        max: int | None = None,
        fuzz: int | None = None,
        flat: int | None = None,
        resolution: int | None = None,
    ) -> None: ...
