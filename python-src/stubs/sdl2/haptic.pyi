from ctypes import Array, Structure, Union, _Pointer, c_void_p

from .joystick import SDL_Joystick
from .stdinc import Sint16, Sint32, Uint16

__all__ = [
    'SDL_HAPTIC_AUTOCENTER',
    'SDL_HAPTIC_CARTESIAN',
    'SDL_HAPTIC_CONSTANT',
    'SDL_HAPTIC_CUSTOM',
    'SDL_HAPTIC_DAMPER',
    'SDL_HAPTIC_FRICTION',
    'SDL_HAPTIC_GAIN',
    'SDL_HAPTIC_INERTIA',
    'SDL_HAPTIC_INFINITY',
    'SDL_HAPTIC_LEFTRIGHT',
    'SDL_HAPTIC_PAUSE',
    'SDL_HAPTIC_POLAR',
    'SDL_HAPTIC_RAMP',
    'SDL_HAPTIC_SAWTOOTHDOWN',
    'SDL_HAPTIC_SAWTOOTHUP',
    'SDL_HAPTIC_SINE',
    'SDL_HAPTIC_SPHERICAL',
    'SDL_HAPTIC_SPRING',
    'SDL_HAPTIC_STATUS',
    'SDL_HAPTIC_STEERING_AXIS',
    'SDL_HAPTIC_TRIANGLE',
    'SDL_Haptic',
    'SDL_HapticClose',
    'SDL_HapticCondition',
    'SDL_HapticConstant',
    'SDL_HapticCustom',
    'SDL_HapticDestroyEffect',
    'SDL_HapticDirection',
    'SDL_HapticEffect',
    'SDL_HapticEffectSupported',
    'SDL_HapticGetEffectStatus',
    'SDL_HapticIndex',
    'SDL_HapticLeftRight',
    'SDL_HapticName',
    'SDL_HapticNewEffect',
    'SDL_HapticNumAxes',
    'SDL_HapticNumEffects',
    'SDL_HapticNumEffectsPlaying',
    'SDL_HapticOpen',
    'SDL_HapticOpenFromJoystick',
    'SDL_HapticOpenFromMouse',
    'SDL_HapticOpened',
    'SDL_HapticPause',
    'SDL_HapticPeriodic',
    'SDL_HapticQuery',
    'SDL_HapticRamp',
    'SDL_HapticRumbleInit',
    'SDL_HapticRumblePlay',
    'SDL_HapticRumbleStop',
    'SDL_HapticRumbleSupported',
    'SDL_HapticRunEffect',
    'SDL_HapticSetAutocenter',
    'SDL_HapticSetGain',
    'SDL_HapticStopAll',
    'SDL_HapticStopEffect',
    'SDL_HapticUnpause',
    'SDL_HapticUpdateEffect',
    'SDL_JoystickIsHaptic',
    'SDL_MouseIsHaptic',
    'SDL_NumHaptics',
]

SDL_HAPTIC_CONSTANT: int
SDL_HAPTIC_SINE: int
SDL_HAPTIC_LEFTRIGHT: int
SDL_HAPTIC_TRIANGLE: int
SDL_HAPTIC_SAWTOOTHUP: int
SDL_HAPTIC_SAWTOOTHDOWN: int
SDL_HAPTIC_RAMP: int
SDL_HAPTIC_SPRING: int
SDL_HAPTIC_DAMPER: int
SDL_HAPTIC_INERTIA: int
SDL_HAPTIC_FRICTION: int
SDL_HAPTIC_CUSTOM: int
SDL_HAPTIC_GAIN: int
SDL_HAPTIC_AUTOCENTER: int
SDL_HAPTIC_STATUS: int
SDL_HAPTIC_PAUSE: int
SDL_HAPTIC_POLAR: int
SDL_HAPTIC_CARTESIAN: int
SDL_HAPTIC_SPHERICAL: int
SDL_HAPTIC_STEERING_AXIS: int
SDL_HAPTIC_INFINITY: int

class SDL_Haptic(c_void_p): ...

class SDL_HapticDirection(Structure):
    type: int
    dir: Array[Sint32]

class SDL_HapticConstant(Structure):
    type: int
    direction: SDL_HapticDirection
    length: int
    delay: int
    button: int
    interval: int
    level: int
    attack_length: int
    attack_level: int
    fade_length: int
    fade_level: int

class SDL_HapticPeriodic(Structure):
    type: int
    direction: SDL_HapticDirection
    length: int
    delay: int
    button: int
    interval: int
    period: int
    magnitude: int
    offset: int
    phase: int
    attack_length: int
    attack_level: int
    fade_length: int
    fade_level: int

