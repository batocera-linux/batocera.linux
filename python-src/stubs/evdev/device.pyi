import contextlib
import os
from collections.abc import Generator
from typing import Literal, NamedTuple, overload

from . import ff
from .eventio_async import EvdevError as EvdevError, EventIO

type _CapabilitiesKeys = Literal[0, 1, 2, 4, 5, 17, 18, 20, 21, 22, 23]
type _CapabilitiesAbsKeys = Literal[3]
type _CapabilitiesVerboseKeys = (
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
    | tuple[Literal['EV_FF_STATUS'], Literal[23]]
)
type _CapabilitiesVerboseAbsKeys = tuple[Literal['EV_ABS'], Literal[3]]

class _Capabilities[KeyT, AbsKeyT, ValueT, AbsValueT](dict[KeyT | AbsKeyT, ValueT | AbsValueT]):
    @overload
    def __getitem__(self, key: AbsKeyT) -> AbsValueT: ...
    @overload
    def __getitem__(self, key: KeyT) -> ValueT: ...
    @overload
    def __getitem__(self, key: KeyT | AbsKeyT) -> AbsValueT | ValueT: ...
    @overload
    def get(self, key: AbsKeyT, default: None = None, /) -> AbsValueT | None: ...
    @overload
    def get(self, key: KeyT, default: None = None, /) -> ValueT | None: ...
    @overload
    def get(self, key: KeyT | AbsKeyT, default: None = None, /) -> AbsValueT | ValueT | None: ...
    @overload
    def get[T](self, key: AbsKeyT, default: AbsValueT | T, /) -> AbsValueT | T: ...
    @overload
    def get[T](self, key: KeyT, default: ValueT | T, /) -> ValueT | T: ...
    @overload
    def get[T](self, key: KeyT | AbsKeyT, default: AbsValueT | ValueT | T, /) -> AbsValueT | ValueT | T: ...  # pyright: ignore[reportIncompatibleMethodOverride]

class _AbsInfoCapabilities(
    _Capabilities[_CapabilitiesKeys, _CapabilitiesAbsKeys, list[int], list[tuple[int, AbsInfo]]]
): ...
class _VerboseAbsInfoCapabilities(
    _Capabilities[
        _CapabilitiesVerboseKeys,
        _CapabilitiesVerboseAbsKeys,
        list[tuple[str, int]],
        list[tuple[tuple[str, int], AbsInfo]],
    ]
): ...

class AbsInfo(NamedTuple):
    value: int
    min: int
    max: int
    fuzz: int
    flat: int
    resolution: int

class KbdInfo(NamedTuple):
    delay: int
    repeat: int

class DeviceInfo(NamedTuple):
    bustype: int
    vendor: int
    product: int
    version: int

class InputDevice[AnyStr: (str, bytes)](EventIO):
    path: AnyStr
    fd: int
    info: DeviceInfo
    name: str
    phys: str
    uniq: str
    version: int
    ff_effects_count: int
    def __init__(self, dev: AnyStr | os.PathLike[AnyStr]) -> None: ...
    def __del__(self) -> None: ...
    @overload
    def capabilities(self, verbose: Literal[False] = ..., absinfo: Literal[True] = ...) -> _AbsInfoCapabilities: ...
    @overload
    def capabilities(self, verbose: Literal[False], absinfo: Literal[False]) -> dict[int, list[int]]: ...
    @overload
    def capabilities(self, verbose: Literal[True], absinfo: Literal[True] = ...) -> _VerboseAbsInfoCapabilities: ...
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
    @overload
    def input_props(self, verbose: Literal[False] = ...) -> list[int]: ...
    @overload
    def input_props(self, verbose: Literal[True]) -> list[tuple[str | tuple[str, ...], int]]: ...
    @overload
    def input_props(self, verbose: bool) -> list[int] | list[tuple[str | tuple[str, ...], int]]: ...
    @overload
    def leds(self, verbose: Literal[False] = ...) -> list[int]: ...
    @overload
    def leds(self, verbose: Literal[True]) -> list[tuple[str | tuple[str, ...], int]]: ...
    @overload
    def leds(self, verbose: bool) -> list[int] | list[tuple[str | tuple[str, ...], int]]: ...
    def set_led(self, led_num: int, value: int) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __fspath__(self) -> AnyStr: ...
    def close(self) -> None: ...
    def grab(self) -> None: ...
    def ungrab(self) -> None: ...
    @contextlib.contextmanager
    def grab_context(self) -> Generator[None]: ...
    def upload_effect(self, effect: ff.Effect) -> int: ...
    def erase_effect(self, ff_id: int) -> None: ...
    @property
    def repeat(self) -> KbdInfo: ...
    @repeat.setter
    def repeat(self, value: tuple[int, int]) -> None: ...
    @overload
    def active_keys(self, verbose: Literal[False] = ...) -> list[int]: ...
    @overload
    def active_keys(self, verbose: Literal[True]) -> list[tuple[str | tuple[str, ...], int]]: ...
    @overload
    def active_keys(self, verbose: bool) -> list[int] | list[tuple[str | tuple[str, ...], int]]: ...
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
