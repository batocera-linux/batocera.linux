from ctypes import _Pointer, c_char_p, c_int, c_uint, c_uint64, c_void_p

from .video import SDL_Window

__all__ = [
    'SDL_Vulkan_CreateSurface',
    'SDL_Vulkan_GetDrawableSize',
    'SDL_Vulkan_GetInstanceExtensions',
    'SDL_Vulkan_GetVkGetInstanceProcAddr',
    'SDL_Vulkan_LoadLibrary',
    'SDL_Vulkan_UnloadLibrary',
]

VkInstance = c_void_p
VkSurfaceKHR = c_uint64

def SDL_Vulkan_LoadLibrary(path: bytes | None, /) -> int: ...
def SDL_Vulkan_GetVkGetInstanceProcAddr() -> int | None: ...
def SDL_Vulkan_UnloadLibrary() -> None: ...
def SDL_Vulkan_GetInstanceExtensions(
    window: _Pointer[SDL_Window], pCount: _Pointer[c_uint], pNames: _Pointer[c_char_p], /
) -> int: ...
def SDL_Vulkan_CreateSurface(
    window: _Pointer[SDL_Window], instance: c_void_p | int | None, surface: _Pointer[c_uint64], /
) -> int: ...
def SDL_Vulkan_GetDrawableSize(window: _Pointer[SDL_Window], w: _Pointer[c_int], h: _Pointer[c_int], /) -> None: ...
