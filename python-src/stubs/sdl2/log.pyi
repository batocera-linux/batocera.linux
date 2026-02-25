from ctypes import _CFuncPtr, _Pointer, c_int

__all__ = [
    'SDL_LOG_CATEGORY_APPLICATION',
    'SDL_LOG_CATEGORY_ASSERT',
    'SDL_LOG_CATEGORY_AUDIO',
    'SDL_LOG_CATEGORY_CUSTOM',
    'SDL_LOG_CATEGORY_ERROR',
    'SDL_LOG_CATEGORY_INPUT',
    'SDL_LOG_CATEGORY_RENDER',
    'SDL_LOG_CATEGORY_RESERVED1',
    'SDL_LOG_CATEGORY_RESERVED2',
    'SDL_LOG_CATEGORY_RESERVED3',
    'SDL_LOG_CATEGORY_RESERVED4',
    'SDL_LOG_CATEGORY_RESERVED5',
    'SDL_LOG_CATEGORY_RESERVED6',
    'SDL_LOG_CATEGORY_RESERVED7',
    'SDL_LOG_CATEGORY_RESERVED8',
    'SDL_LOG_CATEGORY_RESERVED9',
    'SDL_LOG_CATEGORY_RESERVED10',
    'SDL_LOG_CATEGORY_SYSTEM',
    'SDL_LOG_CATEGORY_TEST',
    'SDL_LOG_CATEGORY_VIDEO',
    'SDL_LOG_PRIORITY_CRITICAL',
    'SDL_LOG_PRIORITY_DEBUG',
    'SDL_LOG_PRIORITY_ERROR',
    'SDL_LOG_PRIORITY_INFO',
    'SDL_LOG_PRIORITY_VERBOSE',
    'SDL_LOG_PRIORITY_WARN',
    'SDL_MAX_LOG_MESSAGE',
    'SDL_NUM_LOG_PRIORITIES',
    'SDL_Log',
    'SDL_LogCategory',
    'SDL_LogCritical',
    'SDL_LogDebug',
    'SDL_LogError',
    'SDL_LogGetOutputFunction',
    'SDL_LogGetPriority',
    'SDL_LogInfo',
    'SDL_LogMessage',
    'SDL_LogOutputFunction',
    'SDL_LogPriority',
    'SDL_LogResetPriorities',
    'SDL_LogSetAllPriority',
    'SDL_LogSetOutputFunction',
    'SDL_LogSetPriority',
    'SDL_LogVerbose',
    'SDL_LogWarn',
]

SDL_MAX_LOG_MESSAGE: int
SDL_LogCategory = c_int
SDL_LOG_CATEGORY_APPLICATION: int
SDL_LOG_CATEGORY_ERROR: int
SDL_LOG_CATEGORY_ASSERT: int
SDL_LOG_CATEGORY_SYSTEM: int
SDL_LOG_CATEGORY_AUDIO: int
SDL_LOG_CATEGORY_VIDEO: int
SDL_LOG_CATEGORY_RENDER: int
SDL_LOG_CATEGORY_INPUT: int
SDL_LOG_CATEGORY_TEST: int
SDL_LOG_CATEGORY_RESERVED1: int
SDL_LOG_CATEGORY_RESERVED2: int
SDL_LOG_CATEGORY_RESERVED3: int
SDL_LOG_CATEGORY_RESERVED4: int
SDL_LOG_CATEGORY_RESERVED5: int
SDL_LOG_CATEGORY_RESERVED6: int
SDL_LOG_CATEGORY_RESERVED7: int
SDL_LOG_CATEGORY_RESERVED8: int
SDL_LOG_CATEGORY_RESERVED9: int
SDL_LOG_CATEGORY_RESERVED10: int
SDL_LOG_CATEGORY_CUSTOM: int
SDL_LogPriority = c_int
SDL_LOG_PRIORITY_VERBOSE: int
SDL_LOG_PRIORITY_DEBUG: int
SDL_LOG_PRIORITY_INFO: int
SDL_LOG_PRIORITY_WARN: int
SDL_LOG_PRIORITY_ERROR: int
SDL_LOG_PRIORITY_CRITICAL: int
SDL_NUM_LOG_PRIORITIES: int
SDL_LogOutputFunction: type[_CFuncPtr]

def SDL_LogSetAllPriority(priority: int, /) -> None: ...
def SDL_LogSetPriority(category: int, priority: int, /) -> None: ...
def SDL_LogGetPriority(category: int, /) -> int: ...
def SDL_LogResetPriorities() -> None: ...
def SDL_Log(fmt: bytes | None, /) -> None: ...
def SDL_LogVerbose(category: int, fmt: bytes | None, /) -> None: ...
def SDL_LogDebug(category: int, fmt: bytes | None, /) -> None: ...
def SDL_LogInfo(category: int, fmt: bytes | None, /) -> None: ...
def SDL_LogWarn(category: int, fmt: bytes | None, /) -> None: ...
def SDL_LogError(category: int, fmt: bytes | None, /) -> None: ...
def SDL_LogCritical(category: int, fmt: bytes | None, /) -> None: ...
def SDL_LogMessage(category: int, priority: int, fmt: bytes | None, /) -> None: ...
def SDL_LogGetOutputFunction(callback: _Pointer[_CFuncPtr], userdata: int | None, /) -> None: ...
def SDL_LogSetOutputFunction(callback: _CFuncPtr, userdata: int | None, /) -> None: ...
