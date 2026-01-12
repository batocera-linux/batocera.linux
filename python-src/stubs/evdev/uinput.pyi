from collections.abc import Mapping, Sequence
from typing import Literal, Self, overload

from .device import AbsInfo, InputDevice, _CapabilitiesWithAbsInfo, _VerboseCapabilitiesWithAbsInfo
from .eventio import EventIO
from .ff import UInputErase, UInputUpload

class UInputError(Exception): ...

class UInput(EventIO):
    name: str
    vendor: int
    product: int
    version: int
    bustype: int
    devnode: str
    fd: int
    device: InputDevice

    def __init__(
        self,
        events: Mapping[int, Sequence[int | tuple[int, AbsInfo]]] | None = None,
        name: str = ...,
        vendor: int = ...,
        product: int = ...,
        version: int = ...,
        bustype: int = ...,
        devnode: str = ...,
        phys: str = ...,
        input_props: None = None,
    ) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, type: object, value: object, tb: object) -> None: ...
    def close(self) -> None: ...
    def syn(self) -> None: ...
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
    def begin_upload(self, effect_id: int) -> UInputUpload: ...
    def end_upload(self, upload: UInputUpload) -> None: ...
    def begin_erase(self, effect_id: int) -> UInputErase: ...
    def end_erase(self, erase: UInputErase) -> None: ...
