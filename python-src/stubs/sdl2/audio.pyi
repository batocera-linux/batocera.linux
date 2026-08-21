from ctypes import Array, Structure, _CFuncPtr, _Pointer, c_char_p, c_int, c_void_p

from .rwops import SDL_RWops
from .stdinc import Uint8, Uint16, Uint32

__all__ = [
    'AUDIO_F32',
    'AUDIO_F32LSB',
    'AUDIO_F32MSB',
    'AUDIO_F32SYS',
    'AUDIO_FORMATS',
    'AUDIO_S8',
    'AUDIO_S16',
    'AUDIO_S16LSB',
    'AUDIO_S16MSB',
    'AUDIO_S16SYS',
    'AUDIO_S32',
    'AUDIO_S32LSB',
    'AUDIO_S32MSB',
    'AUDIO_S32SYS',
    'AUDIO_U8',
    'AUDIO_U16',
    'AUDIO_U16LSB',
    'AUDIO_U16MSB',
    'AUDIO_U16SYS',
    'SDL_AUDIOCVT_MAX_FILTERS',
    'SDL_AUDIO_ALLOW_ANY_CHANGE',
    'SDL_AUDIO_ALLOW_CHANNELS_CHANGE',
    'SDL_AUDIO_ALLOW_FORMAT_CHANGE',
    'SDL_AUDIO_ALLOW_FREQUENCY_CHANGE',
    'SDL_AUDIO_ALLOW_SAMPLES_CHANGE',
    'SDL_AUDIO_BITSIZE',
    'SDL_AUDIO_ISBIGENDIAN',
    'SDL_AUDIO_ISFLOAT',
    'SDL_AUDIO_ISINT',
    'SDL_AUDIO_ISLITTLEENDIAN',
    'SDL_AUDIO_ISSIGNED',
    'SDL_AUDIO_ISUNSIGNED',
    'SDL_AUDIO_MASK_BITSIZE',
    'SDL_AUDIO_MASK_DATATYPE',
    'SDL_AUDIO_MASK_ENDIAN',
    'SDL_AUDIO_MASK_SIGNED',
    'SDL_AUDIO_PAUSED',
    'SDL_AUDIO_PLAYING',
    'SDL_AUDIO_STOPPED',
    'SDL_MIX_MAXVOLUME',
    'SDL_AudioCVT',
    'SDL_AudioCallback',
    'SDL_AudioFilter',
    'SDL_AudioFormat',
    'SDL_AudioInit',
    'SDL_AudioQuit',
    'SDL_AudioSpec',
    'SDL_AudioStatus',
    'SDL_AudioStreamAvailable',
    'SDL_AudioStreamClear',
    'SDL_AudioStreamGet',
    'SDL_AudioStreamPut',
    'SDL_BuildAudioCVT',
    'SDL_ClearQueuedAudio',
    'SDL_CloseAudio',
    'SDL_CloseAudioDevice',
    'SDL_ConvertAudio',
    'SDL_DequeueAudio',
    'SDL_FreeAudioStream',
    'SDL_FreeWAV',
    'SDL_GetAudioDeviceName',
    'SDL_GetAudioDeviceSpec',
    'SDL_GetAudioDeviceStatus',
    'SDL_GetAudioDriver',
    'SDL_GetAudioStatus',
    'SDL_GetCurrentAudioDriver',
    'SDL_GetDefaultAudioInfo',
    'SDL_GetNumAudioDevices',
    'SDL_GetNumAudioDrivers',
    'SDL_GetQueuedAudioSize',
    'SDL_LoadWAV',
    'SDL_LoadWAV_RW',
    'SDL_LockAudio',
    'SDL_LockAudioDevice',
    'SDL_MixAudio',
    'SDL_MixAudioFormat',
    'SDL_NewAudioStream',
    'SDL_OpenAudio',
    'SDL_OpenAudioDevice',
    'SDL_PauseAudio',
    'SDL_PauseAudioDevice',
    'SDL_QueueAudio',
    'SDL_UnlockAudio',
    'SDL_UnlockAudioDevice',
]

