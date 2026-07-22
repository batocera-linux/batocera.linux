from ctypes import Structure, _CFuncPtr, _Pointer, c_int, c_void_p

from .audio import AUDIO_S16SYS, SDL_MIX_MAXVOLUME
from .error import SDL_ClearError, SDL_GetError, SDL_OutOfMemory, SDL_SetError
from .rwops import SDL_RWops
from .stdinc import Uint8, Uint16
from .version import SDL_version

__all__ = [
    'MIX_CHANNELS',
    'MIX_CHANNEL_POST',
    'MIX_DEFAULT_CHANNELS',
    'MIX_DEFAULT_FORMAT',
    'MIX_DEFAULT_FREQUENCY',
    'MIX_EFFECTSMAXSPEED',
    'MIX_FADING_IN',
    'MIX_FADING_OUT',
    'MIX_INIT_FLAC',
    'MIX_INIT_MID',
    'MIX_INIT_MOD',
    'MIX_INIT_MP3',
    'MIX_INIT_OGG',
    'MIX_INIT_OPUS',
    'MIX_INIT_WAVPACK',
    'MIX_MAJOR_VERSION',
    'MIX_MAX_VOLUME',
    'MIX_MINOR_VERSION',
    'MIX_NO_FADING',
    'MIX_PATCHLEVEL',
    'MIX_VERSION',
    'MUS_CMD',
    'MUS_FLAC',
    'MUS_GME',
    'MUS_MID',
    'MUS_MOD',
    'MUS_MODPLUG_UNUSED',
    'MUS_MP3',
    'MUS_MP3_MAD_UNUSED',
    'MUS_NONE',
    'MUS_OGG',
    'MUS_OPUS',
    'MUS_WAV',
    'MUS_WAVPACK',
    'SDL_MIXER_COMPILEDVERSION',
    'SDL_MIXER_MAJOR_VERSION',
    'SDL_MIXER_MINOR_VERSION',
    'SDL_MIXER_PATCHLEVEL',
    'SDL_MIXER_VERSION',
    'SDL_MIXER_VERSION_ATLEAST',
    'MIX_InitFlags',
    'Mix_AllocateChannels',
    'Mix_ChannelFinished',
    'Mix_Chunk',
    'Mix_ClearError',
    'Mix_CloseAudio',
    'Mix_EachSoundFont',
    'Mix_EffectDone_t',
    'Mix_EffectFunc_t',
    'Mix_ExpireChannel',
    'Mix_FadeInChannel',
    'Mix_FadeInChannelTimed',
    'Mix_FadeInMusic',
    'Mix_FadeInMusicPos',
    'Mix_FadeOutChannel',
    'Mix_FadeOutGroup',
    'Mix_FadeOutMusic',
    'Mix_Fading',
    'Mix_FadingChannel',
    'Mix_FadingMusic',
    'Mix_FreeChunk',
    'Mix_FreeMusic',
    'Mix_GetChunk',
    'Mix_GetChunkDecoder',
    'Mix_GetError',
    'Mix_GetMusicAlbumTag',
    'Mix_GetMusicArtistTag',
    'Mix_GetMusicCopyrightTag',
    'Mix_GetMusicDecoder',
    'Mix_GetMusicHookData',
    'Mix_GetMusicLoopEndTime',
    'Mix_GetMusicLoopLengthTime',
    'Mix_GetMusicLoopStartTime',
    'Mix_GetMusicPosition',
    'Mix_GetMusicTitle',
    'Mix_GetMusicTitleTag',
    'Mix_GetMusicType',
    'Mix_GetMusicVolume',
    'Mix_GetNumChunkDecoders',
    'Mix_GetNumMusicDecoders',
    'Mix_GetNumTracks',
    'Mix_GetSoundFonts',
    'Mix_GetSynchroValue',
    'Mix_GetTimidityCfg',
    'Mix_GroupAvailable',
    'Mix_GroupChannel',
    'Mix_GroupChannels',
    'Mix_GroupCount',
    'Mix_GroupNewer',
    'Mix_GroupOldest',
    'Mix_HaltChannel',
    'Mix_HaltGroup',
    'Mix_HaltMusic',
    'Mix_HasChunkDecoder',
    'Mix_HasMusicDecoder',
    'Mix_HookMusic',
    'Mix_HookMusicFinished',
    'Mix_Init',
    'Mix_Linked_Version',
    'Mix_LoadMUS',
    'Mix_LoadMUSType_RW',
    'Mix_LoadMUS_RW',
    'Mix_LoadWAV',
    'Mix_LoadWAV_RW',
    'Mix_MasterVolume',
    'Mix_ModMusicJumpToOrder',
    'Mix_Music',
    'Mix_MusicDuration',
    'Mix_MusicType',
    'Mix_OpenAudio',
    'Mix_OpenAudioDevice',
    'Mix_Pause',
    'Mix_PauseAudio',
    'Mix_PauseMusic',
    'Mix_Paused',
    'Mix_PausedMusic',
    'Mix_PlayChannel',
    'Mix_PlayChannelTimed',
    'Mix_PlayMusic',
    'Mix_Playing',
    'Mix_PlayingMusic',
    'Mix_QuerySpec',
    'Mix_QuickLoad_RAW',
    'Mix_QuickLoad_WAV',
    'Mix_Quit',
    'Mix_RegisterEffect',
    'Mix_ReserveChannels',
    'Mix_Resume',
    'Mix_ResumeMusic',
    'Mix_RewindMusic',
    'Mix_SetDistance',
    'Mix_SetError',
    'Mix_SetMusicCMD',
    'Mix_SetMusicPosition',
    'Mix_SetPanning',
    'Mix_SetPosition',
    'Mix_SetPostMix',
    'Mix_SetReverseStereo',
    'Mix_SetSoundFonts',
    'Mix_SetSynchroValue',
    'Mix_SetTimidityCfg',
    'Mix_StartTrack',
    'Mix_UnregisterAllEffects',
    'Mix_UnregisterEffect',
    'Mix_Volume',
    'Mix_VolumeChunk',
    'Mix_VolumeMusic',
    'channel_finished',
    'get_dll_file',
    'mix_func',
    'music_finished',
    'soundfont_function',
]

