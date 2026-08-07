__all__ = [
    'SDL_INIT_AUDIO',
    'SDL_INIT_EVENTS',
    'SDL_INIT_EVERYTHING',
    'SDL_INIT_GAMECONTROLLER',
    'SDL_INIT_HAPTIC',
    'SDL_INIT_JOYSTICK',
    'SDL_INIT_NOPARACHUTE',
    'SDL_INIT_SENSOR',
    'SDL_INIT_TIMER',
    'SDL_INIT_VIDEO',
    'SDL_Init',
    'SDL_InitSubSystem',
    'SDL_Quit',
    'SDL_QuitSubSystem',
    'SDL_WasInit',
]

SDL_INIT_TIMER: int
SDL_INIT_AUDIO: int
SDL_INIT_VIDEO: int
SDL_INIT_JOYSTICK: int
SDL_INIT_HAPTIC: int
SDL_INIT_GAMECONTROLLER: int
SDL_INIT_EVENTS: int
SDL_INIT_SENSOR: int
SDL_INIT_NOPARACHUTE: int
SDL_INIT_EVERYTHING: int

def SDL_Init(flags: int, /) -> int: ...
def SDL_InitSubSystem(flags: int, /) -> int: ...
def SDL_QuitSubSystem(flags: int, /) -> None: ...
def SDL_WasInit(flags: int, /) -> int: ...
def SDL_Quit() -> None: ...
