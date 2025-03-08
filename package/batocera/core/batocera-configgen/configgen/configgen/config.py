from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Literal, overload

from .utils.missing import MISSING, MissingType

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass(slots=True)
class Config:
    TRUE_VALUES: ClassVar[set[Literal['1', 'true', 'on', 'enabled', True]]] = {'1', 'true', 'on', 'enabled', True}
    MISSING: ClassVar = MISSING

    data: dict[str, Any]

    def __len__(self) -> int:
        return len(self.data)

    def __contains__(self, x: object, /) -> bool:
        return x in self.data

    def __getitem__(self, key: str, /) -> Any:
        return self.data[key]

    def __setitem__(self, key: str, value: Any, /) -> None:
        self.data[key] = value

    def __delitem__(self, key: str) -> None:
        del self.data[key]

    def __iter__(self) -> Iterator[Any]:
        return self.data.__iter__()

    @overload
    def get(self, key: str, default: MissingType = ..., /) -> Any | MissingType: ...

    @overload
    def get[T](self, key: str, default: T, /) -> Any | T: ...

    def get[T](self, key: str, default: T | MissingType = MISSING, /) -> Any | T | MissingType:
        return self.data.get(key, default)

    @overload
    def get_bool(self, key: str, default: bool = False, /, *, return_values: None = None) -> bool: ...

    @overload
    def get_bool[T, F](self, key: str, default: bool = False, /, *, return_values: tuple[T, F]) -> T | F: ...

    def get_bool[T, F](
        self, key: str, default: bool = False, /, *, return_values: tuple[T, F] | None = None
    ) -> bool | T | F:
        value = self.data.get(key, MISSING)

        if value is MISSING:
            if return_values is None:
                return default

            return return_values[not default]

        if isinstance(value, str):
            value = value.lower()

        if return_values is None:
            return value in self.TRUE_VALUES

        return return_values[value not in self.TRUE_VALUES]

    @overload
    def get_str(self, key: str, default: MissingType = ..., /) -> str | MissingType: ...

    @overload
    def get_str(self, key: str, default: str, /) -> str: ...

    def get_str(self, key: str, default: str | MissingType = MISSING, /) -> str | MissingType:
        value = self.data.get(key, MISSING)

        if value is MISSING:
            return default

        return str(value)

    @overload
    def get_int(self, key: str, default: MissingType = ..., /) -> int | MissingType: ...

    @overload
    def get_int(self, key: str, default: int, /) -> int: ...

    def get_int(self, key: str, default: int | MissingType = MISSING, /) -> int | MissingType:
        value = self.data.get(key, MISSING)

        if value is MISSING:
            return default

        return int(value)

    @overload
    def get_float(self, key: str, default: MissingType = ..., /) -> float | MissingType: ...

    @overload
    def get_float(self, key: str, default: float, /) -> float: ...

    def get_float(self, key: str, default: float | MissingType = MISSING, /) -> float | MissingType:
        value = self.data.get(key, MISSING)

        if value is MISSING:
            return default

        return float(value)

    def items(self, /, *, starts_with: str | None = None) -> Iterator[tuple[str, Any]]:
        if starts_with is None:
            yield from self.data.items()
        else:
            starts_with_len = len(starts_with)
            for key, value in self.data.items():
                if key.startswith(starts_with):
                    yield key[starts_with_len:], value

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()


@dataclass
class SystemConfig(Config):
    @property
    def emulator(self) -> str:
        return self.data['emulator']

    @property
    def emulator_forced(self) -> bool:
        return self.data['emulator-forced']

    @property
    def core(self) -> str:
        return self.data['core']

    @property
    def core_forced(self) -> bool:
        return self.data['core-forced']

    @property
    def ui_mode(self) -> Literal['Full', 'Kiosk', 'Kid']:
        return self.data['uimode']

    @property
    def show_fps(self) -> bool:
        return self.get_bool('showFPS')

    @property
    def video_mode(self) -> str:
        return self.data.get('videomode', 'default')

    @property
    def use_guns(self) -> bool:
        return self.get_bool('use_guns')

    @property
    def use_wheels(self) -> bool:
        return self.get_bool('use_wheels')