class SDL_HapticCondition(Structure):
    type: int
    direction: SDL_HapticDirection
    length: int
    delay: int
    button: int
    interval: int
    right_sat: Array[Uint16]
    left_sat: Array[Uint16]
    right_coeff: Array[Sint16]
    left_coeff: Array[Sint16]
    deadband: Array[Uint16]
    center: Array[Sint16]

class SDL_HapticRamp(Structure):
    type: int
    direction: SDL_HapticDirection
    length: int
    delay: int
    button: int
    interval: int
    start: int
    end: int
    attack_length: int
    attack_level: int
    fade_length: int
    fade_level: int

class SDL_HapticLeftRight(Structure):
    type: int
    length: int
    large_magnitude: int
    small_magnitude: int

class SDL_HapticCustom(Structure):
    type: int
    direction: SDL_HapticDirection
    length: int
    delay: int
    button: int
    interval: int
    channels: int
    period: int
    samples: int
    data: _Pointer[Uint16]
    attack_length: int
    attack_level: int
    fade_length: int
    fade_level: int

class SDL_HapticEffect(Union):
    type: int
    constant: SDL_HapticConstant
    periodic: SDL_HapticPeriodic
    condition: SDL_HapticCondition
    ramp: SDL_HapticRamp
    leftright: SDL_HapticLeftRight
    custom: SDL_HapticCustom

def SDL_NumHaptics() -> int: ...
def SDL_HapticName(device_index: int, /) -> bytes | None: ...
def SDL_HapticOpen(device_index: int, /) -> _Pointer[SDL_Haptic]: ...
def SDL_HapticOpened(device_index: int, /) -> int: ...
def SDL_HapticIndex(haptic: _Pointer[SDL_Haptic], /) -> int: ...
def SDL_MouseIsHaptic() -> int: ...
def SDL_HapticOpenFromMouse() -> _Pointer[SDL_Haptic]: ...
def SDL_JoystickIsHaptic(joystick: _Pointer[SDL_Joystick], /) -> int: ...
def SDL_HapticOpenFromJoystick(joystick: _Pointer[SDL_Joystick], /) -> _Pointer[SDL_Haptic]: ...
def SDL_HapticClose(haptic: _Pointer[SDL_Haptic], /) -> None: ...
def SDL_HapticNumEffects(haptic: _Pointer[SDL_Haptic], /) -> int: ...
def SDL_HapticNumEffectsPlaying(haptic: _Pointer[SDL_Haptic], /) -> int: ...
def SDL_HapticQuery(haptic: _Pointer[SDL_Haptic], /) -> int: ...
def SDL_HapticNumAxes(haptic: _Pointer[SDL_Haptic], /) -> int: ...
def SDL_HapticEffectSupported(haptic: _Pointer[SDL_Haptic], effect: _Pointer[SDL_HapticEffect], /) -> int: ...
def SDL_HapticNewEffect(haptic: _Pointer[SDL_Haptic], effect: _Pointer[SDL_HapticEffect], /) -> int: ...
def SDL_HapticUpdateEffect(haptic: _Pointer[SDL_Haptic], effect: int, data: _Pointer[SDL_HapticEffect], /) -> int: ...
def SDL_HapticRunEffect(haptic: _Pointer[SDL_Haptic], effect: int, iterations: int, /) -> int: ...
def SDL_HapticStopEffect(haptic: _Pointer[SDL_Haptic], effect: int, /) -> int: ...
def SDL_HapticDestroyEffect(haptic: _Pointer[SDL_Haptic], effect: int, /) -> None: ...
def SDL_HapticGetEffectStatus(haptic: _Pointer[SDL_Haptic], effect: int, /) -> int: ...
def SDL_HapticSetGain(haptic: _Pointer[SDL_Haptic], gain: int, /) -> int: ...
def SDL_HapticSetAutocenter(haptic: _Pointer[SDL_Haptic], autocenter: int, /) -> int: ...
def SDL_HapticPause(haptic: _Pointer[SDL_Haptic], /) -> int: ...
def SDL_HapticUnpause(haptic: _Pointer[SDL_Haptic], /) -> int: ...
def SDL_HapticStopAll(haptic: _Pointer[SDL_Haptic], /) -> int: ...
def SDL_HapticRumbleSupported(haptic: _Pointer[SDL_Haptic], /) -> int: ...
def SDL_HapticRumbleInit(haptic: _Pointer[SDL_Haptic], /) -> int: ...
def SDL_HapticRumblePlay(haptic: _Pointer[SDL_Haptic], strength: float, length: int, /) -> int: ...
def SDL_HapticRumbleStop(haptic: _Pointer[SDL_Haptic], /) -> int: ...
