from ctypes import _Pointer, c_float, c_int, c_void_p

from .stdinc import Sint32, Uint64

__all__ = [
    'SDL_SENSOR_ACCEL',
    'SDL_SENSOR_ACCEL_L',
    'SDL_SENSOR_ACCEL_R',
    'SDL_SENSOR_GYRO',
    'SDL_SENSOR_GYRO_L',
    'SDL_SENSOR_GYRO_R',
    'SDL_SENSOR_INVALID',
    'SDL_SENSOR_UNKNOWN',
    'SDL_STANDARD_GRAVITY',
    'SDL_LockSensors',
    'SDL_NumSensors',
    'SDL_Sensor',
    'SDL_SensorClose',
    'SDL_SensorFromInstanceID',
    'SDL_SensorGetData',
    'SDL_SensorGetDataWithTimestamp',
    'SDL_SensorGetDeviceInstanceID',
    'SDL_SensorGetDeviceName',
    'SDL_SensorGetDeviceNonPortableType',
    'SDL_SensorGetDeviceType',
    'SDL_SensorGetInstanceID',
    'SDL_SensorGetName',
    'SDL_SensorGetNonPortableType',
    'SDL_SensorGetType',
    'SDL_SensorID',
    'SDL_SensorOpen',
    'SDL_SensorType',
    'SDL_SensorUpdate',
    'SDL_UnlockSensors',
]

SDL_SensorType = c_int
SDL_SENSOR_INVALID: int
SDL_SENSOR_UNKNOWN: int
SDL_SENSOR_ACCEL: int
SDL_SENSOR_GYRO: int
SDL_SENSOR_ACCEL_L: int
SDL_SENSOR_GYRO_L: int
SDL_SENSOR_ACCEL_R: int
SDL_SENSOR_GYRO_R: int
SDL_STANDARD_GRAVITY: float
SDL_SensorID = Sint32

class SDL_Sensor(c_void_p): ...

def SDL_LockSensors() -> None: ...
def SDL_UnlockSensors() -> None: ...
def SDL_NumSensors() -> int: ...
def SDL_SensorGetDeviceName(device_index: int, /) -> bytes | None: ...
def SDL_SensorGetDeviceType(device_index: int, /) -> int: ...
def SDL_SensorGetDeviceNonPortableType(device_index: int, /) -> int: ...
def SDL_SensorGetDeviceInstanceID(device_index: int, /) -> int: ...
def SDL_SensorOpen(device_index: int, /) -> _Pointer[SDL_Sensor]: ...
def SDL_SensorFromInstanceID(instance_id: int, /) -> _Pointer[SDL_Sensor]: ...
def SDL_SensorGetName(sensor: _Pointer[SDL_Sensor], /) -> bytes | None: ...
def SDL_SensorGetType(sensor: _Pointer[SDL_Sensor], /) -> int: ...
def SDL_SensorGetNonPortableType(sensor: _Pointer[SDL_Sensor], /) -> int: ...
def SDL_SensorGetInstanceID(sensor: _Pointer[SDL_Sensor], /) -> int: ...
def SDL_SensorGetData(sensor: _Pointer[SDL_Sensor], data: _Pointer[c_float], num_values: int, /) -> int: ...
def SDL_SensorGetDataWithTimestamp(
    sensor: _Pointer[SDL_Sensor],
    timestamp: _Pointer[Uint64],
    data: _Pointer[c_float],
    num_values: int,
    /,
) -> int: ...
def SDL_SensorClose(sensor: _Pointer[SDL_Sensor], /) -> None: ...
def SDL_SensorUpdate() -> None: ...