def get_dll_file() -> str: ...

SDL_MIXER_MAJOR_VERSION: int
SDL_MIXER_MINOR_VERSION: int
SDL_MIXER_PATCHLEVEL: int

def SDL_MIXER_VERSION(x: object, /) -> None: ...

MIX_MAJOR_VERSION = SDL_MIXER_MAJOR_VERSION
MIX_MINOR_VERSION = SDL_MIXER_MINOR_VERSION
MIX_PATCHLEVEL = SDL_MIXER_PATCHLEVEL
MIX_VERSION = SDL_MIXER_VERSION
SDL_MIXER_COMPILEDVERSION: int

def SDL_MIXER_VERSION_ATLEAST(x: int, y: int, z: int, /) -> bool: ...

MIX_InitFlags = c_int
MIX_INIT_FLAC: int
MIX_INIT_MOD: int
MIX_INIT_MP3: int
MIX_INIT_OGG: int
MIX_INIT_MID: int
MIX_INIT_OPUS: int
MIX_INIT_WAVPACK: int
Mix_Fading = c_int
MIX_NO_FADING: int
MIX_FADING_OUT: int
MIX_FADING_IN: int
Mix_MusicType = c_int
MUS_NONE: int
MUS_CMD: int
MUS_WAV: int
MUS_MOD: int
MUS_MID: int
MUS_OGG: int
MUS_MP3: int
MUS_MP3_MAD_UNUSED: int
MUS_FLAC: int
MUS_MODPLUG_UNUSED: int
MUS_OPUS: int
MUS_WAVPACK: int
MUS_GME: int
MIX_CHANNELS: int
MIX_DEFAULT_FREQUENCY: int
MIX_DEFAULT_FORMAT = AUDIO_S16SYS
MIX_DEFAULT_CHANNELS: int
MIX_MAX_VOLUME = SDL_MIX_MAXVOLUME
MIX_CHANNEL_POST: int
MIX_EFFECTSMAXSPEED: str

class Mix_Chunk(Structure):
    allocated: int
    abuf: _Pointer[Uint8]
    alen: int
    volume: int

class Mix_Music(c_void_p): ...

mix_func: type[_CFuncPtr]
music_finished: type[_CFuncPtr]
channel_finished: type[_CFuncPtr]
Mix_EffectFunc_t: type[_CFuncPtr]
Mix_EffectDone_t: type[_CFuncPtr]
soundfont_function: type[_CFuncPtr]

