from ctypes import Structure, _Pointer, c_ubyte, c_void_p

__all__ = [
    'SDL_hid_ble_scan',
    'SDL_hid_close',
    'SDL_hid_device',
    'SDL_hid_device_change_count',
    'SDL_hid_device_info',
    'SDL_hid_enumerate',
    'SDL_hid_exit',
    'SDL_hid_free_enumeration',
    'SDL_hid_get_feature_report',
    'SDL_hid_get_indexed_string',
    'SDL_hid_get_manufacturer_string',
    'SDL_hid_get_product_string',
    'SDL_hid_get_serial_number_string',
    'SDL_hid_init',
    'SDL_hid_open',
    'SDL_hid_open_path',
    'SDL_hid_read',
    'SDL_hid_read_timeout',
    'SDL_hid_send_feature_report',
    'SDL_hid_set_nonblocking',
    'SDL_hid_write',
]

class SDL_hid_device(c_void_p): ...

class SDL_hid_device_info(Structure):
    path: bytes | None
    vendor_id: int
    product_id: int
    serial_number: str | None
    release_number: int
    manufacturer_string: str | None
    product_string: str | None
    usage_page: int
    usage: int
    interface_number: int
    interface_class: int
    interface_subclass: int
    interface_protocol: int
    next: _Pointer[SDL_hid_device_info]

def SDL_hid_init() -> int: ...
def SDL_hid_exit() -> int: ...
def SDL_hid_device_change_count() -> int: ...
def SDL_hid_enumerate(vendor_id: int, product_id: int, /) -> _Pointer[SDL_hid_device_info]: ...
def SDL_hid_free_enumeration(devs: _Pointer[SDL_hid_device_info], /) -> None: ...
def SDL_hid_open(vendor_id: int, product_id: int, serial_number: str | None, /) -> _Pointer[SDL_hid_device]: ...
def SDL_hid_open_path(path: bytes | None, bExclusive: int, /) -> _Pointer[SDL_hid_device]: ...
def SDL_hid_write(dev: _Pointer[SDL_hid_device], data: _Pointer[c_ubyte], length: int, /) -> int: ...
def SDL_hid_read_timeout(
    dev: _Pointer[SDL_hid_device], data: _Pointer[c_ubyte], length: int, milliseconds: int, /
) -> int: ...
def SDL_hid_read(dev: _Pointer[SDL_hid_device], data: _Pointer[c_ubyte], length: int, /) -> int: ...
def SDL_hid_set_nonblocking(dev: _Pointer[SDL_hid_device], nonblock: int, /) -> int: ...
def SDL_hid_send_feature_report(dev: _Pointer[SDL_hid_device], data: _Pointer[c_ubyte], length: int, /) -> int: ...
def SDL_hid_get_feature_report(dev: _Pointer[SDL_hid_device], data: _Pointer[c_ubyte], length: int, /) -> int: ...
def SDL_hid_close(dev: _Pointer[SDL_hid_device], /) -> None: ...
def SDL_hid_get_manufacturer_string(dev: _Pointer[SDL_hid_device], string: str | None, maxlen: int, /) -> int: ...
def SDL_hid_get_product_string(dev: _Pointer[SDL_hid_device], string: str | None, maxlen: int, /) -> int: ...
def SDL_hid_get_serial_number_string(dev: _Pointer[SDL_hid_device], string: str | None, maxlen: int, /) -> int: ...
def SDL_hid_get_indexed_string(
    dev: _Pointer[SDL_hid_device], string_index: int, string: str | None, maxlen: int, /
) -> int: ...
def SDL_hid_ble_scan(active: int, /) -> None: ...
