# ruff: ignore[missing-required-import]

# NOTE: in order for dbus_fast to properly introspect the annotations
# this file CANNOT use `from __future__ import annotations`

from typing import TYPE_CHECKING, Annotated, Protocol, Self

from dbus_fast import DBusError, Variant
from dbus_fast.annotations import DBusBool, DBusSignature, DBusStr, DBusUInt64
from dbus_fast.service import ServiceInterface, dbus_method

from batocera_common.dataclasses import cached_dataclass

from ..utils import reset_mouse
from .base import Base
from .common import (
    CONFIG_INTERFACE,
    CONTEXT_INTERFACE,
    DBUS_PATH,
    DBUS_SERVICE,
    HOTKEY_INTERFACE,
    MOUSE_INTERFACE,
    DBusContextType,
    DBusDetails,
    DBusDeviceMappingConfig,
    DBusDeviceMappingsType,
    DBusSystemDefaultMappingConfig,
)

if TYPE_CHECKING:
    from types import TracebackType

    from .._types import HotkeysContext, HotkeysContextMapping

DBusKeysDict = Annotated[dict[str, Variant], DBusSignature('a{sv}')]


class ContextBackend(Protocol):
    def set_context(self, context: HotkeysContextMapping, include_common: bool, /) -> None: ...
    def set_default_context(self) -> None: ...
    def get_context(self) -> HotkeysContext: ...
    def get_device_mappings(self) -> dict[tuple[str, str, str, str], tuple[dict[int, str], dict[int, str]]]: ...
    def reload(self) -> None: ...


class ContextInterface(ServiceInterface):
    backend: ContextBackend

    def __init__(self, backend: ContextBackend) -> None:
        self.backend = backend

        super().__init__(CONTEXT_INTERFACE)

    @dbus_method(name='SetContext')
    def set_context(self, name: DBusStr, keys: DBusKeysDict, include_common: DBusBool) -> None:
        python_keys: dict[str, str | list[str]] = {}

        for key, variant in keys.items():
            if variant.signature not in ('s', 'as'):
                raise DBusError(
                    'org.batocera.Hotkeygen.InvalidKeys',
                    f'Invalid variant signature for key {key}: {variant.signature}',
                )

            python_keys[key] = variant.value

        self.backend.set_context({'name': name, 'keys': python_keys}, include_common)

    @dbus_method(name='SetDefaultContext')
    def set_default_context(self) -> None:
        self.backend.set_default_context()

    @dbus_method(name='GetDetails')
    def get_details(self) -> DBusDetails:
        context = self.backend.get_context()
        mappings = self.backend.get_device_mappings()

        dbus_context: DBusContextType = (
            context['name'],
            {
                action: Variant('s' if isinstance(keys, str) else 't' if isinstance(keys, int) else 'at', keys)
                for action, keys in context['keys'].items()
            },
        )
        dbus_mappings: DBusDeviceMappingsType = [
            (device, (mapping, associations)) for device, (mapping, associations) in mappings.items()
        ]

        return (dbus_context, dbus_mappings)

    @dbus_method(name='Reload')
    def reload(self) -> None:
        self.backend.reload()


class MouseInterface(ServiceInterface):
    def __init__(self) -> None:
        super().__init__(MOUSE_INTERFACE)

    @dbus_method(name='Reset')
    async def reset(self) -> None:
        await reset_mouse()


class HotkeyBackend(Protocol):
    async def send_hotkey(self, key: str, delay: int | None, /) -> None: ...


class HotkeyInterface(ServiceInterface):
    backend: HotkeyBackend

    def __init__(self, backend: HotkeyBackend) -> None:
        self.backend = backend

        super().__init__(HOTKEY_INTERFACE)

    @dbus_method(name='Send')
    async def send(self, key: DBusStr, delay: DBusUInt64) -> None:
        await self.backend.send_hotkey(key, delay if delay > 0 else None)


class ConfigBackend(Protocol):
    def get_system_default_mapping_config(self) -> tuple[dict[str, str], dict[str, str]]: ...
    def get_device_mapping_config(self) -> dict[str, dict[str, str]]: ...
    def remove_device_mapping_config(self, filename: str, key: str, /) -> None: ...
    def set_device_mapping_config(self, filename: str, key: str, action: str, /) -> None: ...


class ConfigInterace(ServiceInterface):
    backend: ConfigBackend

    def __init__(self, backend: ConfigBackend) -> None:
        self.backend = backend

        super().__init__(CONFIG_INTERFACE)

    @dbus_method(name='GetSystemDefaultMappingConfig')
    def get_system_default_mapping_config(self) -> DBusSystemDefaultMappingConfig:
        return self.backend.get_system_default_mapping_config()

    @dbus_method(name='GetDeviceMappingConfig')
    def get_device_mapping_config(self) -> DBusDeviceMappingConfig:
        return self.backend.get_device_mapping_config()

    @dbus_method(name='SetDeviceMappingConfig')
    def set_device_mapping_config(self, filename: DBusStr, key: DBusStr, action: DBusStr) -> None:
        self.backend.set_device_mapping_config(filename, key, action)

    @dbus_method(name='RemoveDeviceMappingConfig')
    def remove_device_mapping_config(self, filename: DBusStr, key: DBusStr) -> None:
        self.backend.remove_device_mapping_config(filename, key)


class Backend(ContextBackend, HotkeyBackend, ConfigBackend, Protocol): ...


@cached_dataclass
class Service(Base):
    backend: Backend

    async def __aenter__(self) -> Self:
        result = await super().__aenter__()

        self.bus.export(DBUS_PATH, ContextInterface(self.backend))
        self.bus.export(DBUS_PATH, MouseInterface())
        self.bus.export(DBUS_PATH, HotkeyInterface(self.backend))
        self.bus.export(DBUS_PATH, ConfigInterace(self.backend))

        await self.bus.request_name(DBUS_SERVICE)

        return result

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
        /,
    ) -> None:
        try:
            await self.bus.release_name(DBUS_SERVICE)
        except Exception:
            pass

        return await super().__aexit__(exc_type, exc_value, traceback)