SDL_AUDIO_MASK_BITSIZE: int
SDL_AUDIO_MASK_DATATYPE: int
SDL_AUDIO_MASK_ENDIAN: int
SDL_AUDIO_MASK_SIGNED: int

def SDL_AUDIO_BITSIZE(x: int, /) -> int: ...
def SDL_AUDIO_ISFLOAT(x: int, /) -> int: ...
def SDL_AUDIO_ISBIGENDIAN(x: int, /) -> int: ...
def SDL_AUDIO_ISSIGNED(x: int, /) -> int: ...
def SDL_AUDIO_ISINT(x: int, /) -> bool: ...
def SDL_AUDIO_ISLITTLEENDIAN(x: int, /) -> bool: ...
def SDL_AUDIO_ISUNSIGNED(x: int, /) -> bool: ...

AUDIO_U8: int
AUDIO_S8: int
AUDIO_U16LSB: int
AUDIO_S16LSB: int
AUDIO_U16MSB: int
AUDIO_S16MSB: int
AUDIO_U16 = AUDIO_U16LSB
AUDIO_S16 = AUDIO_S16LSB
AUDIO_S32LSB: int
AUDIO_S32MSB: int
AUDIO_S32 = AUDIO_S32LSB
AUDIO_F32LSB: int
AUDIO_F32MSB: int
AUDIO_F32 = AUDIO_F32LSB
AUDIO_FORMATS: set[int]
AUDIO_U16SYS: int
AUDIO_S16SYS: int
AUDIO_S32SYS: int
AUDIO_F32SYS: int
SDL_AUDIO_ALLOW_FREQUENCY_CHANGE: int
SDL_AUDIO_ALLOW_FORMAT_CHANGE: int
SDL_AUDIO_ALLOW_CHANNELS_CHANGE: int
SDL_AUDIO_ALLOW_SAMPLES_CHANGE: int
SDL_AUDIO_ALLOW_ANY_CHANGE: int
SDL_AudioStatus = c_int
SDL_AUDIO_STOPPED: int
SDL_AUDIO_PLAYING: int
SDL_AUDIO_PAUSED: int
SDL_MIX_MAXVOLUME: int
SDL_AUDIOCVT_MAX_FILTERS: int
SDL_AudioFormat = Uint16
SDL_AudioDeviceID = Uint32
SDL_AudioCallback: type[_CFuncPtr]

class SDL_AudioSpec(Structure):
    freq: int
    format: int
    channels: int
    silence: int
    samples: int
    padding: int
    size: int
    callback: _CFuncPtr
    userdata: int | None
    def __init__(
        self,
        freq: int,
        aformat: int,
        channels: int,
        samples: int,
        callback: _CFuncPtr = ...,
        userdata: int | None = ...,
    ) -> None: ...

class SDL_AudioCVT(Structure):
    needed: int
    src_format: int
    dst_format: int
    rate_incr: float
    buf: _Pointer[Uint8]
    len: int
    len_cvt: int
    len_mult: int
    len_ratio: float
    filters: Array[_CFuncPtr]
    filter_index: int

SDL_AudioFilter: type[_CFuncPtr]

class SDL_AudioStream(c_void_p): ...