def Mix_Linked_Version() -> _Pointer[SDL_version]: ...
def Mix_Init(flags: int, /) -> int: ...
def Mix_Quit() -> None: ...
def Mix_OpenAudio(frequency: int, format: int, channels: int, chunksize: int, /) -> int: ...
def Mix_OpenAudioDevice(
    frequency: int,
    format: int,
    channels: int,
    chunksize: int,
    device: bytes | None,
    allowed_changes: int,
    /,
) -> int: ...
def Mix_PauseAudio(pause_on: int, /) -> None: ...
def Mix_AllocateChannels(numchans: int, /) -> int: ...
def Mix_QuerySpec(frequency: _Pointer[c_int], format: _Pointer[Uint16], channels: _Pointer[c_int], /) -> int: ...
def Mix_LoadWAV_RW(src: _Pointer[SDL_RWops], freesrc: int, /) -> _Pointer[Mix_Chunk]: ...
def Mix_LoadWAV(file: bytes | None, /) -> _Pointer[Mix_Chunk]: ...
def Mix_LoadMUS(file: bytes | None, /) -> _Pointer[Mix_Music]: ...
def Mix_LoadMUS_RW(src: _Pointer[SDL_RWops], freesrc: int, /) -> _Pointer[Mix_Music]: ...
def Mix_LoadMUSType_RW(src: _Pointer[SDL_RWops], type: int, freesrc: int, /) -> _Pointer[Mix_Music]: ...
def Mix_QuickLoad_WAV(mem: _Pointer[Uint8], /) -> _Pointer[Mix_Chunk]: ...
def Mix_QuickLoad_RAW(mem: _Pointer[Uint8], len: int, /) -> _Pointer[Mix_Chunk]: ...
def Mix_FreeChunk(chunk: _Pointer[Mix_Chunk], /) -> None: ...
def Mix_FreeMusic(music: _Pointer[Mix_Music], /) -> None: ...
def Mix_GetNumChunkDecoders() -> int: ...
def Mix_GetChunkDecoder(index: int, /) -> bytes | None: ...
def Mix_HasChunkDecoder(name: bytes | None, /) -> int: ...
def Mix_GetNumMusicDecoders() -> int: ...
def Mix_GetMusicDecoder(index: int, /) -> bytes | None: ...
def Mix_HasMusicDecoder(name: bytes | None, /) -> int: ...
def Mix_GetMusicType(music: _Pointer[Mix_Music], /) -> int: ...
def Mix_GetMusicTitle(music: _Pointer[Mix_Music], /) -> bytes | None: ...
def Mix_GetMusicTitleTag(music: _Pointer[Mix_Music], /) -> bytes | None: ...
def Mix_GetMusicArtistTag(music: _Pointer[Mix_Music], /) -> bytes | None: ...
def Mix_GetMusicAlbumTag(music: _Pointer[Mix_Music], /) -> bytes | None: ...
def Mix_GetMusicCopyrightTag(music: _Pointer[Mix_Music], /) -> bytes | None: ...
def Mix_SetPostMix(mix_func: _CFuncPtr, arg: int | None, /) -> None: ...
def Mix_HookMusic(mix_func: _CFuncPtr, arg: int | None, /) -> None: ...
def Mix_HookMusicFinished(music_finished: _CFuncPtr, /) -> None: ...
def Mix_GetMusicHookData() -> int | None: ...
def Mix_ChannelFinished(channel_finished: _CFuncPtr, /) -> None: ...
def Mix_RegisterEffect(chan: int, f: _CFuncPtr, d: _CFuncPtr, arg: int | None, /) -> int: ...
def Mix_UnregisterEffect(channel: int, f: _CFuncPtr, /) -> int: ...
def Mix_UnregisterAllEffects(channel: int, /) -> None: ...
def Mix_SetPanning(channel: int, left: int, right: int, /) -> int: ...
def Mix_SetPosition(channel: int, angle: int, distance: int, /) -> int: ...
def Mix_SetDistance(channel: int, distance: int, /) -> None: ...
def Mix_SetReverseStereo(channel: int, flip: int, /) -> int: ...
def Mix_ReserveChannels(num: int, /) -> int: ...
def Mix_GroupChannel(which: int, tag: int, /) -> int: ...
def Mix_GroupChannels(from_: int, to: int, tag: int, /) -> int: ...
def Mix_GroupAvailable(tag: int, /) -> int: ...
def Mix_GroupCount(tag: int, /) -> int: ...
def Mix_GroupOldest(tag: int, /) -> int: ...
def Mix_GroupNewer(tag: int, /) -> int: ...
def Mix_PlayChannel(channel: int, chunk: _Pointer[Mix_Chunk], loops: int, /) -> int: ...
def Mix_PlayChannelTimed(channel: int, chunk: _Pointer[Mix_Chunk], loops: int, ticks: int, /) -> int: ...
def Mix_PlayMusic(music: _Pointer[Mix_Music], loops: int, /) -> int: ...
def Mix_FadeInMusic(music: _Pointer[Mix_Music], loops: int, ms: int, /) -> int: ...
def Mix_FadeInMusicPos(music: _Pointer[Mix_Music], loops: int, ms: int, position: float, /) -> int: ...
def Mix_FadeInChannel(channel: int, chunk: _Pointer[Mix_Chunk], loops: int, ms: int, /) -> int: ...
def Mix_FadeInChannelTimed(channel: int, chunk: _Pointer[Mix_Chunk], loops: int, ms: int, ticks: int, /) -> int: ...
def Mix_Volume(channel: int, volume: int, /) -> int: ...
def Mix_VolumeChunk(chunk: _Pointer[Mix_Chunk], volume: int, /) -> int: ...
def Mix_VolumeMusic(volume: int, /) -> int: ...
def Mix_GetMusicVolume(music: _Pointer[Mix_Music], /) -> int: ...
def Mix_MasterVolume(volume: int, /) -> int: ...
def Mix_HaltChannel(channel: int, /) -> int: ...
def Mix_HaltGroup(tag: int, /) -> int: ...
def Mix_HaltMusic() -> int: ...
def Mix_ExpireChannel(channel: int, ticks: int, /) -> int: ...
def Mix_FadeOutChannel(which: int, ms: int, /) -> int: ...
def Mix_FadeOutGroup(tag: int, ms: int, /) -> int: ...
def Mix_FadeOutMusic(ms: int, /) -> int: ...
def Mix_FadingMusic() -> int: ...
def Mix_FadingChannel(which: int, /) -> int: ...
def Mix_Pause(channel: int, /) -> None: ...
def Mix_Resume(channel: int, /) -> None: ...
def Mix_Paused(channel: int, /) -> int: ...
def Mix_PauseMusic() -> None: ...
def Mix_ResumeMusic() -> None: ...
def Mix_RewindMusic() -> None: ...
def Mix_PausedMusic() -> int: ...
def Mix_ModMusicJumpToOrder(order: int, /) -> int: ...
def Mix_StartTrack(music: _Pointer[Mix_Music], track: int, /) -> int: ...
def Mix_GetNumTracks(music: _Pointer[Mix_Music], /) -> int: ...
def Mix_SetMusicPosition(position: float, /) -> int: ...
def Mix_GetMusicPosition(music: _Pointer[Mix_Music], /) -> float: ...
def Mix_MusicDuration(music: _Pointer[Mix_Music], /) -> float: ...
def Mix_GetMusicLoopStartTime(music: _Pointer[Mix_Music], /) -> float: ...
def Mix_GetMusicLoopEndTime(music: _Pointer[Mix_Music], /) -> float: ...
def Mix_GetMusicLoopLengthTime(music: _Pointer[Mix_Music], /) -> float: ...
def Mix_Playing(channel: int, /) -> int: ...
def Mix_PlayingMusic() -> int: ...
def Mix_SetMusicCMD(command: bytes | None, /) -> int: ...
def Mix_SetSynchroValue(value: int, /) -> int: ...
def Mix_GetSynchroValue() -> int: ...
def Mix_SetSoundFonts(paths: bytes | None, /) -> int: ...
def Mix_GetSoundFonts() -> bytes | None: ...
def Mix_EachSoundFont(function: _CFuncPtr, data: int | None, /) -> int: ...
def Mix_SetTimidityCfg(path: bytes | None, /) -> int: ...
def Mix_GetTimidityCfg() -> bytes | None: ...
def Mix_GetChunk(channel: int, /) -> _Pointer[Mix_Chunk]: ...
def Mix_CloseAudio() -> None: ...

Mix_SetError = SDL_SetError
Mix_GetError = SDL_GetError
Mix_ClearError = SDL_ClearError
Mix_OutOfMemory = SDL_OutOfMemory
