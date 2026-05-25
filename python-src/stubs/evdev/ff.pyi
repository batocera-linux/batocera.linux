import ctypes

class Replay(ctypes.Structure):
    length: int
    delay: int

class Trigger(ctypes.Structure):
    button: int
    interval: int

class Envelope(ctypes.Structure):
    attack_length: int
    attack_level: int
    fade_length: int
    fade_level: int

class Constant(ctypes.Structure):
    level: int
    ff_envelope: Envelope

class Ramp(ctypes.Structure):
    start_level: int
    end_level: int
    ff_envelope: Envelope

class Condition(ctypes.Structure):
    right_saturation: int
    left_saturation: int
    right_coeff: int
    left_coeff: int
    deadband: int
    center: int

class Periodic(ctypes.Structure):
    waveform: int
    period: int
    magnitude: int
    offset: int
    phase: int
    envelope: Envelope
    custom_len: int
    custom_data: ctypes._Pointer[ctypes.c_int16]

class Rumble(ctypes.Structure):
    strong_magnitude: int
    weak_magnitude: int

class EffectType(ctypes.Union):
    ff_constant_effect: Constant
    ff_ramp_effect: Ramp
    ff_periodic_effect: Periodic
    ff_condition_effect: ctypes.Array[Condition]
    ff_rumble_effect: Rumble

class Effect(ctypes.Structure):
    type: int
    id: int
    direction: int
    ff_trigger: Trigger
    ff_replay: Replay
    u: EffectType

class UInputUpload(ctypes.Structure):
    request_id: int
    retval: int
    effect: Effect
    old: Effect

class UInputErase(ctypes.Structure):
    request_id: int
    retval: int
    effect_id: int