def SDL_GetNumAudioDrivers() -> int: ...
def SDL_GetAudioDriver(index: int, /) -> bytes | None: ...
def SDL_AudioInit(driver_name: bytes | None, /) -> int: ...
def SDL_AudioQuit() -> None: ...
def SDL_GetCurrentAudioDriver() -> bytes | None: ...
def SDL_OpenAudio(desired: _Pointer[SDL_AudioSpec], obtained: _Pointer[SDL_AudioSpec], /) -> int: ...
def SDL_GetNumAudioDevices(iscapture: int, /) -> int: ...
def SDL_GetAudioDeviceName(index: int, iscapture: int, /) -> bytes | None: ...
def SDL_GetAudioDeviceSpec(index: int, iscapture: int, spec: _Pointer[SDL_AudioSpec], /) -> int: ...
def SDL_GetDefaultAudioInfo(name: _Pointer[c_char_p], spec: _Pointer[SDL_AudioSpec], iscapture: int, /) -> int: ...
def SDL_OpenAudioDevice(
    device: bytes | None,
    iscapture: int,
    desired: _Pointer[SDL_AudioSpec],
    obtained: _Pointer[SDL_AudioSpec],
    allowed_changes: int,
    /,
) -> int: ...
def SDL_GetAudioStatus() -> int: ...
def SDL_GetAudioDeviceStatus(dev: int, /) -> int: ...
def SDL_PauseAudio(pause_on: int, /) -> None: ...
def SDL_PauseAudioDevice(dev: int, pause_on: int, /) -> None: ...
def SDL_LoadWAV_RW(
    src: _Pointer[SDL_RWops],
    freesrc: int,
    spec: _Pointer[SDL_AudioSpec],
    audio_buf: _Pointer[_Pointer[Uint8]],
    audio_len: _Pointer[Uint32],
    /,
) -> _Pointer[SDL_AudioSpec]: ...
def SDL_LoadWAV(
    file: bytes | None,
    spec: _Pointer[SDL_AudioSpec],
    audio_buf: _Pointer[_Pointer[Uint8]],
    audio_len: _Pointer[Uint32],
    /,
) -> _Pointer[SDL_AudioSpec]: ...
def SDL_FreeWAV(audio_buf: _Pointer[Uint8], /) -> None: ...
def SDL_BuildAudioCVT(
    cvt: _Pointer[SDL_AudioCVT],
    src_format: int,
    src_channels: int,
    src_rate: int,
    dst_format: int,
    dst_channels: int,
    dst_rate: int,
    /,
) -> int: ...
def SDL_ConvertAudio(cvt: _Pointer[SDL_AudioCVT], /) -> int: ...
def SDL_MixAudio(dst: _Pointer[Uint8], src: _Pointer[Uint8], length: int, volume: int, /) -> None: ...
def SDL_MixAudioFormat(
    dst: _Pointer[Uint8], src: _Pointer[Uint8], format: int, length: int, volume: int, /
) -> None: ...
def SDL_LockAudio() -> None: ...
def SDL_LockAudioDevice(dev: int, /) -> None: ...
def SDL_UnlockAudio() -> None: ...
def SDL_UnlockAudioDevice(dev: int, /) -> None: ...
def SDL_CloseAudio() -> None: ...
def SDL_CloseAudioDevice(dev: int, /) -> None: ...
def SDL_QueueAudio(dev: int, data: c_void_p | int | None, length: int, /) -> int: ...
def SDL_DequeueAudio(dev: int, data: c_void_p | int | None, length: int, /) -> int: ...
def SDL_GetQueuedAudioSize(dev: int, /) -> int: ...
def SDL_ClearQueuedAudio(dev: int, /) -> None: ...
def SDL_NewAudioStream(
    src_format: int,
    src_channels: int,
    src_rate: int,
    dst_format: int,
    dst_channels: int,
    dst_rate: int,
    /,
) -> _Pointer[SDL_AudioStream]: ...
def SDL_AudioStreamPut(stream: _Pointer[SDL_AudioStream], buf: c_void_p | int | None, length: int, /) -> int: ...
def SDL_AudioStreamGet(stream: _Pointer[SDL_AudioStream], buf: c_void_p | int | None, length: int, /) -> int: ...
def SDL_AudioStreamAvailable(stream: _Pointer[SDL_AudioStream], /) -> int: ...
def SDL_AudioStreamClear(stream: _Pointer[SDL_AudioStream], /) -> None: ...
def SDL_FreeAudioStream(stream: _Pointer[SDL_AudioStream], /) -> None: ...
