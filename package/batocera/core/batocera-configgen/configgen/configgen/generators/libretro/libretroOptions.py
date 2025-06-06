from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ... import controllersConfig
from ...batoceraPaths import BIOS, ROMS, ensure_parents_and_open
from ...gun import Guns, guns_need_crosses
from ...utils import videoMode
from ...utils.configparser import CaseSensitiveConfigParser

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from ...Emulator import Emulator
    from ...settings.unixSettings import UnixSettings
    from ...types import DeviceInfoMapping


def _set(settings: UnixSettings, settings_name: str, value: Any) -> None:
    settings.save(settings_name, '' if value is None else f'"{value}"')


def _set_from_system(settings: UnixSettings, settings_name: str, system: Emulator, option_name: str | None = None, *, default: Any = '') -> None:
    _set(settings, settings_name, system.config.get(option_name or settings_name, default))


def _set_from_system_bool(settings: UnixSettings, settings_name: str, system: Emulator, option_name: str | None = None, *, default: bool = False, values: tuple[Any, Any]) -> None:
    _set(settings, settings_name, system.config.get_bool(option_name or settings_name, default, return_values=values))


# Amstrad CPC / GX4000
def _cap32_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Virtual Keyboard by default (select+start) change to (start+Y)
    _set(coreSettings, 'cap32_combokey', 'y')
    # Auto Select Model
    if system.name == 'gx4000':
        _set(coreSettings, 'cap32_model', '6128+ (experimental)')
    else:
        _set_from_system(coreSettings, 'cap32_model', system, default='6128')

    # Ram size
    _set_from_system(coreSettings, 'cap32_ram', system, default="128")

    # colour depth
    _set_from_system(coreSettings, 'cap32_gfx_colors', system, "cap32_colour", default="24bit")

    # language
    _set_from_system(coreSettings, 'cap32_lang_layout', system, "cap32_language", default="english")


# Atari 800 and 5200
def _atari800_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    if system.name == 'atari800':
        # Select Atari 800
        # Let user overide Atari System
        _set_from_system(coreSettings, 'atari800_system', system, default="800XL (64K)")

        # Video Standard
        _set_from_system(coreSettings, 'atari800_ntscpal', system, default="NTSC")

        # SIO Acceleration
        _set_from_system(coreSettings, 'atari800_sioaccel', system, default="enabled")

        # Hi-Res Artifacting
        _set_from_system(coreSettings, 'atari800_artifacting', system, default="disabled")

        # Internal resolution
        _set_from_system(coreSettings, 'atari800_resolution', system) # Default : 336x240

        # Internal BASIC interpreter
        _set_from_system(coreSettings, 'atari800_internalbasic', system, default="disabled")

        # WARNING: Now we must stop to use "atari800.cfg" because core options crush them

    else:
        # Select Atari 5200
        _set(coreSettings, 'atari800_system', '5200')

        # Autodetect A5200 CartType (Off/On)
        _set(coreSettings, 'atari800_CartType', 'enabled')

        # Joy Hack (for robotron)
        _set_from_system(coreSettings, 'atari800_opt2', system, default="disabled")


# Atari Jaguar
def _virtualjaguar_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Fast Blitter (Older, Faster, Less compatible)
    _set_from_system(coreSettings, 'virtualjaguar_usefastblitter', system, 'usefastblitter', default="enabled")

    # Show Bios Bootlogo
    _set_from_system(coreSettings, 'virtualjaguar_bios', system, 'bios_vj', default="enabled")

    # Doom Res Hack
    _set_from_system(coreSettings, 'virtualjaguar_doom_res_hack', system, 'doom_res_hack', default="disabled")


# Atari Lynx
def _handy_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Display rotation
    # Set this option to start game at 'None' because it crash the emulator
    _set(coreSettings, 'handy_rot', 'None')

# Bandai Wonder Swan & Wonder Swan Color
def _mednafen_wswan_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Display rotation
    if (rotate_display := system.config.get('wswan_rotate_display')) is not system.config.MISSING:
        wswanOrientation = rotate_display
    else:
        wswanGameRotation = videoMode.getAltDecoration(system.name, rom, 'retroarch')
        wswanOrientation = "portrait" if wswanGameRotation == "90" else "manual"

    _set(coreSettings, 'wswan_rotate_display', wswanOrientation)

# Commodore 64
def _vice_x64_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Activate Jiffydos
    _set(coreSettings, 'vice_jiffydos',          'enabled')
    # Enable Automatic Load Warp
    _set(coreSettings, 'vice_autoloadwarp',      'enabled')
    # Disable Datasette Hotkeys
    _set(coreSettings, 'vice_datasette_hotkeys', 'disabled')
    # Not Read 'vicerc'
    _set(coreSettings, 'vice_read_vicerc',       'disabled')
    # Select Joystick Type
    _set(coreSettings, 'vice_Controller',        'joystick')
    # Disable Turbo Fire
    _set(coreSettings, 'vice_turbo_fire',        'disabled')
    # Controller options for c64 are in libretroControllers.py
    c64_mapping = { 'a': "---",
            'aspect_ratio_toggle': "---",
            'b': "---",
            'joyport_switch': "RETROK_F10",
            'l': "RETROK_ESCAPE",
            'l2': "RETROK_F11",
            'l3': "SWITCH_JOYPORT",
            'ld': "---",
            'll': "---",
            'lr': "---",
            'lu': "---",
            'r': "RETROK_PAGEUP",
            'r2': "RETROK_LSHIFT",
            'rd': "RETROK_F7",
            'reset': "---",
            'rl': "RETROK_F3",
            'rr': "RETROK_F5",
            'ru': "RETROK_F1",
            'select': "TOGGLE_VKBD",
            'start': "RETROK_RETURN",
            'statusbar': "RETROK_F9",
            'vkbd': "RETROK_F12",
            'warp_mode': "RETROK_F11",
            'turbo_fire_toggle': "RETROK_RCTRL",
            'x': "RETROK_RCTRL",
            'y': "RETROK_SPACE" }
    for key, mapping_key in c64_mapping.items():
        coreSettings.save('vice_mapper_' + key, mapping_key)

    # Model type
    _set_from_system(coreSettings, 'vice_c64_model', system, 'c64_model', default="C64 PAL auto")

    # Aspect Ratio
    _set_from_system(coreSettings, 'vice_aspect_ratio', system, default="pal")

    # Zoom Mode
    zoom_mode = system.config.get('vice_zoom_mode', 'auto_disable')
    zoom_mode = 'auto' if zoom_mode == 'automatic' else zoom_mode
    _set(coreSettings, 'vice_crop', zoom_mode)
    _set(coreSettings, 'vice_zoom_mode', 'deprecated')

    # External palette
    _set_from_system(coreSettings, 'vice_external_palette', system, default="colodore")

    # Button options
    _set_from_system(coreSettings, 'vice_retropad_options', system, default="jump")

    # Select Controller Port
    _set_from_system(coreSettings, 'vice_joyport', system, default="2")

    # Select Controller Type
    # gun
    if system.config.use_guns and guns:
        _set(coreSettings, 'vice_joyport_type', '14')
    else:
        _set_from_system(coreSettings, 'vice_joyport_type', system, default="1")

    # RAM Expansion Unit (REU)
    _set_from_system(coreSettings, 'vice_ram_expansion_unit', system, default="none")

    # Keyboard Pass-through for Pad2Key
    _set_from_system(coreSettings, 'vice_physical_keyboard_pass_through', system, 'vice_keyboard_pass_through', default="disabled")


# Commodore 128
def _vice_x128_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Activate Jiffydos
    _set(coreSettings, 'vice_jiffydos',          'enabled')
    # Enable Automatic Load Warp
    _set(coreSettings, 'vice_autoloadwarp',      'enabled')
    # Disable Datasette Hotkeys
    _set(coreSettings, 'vice_datasette_hotkeys', 'disabled')
    # Not Read 'vicerc'
    _set(coreSettings, 'vice_read_vicerc',       'disabled')
    # Select Joystick Type
    _set(coreSettings, 'vice_Controller',        'joystick')
    # Disable Turbo Fire
    _set(coreSettings, 'vice_turbo_fire',        'disabled')

    # Model type
    _set_from_system(coreSettings, 'vice_c128_model', system, 'c128_model', default="C128 PAL")

    # Aspect Ratio
    _set_from_system(coreSettings, 'vice_aspect_ratio', system, default="pal")

    # Zoom Mode
    zoom_mode = system.config.get('vice_zoom_mode', 'auto_disable')
    zoom_mode = 'auto' if zoom_mode == 'automatic' else zoom_mode
    _set(coreSettings, 'vice_crop', zoom_mode)
    _set(coreSettings, 'vice_zoom_mode', 'deprecated')

    # External palette
    _set_from_system(coreSettings, 'vice_external_palette', system, default="colodore")

    # Button options
    _set_from_system(coreSettings, 'vice_retropad_options', system, default="disabled")

    # Select Controller Port
    _set_from_system(coreSettings, 'vice_joyport', system, default="2")

    # Select Controller Type
    _set_from_system(coreSettings, 'vice_joyport_type', system, default="1")

    # Keyboard Pass-through for Pad2Key
    _set_from_system(coreSettings, 'vice_physical_keyboard_pass_through', system, 'vice_keyboard_pass_through', default="disabled")


# Commodore Plus/4
def _vice_xplus4_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Enable Automatic Load Warp
    _set(coreSettings, 'vice_autoloadwarp',      'enabled')
    # Disable Datasette Hotkeys
    _set(coreSettings, 'vice_datasette_hotkeys', 'disabled')
    # Not Read 'vicerc'
    _set(coreSettings, 'vice_read_vicerc',       'disabled')
    # Select Joystick Type
    _set(coreSettings, 'vice_Controller',        'joystick')
    # Disable Turbo Fire
    _set(coreSettings, 'vice_turbo_fire',        'disabled')

    # Model type
    _set_from_system(coreSettings, 'vice_plus4_model', system, 'plus4_model', default="PLUS4 PAL")

    # Aspect Ratio
    _set_from_system(coreSettings, 'vice_aspect_ratio', system, default="pal")

    # Zoom Mode
    zoom_mode = system.config.get('vice_zoom_mode', 'auto_disable')
    zoom_mode = 'auto' if zoom_mode == 'automatic' else zoom_mode
    _set(coreSettings, 'vice_crop', zoom_mode)
    _set(coreSettings, 'vice_zoom_mode', 'deprecated')

    # External palette
    _set_from_system(coreSettings, 'vice_plus4_external_palette', system, default="colodore_ted")

    # Button options
    _set_from_system(coreSettings, 'vice_retropad_options', system, default="disabled")

    # Select Controller Port
    _set_from_system(coreSettings, 'vice_joyport', system, default="2")

    # Select Controller Type
    _set_from_system(coreSettings, 'vice_joyport_type', system, default="1")

    # Keyboard Pass-through for Pad2Key
    _set_from_system(coreSettings, 'vice_physical_keyboard_pass_through', system, 'vice_keyboard_pass_through', default="disabled")


# Commodore VIC-20
def _vice_xvic_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Enable Automatic Load Warp
    _set(coreSettings, 'vice_autoloadwarp',      'enabled')
    # Disable Datasette Hotkeys
    _set(coreSettings, 'vice_datasette_hotkeys', 'disabled')
    # Not Read 'vicerc'
    _set(coreSettings, 'vice_read_vicerc',       'disabled')
    # Select Joystick Type
    _set(coreSettings, 'vice_Controller',        'joystick')
    # Disable Turbo Fire
    _set(coreSettings, 'vice_turbo_fire',        'disabled')

    # Model type
    _set_from_system(coreSettings, 'vice_vic20_model', system, 'vic20_model', default="VIC20 PAL auto")

    # Aspect Ratio
    _set_from_system(coreSettings, 'vice_aspect_ratio', system, default="pal")

    # Zoom Mode
    zoom_mode = system.config.get('vice_zoom_mode', 'auto_disable')
    zoom_mode = 'auto' if zoom_mode == 'automatic' else zoom_mode
    _set(coreSettings, 'vice_crop', zoom_mode)
    _set(coreSettings, 'vice_zoom_mode', 'deprecated')

    # External palette
    _set_from_system(coreSettings, 'vice_vic20_external_palette', system, default="colodore_vic")

    # Button options
    _set_from_system(coreSettings, 'vice_retropad_options', system, default="disabled")

    # Select Controller Port
    _set_from_system(coreSettings, 'vice_joyport', system, default="2")

    # Select Controller Type
    _set_from_system(coreSettings, 'vice_joyport_type', system, default="1")

    # Keyboard Pass-through for Pad2Key
    _set_from_system(coreSettings, 'vice_physical_keyboard_pass_through', system, 'vice_keyboard_pass_through', default="disabled")


# Commodore PET
def _vice_xpet_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Enable Automatic Load Warp
    _set(coreSettings, 'vice_autoloadwarp',      'enabled')
    # Disable Datasette Hotkeys
    _set(coreSettings, 'vice_datasette_hotkeys', 'disabled')
    # Not Read 'vicerc'
    _set(coreSettings, 'vice_read_vicerc',       'disabled')
    # Select Joystick Type
    _set(coreSettings, 'vice_Controller',        'joystick')
    # Disable Turbo Fire
    _set(coreSettings, 'vice_turbo_fire',        'disabled')

    # Model type
    _set_from_system(coreSettings, 'vice_pet_model', system, 'pet_model', default="8032")

    # Aspect Ratio
    _set_from_system(coreSettings, 'vice_aspect_ratio', system, default="pal")

    # Zoom Mode
    zoom_mode = system.config.get('vice_zoom_mode', 'auto_disable')
    zoom_mode = 'auto' if zoom_mode == 'automatic' else zoom_mode
    _set(coreSettings, 'vice_crop', zoom_mode)
    _set(coreSettings, 'vice_zoom_mode', 'deprecated')

    # External palette
    _set_from_system(coreSettings, 'vice_pet_external_palette', system, default="default")

    # Button options
    _set_from_system(coreSettings, 'vice_retropad_options', system, default="disabled")

    # Select Controller Port
    _set_from_system(coreSettings, 'vice_joyport', system, default="2")

    # Select Controller Type
    _set_from_system(coreSettings, 'vice_joyport_type', system, default="1")

    # Keyboard Pass-through for Pad2Key
    _set_from_system(coreSettings, 'vice_physical_keyboard_pass_through', system, 'vice_keyboard_pass_through', default="disabled")


# Commodore AMIGA
def _puae_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Functional mapping for Amiga system
    # If you want to change them, you can add
    # some strings to batocera.conf by using
    # this syntax: SYSTEMNAME.retroarchcore.puae_mapper_BUTTONNAME=VALUE
    if system.name != 'amigacd32' and system.config.get('controller1_puae') != "517" and system.config.get('controller2_puae') != "517":
        # Controller mapping for A500 and A1200
        uae_mapping = { 'aspect_ratio_toggle': "---",
            'mouse_toggle': "RETROK_RCTRL",
            'statusbar': "RETROK_F11",
            'vkbd': "---",
            'reset': "---",
            'crop_toggle': "RETROK_F12",
            'zoom_mode_toggle': "---",
            'a': "---",
            'b': "---",
            'x': "RETROK_LALT",
            'y': "RETROK_SPACE",
            'l': "RETROK_ESCAPE",
            'l2': "MOUSE_LEFT_BUTTON",
            'l3': "SWITCH_JOYMOUSE",
            'ld': "---",
            'll': "---",
            'lr': "---",
            'lu': "---",
            'r': "RETROK_F1",
            'r2': "MOUSE_RIGHT_BUTTON",
            'r3': "TOGGLE_STATUSBAR",
            'rd': "---",
            'rl': "---",
            'rr': "---",
            'ru': "---",
            'select': "TOGGLE_VKBD",
            'start': "RETROK_RETURN",}
        for key, mapped_key in uae_mapping.items():
            coreSettings.save('puae_mapper_' + key, mapped_key)
    else:
        # Controller mapping for CD32
        uae_mapping = { 'aspect_ratio_toggle': "---",
            'mouse_toggle': "RETROK_RCTRL",
            'statusbar': "RETROK_F11",
            'vkbd': "---",
            'reset': "---",
            'crop_toggle': "RETROK_F12",
            'zoom_mode_toggle': "---",
            'a': "---",
            'b': "---",
            'x': "---",
            'y': "---",
            'l': "---",
            'l2': "MOUSE_LEFT_BUTTON",
            'l3': "SWITCH_JOYMOUSE",
            'ld': "---",
            'll': "---",
            'lr': "---",
            'lu': "---",
            'r': "---",
            'r2': "MOUSE_RIGHT_BUTTON",
            'r3': "TOGGLE_STATUSBAR",
            'rd': "---",
            'rl': "---",
            'rr': "---",
            'ru': "---",
            'select': "---",
            'start': "---",}
        for key, mapped_key in uae_mapping.items():
            coreSettings.save('puae_mapper_' + key, mapped_key)
    # Show Video Options
    _set(coreSettings, 'puae_video_options_display', 'enabled')

    # Amiga Model
    if (model := system.config.get('puae_model', 'automatic')) != 'automatic':
        _set(coreSettings, 'puae_model', model)
    else:
        model_mapping = {
            'amiga1200': 'A1200',
            'amigacd32': 'CD32FR',
            'amigacdtv': 'CDTV',
        }
        # Will default to A500 when booting floppy disks, A600 when booting hard drives on auto
        _set(coreSettings, 'puae_model', model_mapping.get(system.name, 'auto'))

    # CPU Compatibility
    _set_from_system(coreSettings, 'puae_cpu_compatibility', system, 'cpu_compatibility', default="normal")

    # CPU Multiplier (Overclock)
    _set_from_system(coreSettings, 'puae_cpu_throttle', system, 'cpu_throttle', default="0.0")
    _set(coreSettings, 'puae_cpu_multiplier', '0')

    # CPU Cycle Exact Speed (Overclock)
    if system.config.get('cpu_compatibility') == 'exact':
        _set(coreSettings, 'puae_cpu_throttle', '0.0')
        _set_from_system(coreSettings, 'puae_cpu_multiplier', system, 'cpu_multiplier', default="0")

    # Standard Video
    _set_from_system(coreSettings, 'puae_video_standard', system, 'video_standard', default="PAL auto")

    # Video Resolution
    _set_from_system(coreSettings, 'puae_video_resolution', system, 'video_resolution', default="hires")

    # Zoom Mode
    zoom_mode = system.config.get('zoom_mode', 'automatic')
    zoom_mode = 'auto' if zoom_mode == 'automatic' else zoom_mode
    _set(coreSettings, 'puae_crop', zoom_mode)
    _set(coreSettings, 'puae_zoom_mode', 'deprecated')

    # Frameskip
    _set_from_system(coreSettings, 'puae_gfx_framerate', system, 'gfx_framerate', default="disabled")

    # Mouse Speed
    _set_from_system(coreSettings, 'puae_mouse_speed', system, 'mouse_speed', default="200")

    # Jump on B
    _set_from_system(coreSettings, 'puae_retropad_options', system, 'pad_options', default='disabled' if system.name == 'amigacdtv' else 'jump')

    if system.name in ['amiga500', 'amiga1200']:
        # Floppy Turbo Speed
        _set_from_system(coreSettings, 'puae_floppy_speed', system, default="100")

        # 2P Gamepad Mapping (Keyrah)
        _set_from_system(coreSettings, 'puae_keyrah_keypad_mappings', system, 'keyrah_mapping', default="enabled")

        # Whdload Launcher
        _set_from_system(coreSettings, 'puae_use_whdload_prefs', system, 'whdload', default="config")

        # Disable Emulator Joystick for Pad2Key
        _set_from_system(coreSettings, 'puae_physical_keyboard_pass_through', system, 'disable_joystick', default="disabled")

    if system.name in ['amigacd32', 'amigacdtv']:
        # Boot animation first inserting CD
        _set_from_system(coreSettings, 'puae_cd_startup_delayed_insert', system, default="disabled")

        # CD Turbo Speed
        _set_from_system(coreSettings, 'puae_cd_speed', system, default="100")

    if system.name == 'amigacd32':
        # Jump on A (Blue)
        _set_from_system(coreSettings, 'puae_cd32pad_options', system, default="disabled")


# DICE
def _dice_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Pointer-as-paddle, simplest mouse setup
    _set_from_system(coreSettings, 'dice_use_mouse_pointer_for_paddle_1', system, 'ttl_use_mouse_pointer_for_paddle_1', default='disabled')
    # DEVICE_RETRO_MOUSE control of paddles
    _set_from_system(coreSettings, 'dice_retromouse_paddle0', system, 'ttl_retromouse_paddle0', default='disabled')
    _set_from_system(coreSettings, 'dice_retromouse_paddle1', system, 'ttl_retromouse_paddle1', default='disabled')
    _set_from_system(coreSettings, 'dice_retromouse_paddle2', system, 'ttl_retromouse_paddle2', default='disabled')
    _set_from_system(coreSettings, 'dice_retromouse_paddle3', system, 'ttl_retromouse_paddle3', default='disabled')
    # Axes for mouse-paddles.  Default for mice, but allow overrides for spinner setups
    _set_from_system(coreSettings, 'dice_retromouse_paddle0_x', system, 'ttl_retromouse_paddle0_x', default='x')
    _set_from_system(coreSettings, 'dice_retromouse_paddle0_y', system, 'ttl_retromouse_paddle0_y', default='y')
    _set_from_system(coreSettings, 'dice_retromouse_paddle1_x', system, 'ttl_retromouse_paddle0_x', default='x')
    _set_from_system(coreSettings, 'dice_retromouse_paddle1_y', system, 'ttl_retromouse_paddle0_y', default='y')
    _set_from_system(coreSettings, 'dice_retromouse_paddle2_x', system, 'ttl_retromouse_paddle0_x', default='x')
    _set_from_system(coreSettings, 'dice_retromouse_paddle2_y', system, 'ttl_retromouse_paddle0_y', default='y')
    _set_from_system(coreSettings, 'dice_retromouse_paddle3_x', system, 'ttl_retromouse_paddle0_x', default='x')
    _set_from_system(coreSettings, 'dice_retromouse_paddle3_y', system, 'ttl_retromouse_paddle0_y', default='y')
    # Miscellaneous input scaling tweaks
    _set_from_system(coreSettings, 'dice_paddle_keyboard_sensitivity', system, 'ttl_paddle_keyboard_sensitivity', default='250')
    _set_from_system(coreSettings, 'dice_paddle_joystick_sensitivity', system, 'ttl_paddle_joystick_sensitivity', default='500')
    _set_from_system(coreSettings, 'dice_retromouse_paddle_sensitivity', system, 'ttl_retromouse_paddle_sensitivity', default='125')
    _set_from_system(coreSettings, 'dice_wheel_keyjoy_sensitivity', system, 'ttl_wheel_keyjoy_sensitivity', default='500')
    _set_from_system(coreSettings, 'dice_throttle_keyjoy_sensitivity', system, 'ttl_throttle_keyjoy_sensitivity', default='250')
    # DIP switches
    _set_from_system(coreSettings, 'dice_dipswitch_1', system, 'ttl_dipswitch_1', default='-1')
    _set_from_system(coreSettings, 'dice_dipswitch_2', system, 'ttl_dipswitch_2', default='-1')
    _set_from_system(coreSettings, 'dice_dipswitch_3', system, 'ttl_dipswitch_3', default='-1')
    _set_from_system(coreSettings, 'dice_dipswitch16_1', system, 'ttl_dipswitch16_1', default='-1')
    _set_from_system(coreSettings, 'dice_dipswitch16_2', system, 'ttl_dipswitch16_2', default='-1')


# Dolpin Wii
def _dolphin_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Wii System Languages
    _set_from_system(coreSettings, 'dolphin_language', system, 'wii_language', default='English')

    # Wii Resolution Scale
    _set_from_system(coreSettings, 'dolphin_efb_scale', system, 'wii_resolution', default="x1 (640 x 528)")

    # Anisotropic Filtering
    _set_from_system(coreSettings, 'dolphin_max_anisotropy', system, 'wii_anisotropic', default="x1")

    # Wii Tv Mode
    _set_from_system(coreSettings, 'dolphin_widescreen', system, 'wii_widescreen', default="enabled")

    # Widescreen Hack
    _set_from_system(coreSettings, 'dolphin_widescreen_hack', system, 'wii_widescreen_hack', default="disabled")

    # Shader Compilation Mode
    _set_from_system(coreSettings, 'dolphin_shader_compilation_mode', system, 'wii_shader_mode', default="sync")

    # OSD
    _set_from_system(coreSettings, 'dolphin_osd_enabled', system, 'wii_osd', default="enabled")


# Magnavox - Odyssey2 / Phillips Videopac+
def _o2em_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Virtual keyboard transparency
    _set(coreSettings, 'o2em_vkbd_transparency', '25')

    # Emulated Hardware
    _set_from_system(coreSettings, 'o2em_bios', system, default='g7400.bin' if system.name == 'videopacplus' else 'o2rom.bin')

    # Emulated Hardware
    region = system.config.get('o2em_region', 'autodetect')
    _set(coreSettings, 'o2em_region', 'auto' if region == 'autodetect' else region)

    # Swap Gamepad
    _set_from_system(coreSettings, 'o2em_swap_gamepads', system, default='disabled')

    # Crop Overscan
    _set_from_system(coreSettings, 'o2em_crop_overscan', system, default='enabled')

    # Ghosting effect
    _set_from_system(coreSettings, 'o2em_mix_frames', system, default='disabled')

    # Audio Filter
    low_pass_range = system.config.get('o2em_low_pass_range', '0')
    _set(coreSettings, 'o2em_low_pass_filter', 'disabled' if low_pass_range == '0' else 'enabled')
    _set(coreSettings, 'o2em_low_pass_range', low_pass_range)


# MAME/MESS/MAMEVirtual
def _mame_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Lightgun mode
    _set(coreSettings, 'mame_lightgun_mode', 'lightgun')

    # Enable cheats
    _set(coreSettings, 'mame_cheats_enable', 'enabled')

    # CPU Overclock
    _set_from_system(coreSettings, 'mame_cpu_overclock', system, default='default')

    # Video Resolution
    _set_from_system(coreSettings, 'mame_altres', system, default='640x480')

    # Disable controller profiling
    _set(coreSettings, 'mame_buttons_profiles', 'disabled')

    # Software Lists (MESS)
    _set(coreSettings, 'mame_softlists_enable', 'disabled')
    _set(coreSettings, 'mame_softlists_auto_media', 'disabled')

    # Enable config reading (for controls)
    _set(coreSettings, 'mame_read_config', 'enabled')

    # Use CLI (via CMD file) to boot
    _set(coreSettings, 'mame_boot_from_cli', 'enabled')

    # Activate mouse for Mac & Archimedes
    _set(coreSettings, 'mame_mouse_enable', 'enabled' if system.name in [ 'macintosh', 'archimedes' ] else 'disabled')


# SAME_CDI
def _same_cdi_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Lightgun mode
    _set(coreSettings, 'same_cdi_lightgun_mode', 'lightgun')

    # Enable cheats
    _set(coreSettings, 'same_cdi_cheats_enable', 'enabled')

    # CPU Overclock
    _set_from_system(coreSettings, 'same_cdi_cpu_overclock', system, default='default')

    # Video Resolution
    _set_from_system(coreSettings, 'same_cdi_altres', system, 'same_cdi_altres', default='640x480')

    # Disable controller profiling
    _set(coreSettings, 'same_cdi_buttons_profiles', 'disabled')
    # Software Lists (MESS)
    _set(coreSettings, 'same_cdi_softlists_enable', 'disabled')
    _set(coreSettings, 'same_cdi_softlists_auto_media', 'disabled')
    # Enable config reading (for controls)
    _set(coreSettings, 'same_cdi_read_config', 'enabled')
    # Use CLI (via CMD file) to boot
    _set(coreSettings, 'same_cdi_boot_from_cli', 'enabled')
    # Activate mouse
    _set(coreSettings, 'same_cdi_mouse_enable', 'enabled')


# MAME 2003 Plus
def _mame078plus_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Skip Disclaimer and Warnings
    _set(coreSettings, 'mame2003-plus_skip_disclaimer', 'enabled')
    _set(coreSettings, 'mame2003-plus_skip_warnings',   'enabled')

    # Control Mapping
    _set_from_system(coreSettings, 'mame2003-plus_analog', system, 'mame2003-plus_analog', default='digital')

    # Frameskip
    _set_from_system(coreSettings, 'mame2003-plus_frameskip', system, 'mame2003-plus_frameskip', default='0')

    # Input interface
    _set_from_system(coreSettings, 'mame2003-plus_input_interface', system, 'mame2003-plus_input_interface', default='retropad')

    # TATE Mode
    _set_from_system(coreSettings, 'mame2003-plus_tate_mode', system, 'mame2003-plus_tate_mode', default='disabled')

    # NEOGEO Bios
    _set_from_system(coreSettings, 'mame2003-plus_neogeo_bios', system, 'mame2003-plus_neogeo_bios', default='unibios33')

    # gun
    _set(coreSettings, 'mame2003-plus_xy_device', 'lightgun' if system.config.use_guns and guns else 'mouse')

    # gun cross
    _set_from_system(coreSettings, 'mame2003-plus_crosshair_enabled', system, 'mame2003-plus_crosshair_enabled', default='enabled' if guns_need_crosses(guns) else 'disabled')


# TODO: Add CORE options for MAME / iMame4all

# MB Vectrex
def _vecx_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Res Multiplier
    _set_from_system(coreSettings, 'vecx_res_multi', system, 'res_multi', default='1')


# Microsoft DOS
def _dosbox_pure_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    #allow to read a custom dosbox.conf present in the game directory
    _set(coreSettings, 'dosbox_pure_conf', 'inside')

    # CPU Type
    cpu_type = system.config.get('pure_cpu_type', 'automatic')
    _set(coreSettings, 'dosbox_pure_cpu_type', 'auto' if cpu_type == 'automatic' else cpu_type)

    # CPU Core
    cpu_core = system.config.get('pure_cpu_core', 'automatic')
    _set(coreSettings, 'dosbox_pure_cpu_core', 'auto' if cpu_core == 'automatic' else cpu_core)

    # Emulated performance (CPU Cycles)
    cpu_cycles = system.config.get('pure_cycles', 'automatic')
    _set(coreSettings, 'dosbox_pure_cycles', 'auto' if cpu_cycles == 'automatic' else cpu_cycles)

    # Graphics Chip type
    _set_from_system(coreSettings, 'dosbox_pure_machine', system, 'pure_machine', default='svga')

    # Memory size
    _set_from_system(coreSettings, 'dosbox_pure_memory_size', system, 'pure_memory_size', default='16')

    # Save state
    _set_from_system(coreSettings, 'dosbox_pure_savestate', system, 'pure_savestate', default='on')

    # Keyboard Layout
    _set_from_system(coreSettings, 'dosbox_pure_keyboard_layout', system, 'pure_keyboard_layout', default='us')

    # Automatic Gamepad Mapping
    _set_from_system(coreSettings, 'dosbox_pure_auto_mapping', system, 'pure_auto_mapping', default='true')

    # Joystick Analog Deadzone
    _set_from_system(coreSettings, 'dosbox_pure_joystick_analog_deadzone', system, 'pure_joystick_analog_deadzone', default='15')

    # Enable Joystick Timed Intervals
    _set_from_system(coreSettings, 'dosbox_pure_joystick_timed', system, 'pure_joystick_timed', default='true')

    # SoundBlaster Type
    _set_from_system(coreSettings, 'dosbox_pure_sblaster_type', system, 'pure_sblaster_type', default='sb16')

    # Enable Gravis Sound
    _set_from_system(coreSettings, "dosbox_pure_gus", system, 'pure_gravis', default='false')

    # Midi Type
    _set_from_system(coreSettings, 'dosbox_pure_midi', system, 'pure_midi', default='disabled')


# Microsoft MSX and Colecovision
def _bluemsx_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Auto Select Core
    if system.name == 'colecovision':
        _set(coreSettings, 'bluemsx_msxtype', 'ColecoVision')
    elif system.name == 'msx1':
        _set(coreSettings, 'bluemsx_msxtype', 'MSX')
    elif system.name == 'msx2':
        _set(coreSettings, 'bluemsx_msxtype', 'MSX2')
    elif system.name == 'msx2+':
        _set(coreSettings, 'bluemsx_msxtype', 'MSX2+')
    elif system.name == 'msxturbor':
        _set(coreSettings, 'bluemsx_msxtype', 'MSXturboR')

    # Forces cropping of overscanned frames
    _set(coreSettings, 'bluemsx_overscan', 'enabled' if system.name in ['colecovision', 'msx1'] else 'MSX2')

    # Reduce Sprite Flickering
    _set_from_system_bool(coreSettings, 'bluemsx_nospritelimits', system, default=True, values=('ON', 'OFF'))

    # Zoom, Hide Video Border
    _set_from_system(coreSettings, 'bluemsx_overscan', system, default='MSX2')


# Nec PC Engine / CD
def _pce_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Remove 16-sprites-per-scanline hardware limit
    _set_from_system(coreSettings, 'pce_nospritelimit', system, 'pce_nospritelimit', default='enabled')


# Nec PC-8800
def _quasi88_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # PC Model
    _set_from_system(coreSettings, 'q88_basic_mode', system, default='N88 V2')

    # CPU clock (Overclock)
    _set_from_system(coreSettings, 'q88_cpu_clock', system, default='4')

    # Use PCG-8100
    _set_from_system(coreSettings, 'q88_pcg-8100', system, default='disabled')


# Nec PC-9800
def _np2kai_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # https://github.com/AZO234/NP2kai/blob/6e8f651a72c2ece37cc52e17cdaf4fdb87a6b2f9/sdl/libretro/libretro_core_options.h
    # Use the American keyboard
    _set(coreSettings, 'np2kai_keyboard', 'Us')
    # Fast memcheck at startup
    _set(coreSettings, 'np2kai_FastMC', 'ON')
    # Sound Generator: Use "fmgen" for enhanced sound rendering, not "Default"
    # _set(coreSettings, 'np2kai_usefmgen', 'fmgen')
    # PC Model
    _set_from_system(coreSettings, 'np2kai_model', system, default='PC-9801VX')

    # CPU Feature
    _set_from_system(coreSettings, 'np2kai_cpu_feature', system, default='Intel 80386')

    # CPU Clock Multiplier
    _set_from_system(coreSettings, 'np2kai_clk_mult', system, default='4')

    # RAM Size
    _set_from_system(coreSettings, 'np2kai_ExMemory', system, 'np2kai_ExMemory', default='3')

    # GDC
    _set_from_system(coreSettings, 'np2kai_gdc', system, 'np2kai_gdc', default='uPD7220')

    # Remove Scanlines (255 lines)
    scanlines = system.config.get('np2kai_skipline', 'Full 255 lines')

    if scanlines == 'True':
        scanlines = 'ON'
    elif scanlines == 'False':
        scanlines = 'OFF'

    _set(coreSettings, 'np2kai_skipline', scanlines)

    # Real Palettes
    _set_from_system_bool(coreSettings, 'np2kai_realpal', system, values=('ON', 'OFF'))

    # Sound Board
    _set_from_system(coreSettings, 'np2kai_SNDboard', system, 'np2kai_SNDboard', default='PC9801-26K + 86')

    # JAST SOUND
    _set_from_system_bool(coreSettings, 'np2kai_jast_snd', system, values=('ON', 'OFF'))

    # Joypad to Keyboard Mapping
    _set_from_system(coreSettings, 'np2kai_joymode', system, 'np2kai_joymode', default='Arrows')


# Nec PC Engine SuperGrafx
def _mednafen_supergrafx_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Remove 16-sprites-per-scanline hardware limit
    _set_from_system(coreSettings, 'sgx_nospritelimit', system, 'sgx_nospritelimit', default='enabled')


# Nec PC-FX
def _pcfx_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Remove 16-sprites-per-scanline hardware limit
    _set_from_system(coreSettings, 'pcfx_nospritelimit', system, 'pcfx_nospritelimit', default='enabled')

# Nintendo 64
def _mupen64plus_next_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Threaded Rendering
    _set(coreSettings, 'mupen64plus-ThreadedRenderer', 'True')

    # Use High-Res Textures Pack
    # .htc files must be placed in 'Mupen64plus/cache'
    _set(coreSettings, 'mupen64plus-txHiresEnable', 'True')

    # Video 4:3 Resolution
    _set_from_system(coreSettings, 'mupen64plus-43screensize', system, default='320x240')

    # Video 16:9 Resolution
    _set_from_system(coreSettings, 'mupen64plus-169screensize', system, default='640x360')

    # Widescreen Hack
    # Increases from 4:3 to 16:9 in 3D games (bad for 2D)
    if (
        system.config.get('mupen64plus-aspect') == '16:9 adjusted'
        and system.config.get('ratio') == '16/9'
        and system.config.get('bezel') == 'none'
    ):
        aspect = '16:9 adjusted'
    else:
        aspect = '4:3'

    _set(coreSettings, 'mupen64plus-aspect', aspect)

    # Bilinear Filtering
    _set_from_system(coreSettings, 'mupen64plus-BilinearMode', system, default='standard')

    # Anti-aliasing (MSA)
    _set_from_system(coreSettings, 'mupen64plus-MultiSampling', system, default='0')

    # Texture Filtering
    _set_from_system(coreSettings, 'mupen64plus-txFilterMode', system, default='None')

    # Texture Enhancement
    _set_from_system(coreSettings, 'mupen64plus-txEnhancementMode', system, default='None')

    # Controller rumble settings
    metadata: dict[str, str] | None = None
    for pak_number in range(1, 5):
        pak_default = 'memory' if pak_number == 1 else 'none'
        pak_key = f'mupen64plus-pak{pak_number}'
        pak_value = system.config.get(pak_key, pak_default)

        if pak_value == 'auto_rumble':
            if metadata is None:
                metadata = controllersConfig.getGamesMetaData(system.name, rom)

            pak_value = 'rumble' if metadata.get('controller_rumble') == 'true' else pak_default

        _set(coreSettings, pak_key, pak_value)

    # RDP Plugin
    _set_from_system(coreSettings, 'mupen64plus-rdp-plugin', system, 'mupen64plus-rdpPlugin', default='gliden64')

    # RSP Plugin
    _set_from_system(coreSettings, 'mupen64plus-rsp-plugin', system, 'mupen64plus-rspPlugin', default='hle')

    # CPU Core
    _set_from_system(coreSettings, 'mupen64plus-cpucore', system, 'mupen64plus-cpuCore', default='dynamic_recompiler')

    # Framerate
    _set_from_system(coreSettings, 'mupen64plus-Framerate', system, 'mupen64plus-Framerate', default='Original')

    # Parallel-RDP Upscaling
    _set_from_system(coreSettings, 'mupen64plus-parallel-rdp-upscaling', system, 'mupen64plus-parallel-rdp-upscaling', default='1x')

    # Joystick deadzone
    _set_from_system(coreSettings, 'mupen64plus-astick-deadzone', system, 'mupen64plus-deadzone', default='0' if system.config.use_wheels and wheels else '15')

    # Joystick sensitivity
    _set_from_system(coreSettings, 'mupen64plus-astick-sensitivity', system, 'mupen64plus-sensitivity', default='100')


def _parallel_n64_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    _set(coreSettings, 'parallel-n64-64dd-hardware', 'disabled')
    _set(coreSettings, 'parallel-n64-boot-device',   'Default')

    # Graphics Plugin
    _set_from_system(coreSettings, 'parallel-n64-gfxplugin', system, default='parallel' if system.config.get('gfxbackend') == 'vulkan' else 'auto')  # vulkan doesn't work with auto

    # Video Resolution
    _set_from_system(coreSettings, 'parallel-n64-screensize', system, 'parallel-n64-screensize', default='320x240')

    # Widescreen Hack
    # Increases from 4:3 to 16:9 in 3D games (bad for 2D)
    if (
        system.config.get('parallel-n64-aspectratiohint') == 'widescreen'
        and system.config.get('ratio') == '16/9'
        and system.config.get('bezel') == 'none'
    ):
        aspect = 'widescreen'
    else:
        aspect = 'normal'

    _set(coreSettings, 'parallel-n64-aspectratiohint', aspect)

    # Texture Filtering
    _set_from_system(coreSettings, 'parallel-n64-filtering', system, 'parallel-n64-filtering', default='automatic')

    # Framerate
    _set_from_system(coreSettings, 'parallel-n64-framerate', system, 'parallel-n64-framerate', default='automatic')

    # Controller rumble settings
    metadata: dict[str, str] | None = None
    for pak_number in range(1, 5):
        pak_default = 'memory' if pak_number == 1 else 'none'
        pak_key = f'parallel-n64-pak{pak_number}'
        pak_value = system.config.get(pak_key, pak_default)

        if pak_value == 'auto_rumble':
            if metadata is None:
                metadata = controllersConfig.getGamesMetaData(system.name, rom)

            pak_value = 'rumble' if metadata.get('controller_rumble') == 'true' else pak_default

        _set(coreSettings, pak_key, pak_value)

    # Joystick deadzone
    _set_from_system(coreSettings, 'parallel-n64-astick-deadzone', system, 'parallel-n64-deadzone', default='0' if system.config.use_wheels and wheels else '15')

    # Joystick sensitivity
    _set_from_system(coreSettings, 'parallel-n64-astick-sensitivity', system, 'parallel-n64-sensitivity', default='100')

    # Nintendo 64-DD
    if system.name == 'n64dd':
        # 64DD Hardware
        _set(coreSettings, 'parallel-n64-64dd-hardware', 'enabled')
        # Boot device
        _set(coreSettings, 'parallel-n64-boot-device',   '64DD IPL')


# Nintendo DS
def _desmume_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Emulate Stylus on Right Stick
    _set(coreSettings, 'desmume_pointer_device_r', 'emulated')

    # Internal Resolution
    _set_from_system(coreSettings, 'desmume_internal_resolution', system, 'internal_resolution_desmume', default='256x192')

    # Anti-aliasing (MSAA)
    _set_from_system(coreSettings, 'desmume_gfx_multisampling', system, 'multisampling', default='disabled')

    # Texture Smoothing
    _set_from_system(coreSettings, 'desmume_gfx_texture_smoothing', system, 'texture_smoothing', default='disabled')

    # Textures Upscaling (XBRZ)
    _set_from_system(coreSettings, 'desmume_gfx_texture_scaling', system, 'texture_scaling', default='1')

    # Frame Skip
    _set_from_system(coreSettings, 'desmume_frameskip', system, 'frameskip_desmume', default='0')

    # Screen Layout
    _set_from_system(coreSettings, 'desmume_screens_layout', system, 'screens_layout', default='top/bottom')


def _melonds_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Console Mode
    _set_from_system(coreSettings, 'melonds_console_mode', system, 'melonds_console_mode', default='DS')

    # Language
    _set_from_system(coreSettings, 'melonds_language', system, 'melonds_language', default='English')

    # External Firmware
    _set_from_system(coreSettings, 'melonds_use_fw_settings', system, 'melonds_use_fw_settings', default='disable')

    # Enable threaded rendering
    _set(coreSettings, 'melonds_threaded_renderer', 'enabled')

    # Emulate Stylus on Right Stick
    _set_from_system(coreSettings, 'melonds_touch_mode',  system, 'melonds_touch_mode', default='Joystick')

    # Boot game directly
    _set_from_system(coreSettings, 'melonds_boot_directly', system, 'melonds_boot_directly', default='enabled')

    # Screen Layout + Hybrid Ratio
    hybrid_ratio = '2'
    _set(coreSettings, 'melonds_hybrid_ratio', '2')

    coreSettings.save('melonds_hybrid_ratio', '"2"')

    match system.config.get('melonds_screen_layout', 'Top/Bottom'):
        case 'Hybrid Top-Ratio2':
            layout = 'Hybrid Top'
        case 'Hybrid Top-Ratio3':
            layout = 'Hybrid Top'
            hybrid_ratio = '3'
        case 'Hybrid Bottom-Ratio2':
            layout = 'Hybrid Bottom'
        case 'Hybrid Bottom-Ratio3':
            layout = 'Hybrid Bottom'
            hybrid_ratio = '3'
        case _ as screen_layout:
            layout = screen_layout

    _set(coreSettings, 'melonds_screen_layout', layout)
    _set(coreSettings, 'melonds_hybrid_ratio', hybrid_ratio)


def _melondsds_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # System Settings
    _set_from_system(coreSettings, 'melonds_console_mode', system, 'melondsds_console_mode', default='DS')

    # Video Settings
    _set_from_system(coreSettings, 'melonds_render_mode', system, 'melondsds_render_mode', default='software')
    _set_from_system(coreSettings, 'melonds_opengl_resolution', system, 'melondsds_resolution', default='1')
    _set_from_system(coreSettings, 'melonds_opengl_better_polygons', system, 'melondsds_poygon', default='disabled')
    _set_from_system(coreSettings, 'melonds_opengl_filtering', system, 'melondsds_filtering', default='nearest')

    # Screen Settings
    _set_from_system(coreSettings, 'melonds_show_cursor', system, 'melondsds_cursor', default='nearest')
    _set_from_system(coreSettings, 'melonds_cursor_timeout', system, 'melondsds_cursor_timeout', default='3')
    _set_from_system(coreSettings, 'melonds_touch_mode', system, 'melondsds_touchmode', default='auto')
    # set 1 screen for now top/botton
    _set(coreSettings, 'melonds_number_of_screen_layouts', '1')
    _set(coreSettings, 'melonds_screen_gap', '0')
    _set(coreSettings, 'melonds_screen_layout1', 'top-bottom')

    # Firmware Settings
    _set_from_system(coreSettings, 'melonds_firmware_wfc_dns', system, 'melondsds_dns', default='178.62.43.212')
    _set_from_system(coreSettings, 'melonds_firmware_language', system, 'melondsds_language', default='default')
    _set_from_system(coreSettings, 'melonds_firmware_favorite_color', system, 'melondsds_colour', default='default')
    _set_from_system(coreSettings, 'melonds_firmware_birth_month', system, 'melondsds_month', default='default')
    _set_from_system(coreSettings, 'melonds_firmware_birth_day', system, 'melondsds_day', default='default')

    # Onscreen Display
    _set_from_system(coreSettings, 'melonds_show_unsupported_features', system, 'melondsds_show_unsupported', default='disabled')
    _set_from_system(coreSettings, 'melonds_show_bios_warnings', system, 'melondsds_show_bios', default='disabled')
    _set_from_system(coreSettings, 'melonds_show_current_layout', system, 'melondsds_show_layout', default='disabled')
    _set_from_system(coreSettings, 'melonds_show_mic_state', system, 'melondsds_show_mic', default='disabled')
    _set_from_system(coreSettings, 'melonds_show_camera_state', system, 'melondsds_show_camera', default='disabled')
    _set_from_system(coreSettings, 'melonds_show_lid_state', system, 'melondsds_show_lid', default='disabled')


# Nintendo Gameboy (Dual Screen) / GB Color (Dual Screen)
def _tgbdual_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Emulates two Game Boy units
    _set(coreSettings, 'tgbdual_gblink_enable',    'enabled')
    # Displays the selected player screens
    _set(coreSettings, 'tgbdual_single_screen_mp', 'both players')
    # Switches the screen layout
    _set(coreSettings, 'tgbdual_screen_placement', 'left-right')
    # Switch Game Boy sound
    _set(coreSettings, 'tgbdual_audio_output',     'Game Boy #1')
    # Switches the player screens
    _set(coreSettings, 'tgbdual_switch_screens',   'normal')


# Nintendo Gameboy / GB Color / GB Advance
def _gambatte_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # GB / GBC: Use official Bootlogo
    _set_from_system(coreSettings, 'gambatte_gb_bootloader', system, 'gb_bootloader', default='enabled')

    # GB / GBC: Interframe Blending (LCD ghosting effects)
    _set_from_system(coreSettings, 'gambatte_mix_frames', system, 'gb_mix_frames', default='disabled')

    if system.name == 'gbc':
        # GBC Color Correction
        _set_from_system(coreSettings, 'gambatte_gbc_color_correction', system, 'gbc_color_correction', default='disabled')
    elif system.name == 'gb':
        _set(coreSettings, 'gambatte_gbc_color_correction', 'disabled')

    if system.name == 'gb':
        # GB: Colorization of GB games
        match system.config.get('gb_colorization', 'GB - DMG'):
            case 'none':  # No Selection --> Classic Green
                colorization = 'internal'
                palette = 'Special 1'
            case 'GB - Disabled':  # Disabled --> Black and White Color
                colorization = 'disabled'
                palette = 'Special 1'
            case 'GB - SmartColor':  # Smart Coloring --> Gambatte's most colorful/appropriate color
                colorization = 'auto'
                palette = 'Special 1'
            case 'GBC - Game Specific':  # Game specific --> Select automatically a game-specific Game Boy Color palette
                colorization = 'GBC'
                palette = 'Special 1'
            case 'custom':  # Custom Palettes --> Use the custom palettes in the bios/palettes folder
                colorization = 'custom'
                palette = 'Special 1'
            case _ as gb_colorization: # User Selection or default (classic green)
                colorization = 'internal'
                palette = gb_colorization

        _set(coreSettings, 'gambatte_gb_colorization', colorization)
        _set(coreSettings, 'gambatte_gb_internal_palette', palette)


def _mgba_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Skip BIOS intro
    _set_from_system_bool(coreSettings, 'mgba_skip_bios', system, 'skip_bios_mgba', values=('ON', 'OFF'))

    # Rumble
    # This works because only '1' is treated as True in get_bool()
    _set_from_system_bool(coreSettings, 'mgba_force_gbp', system, 'rumble_gain', default=True, values=('OFF', 'ON'))

    if system.name != 'gba':
        # GB / GBC: Use Super Game Boy borders
        _set_from_system_bool(coreSettings, 'mgba_sgb_borders', system, 'sgb_borders', values=('ON', 'OFF'))

        # GB / GBC: Color Correction
        color_correction = system.config.get('color_correction', 'False')
        _set(coreSettings, 'mgba_color_correction', 'OFF' if color_correction == 'False' else color_correction)

    if system.name == 'gba':
        # GBA: Solar sensor level, Boktai 1: The Sun is in Your Hand
        _set_from_system(coreSettings, 'mgba_solar_sensor_level', system, 'solar_sensor_level', default='0')

        # GBA: Frameskip
        _set_from_system(coreSettings, 'mgba_frameskip', system, 'frameskip_mgba', default='0')

    # Force Super Game Boy mode for SGB system, auto for all others
    # No current option to override - add if needed.
    if system.name == 'sgb':
        _set(coreSettings, 'mgba_gb_model', 'Super Game Boy')

        # Default border to on for SGB
        _set_from_system_bool(coreSettings, 'mgba_sgb_borders', system, 'sgb_borders', default=True, values=('ON', 'OFF'))
    else:
        _set(coreSettings, 'mgba_gb_model', 'Autodetect')


def _vba_m_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # GB / GBC / GBA: Auto select fine hardware mode
    # Emulator AUTO mode not working fine
    _set(coreSettings, 'vbam_gbHardware', system.name)

    if system.name == 'gb':
        # GB: Colorisation of GB games
        _set_from_system(coreSettings, 'vbam_palettes', system, 'palettes', default='black and white')

        # GB: Use Super Game Boy borders
        _set_from_system(coreSettings, 'vbam_showborders', system, 'showborders_gb', default='disabled')

        if system.config.get_bool('showborders_gb'):
            # Force SGB mode, "sgb2" is same
            _set(coreSettings, 'vbam_gbHardware', 'sgb')

        # GB: Color Correction
        _set_from_system(coreSettings, 'vbam_gbcoloroption', system, 'gbcoloroption_gb', default='disabled')

    if system.name == 'gbc':
        # GBC: Use Super Game Boy borders
        _set_from_system(coreSettings, 'vbam_showborders', system, 'showborders_gbc', default='disabled')

        if system.config.get_bool('showborders_gbc'):
            # Force SGB mode, "sgb2" is same
            _set(coreSettings, 'vbam_gbHardware', 'sgb')

        # GB: Color Correction
        _set_from_system(coreSettings, 'vbam_gbcoloroption', system, 'gbcoloroption_gbc', default='disabled')

    if system.name == 'gba':
        # GBA: Solar sensor level, Boktai 1: The Sun is in Your Hand
        _set_from_system(coreSettings, 'vbam_solarsensor', system, 'solarsensor', default='0')

        # GBA: Sensor Sensitivity (Gyroscope) (%)
        _set_from_system(coreSettings, 'vbam_gyro_sensitivity', system, 'gyro_sensitivity', default='10')

        # GBA: Sensor Sensitivity (Tilt) (%)
        _set_from_system(coreSettings, 'vbam_tilt_sensitivity', system, 'tilt_sensitivity', default='10')


# Nintendo NES / Famicom Disk System
def _nestopia_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # gun
    _set(coreSettings, 'nestopia_zapper_device', 'lightgun' if system.config.use_guns and guns else 'mouse') # Mouse mode for Zapper

    # gun cross
    _set_from_system(coreSettings, 'nestopia_show_crosshair', system, 'nestopia_show_crosshair', default='enabled' if guns_need_crosses(guns) else 'disabled')

    # Reduce Sprite Flickering
    _set_from_system(coreSettings, 'nestopia_nospritelimit', system, default='enabled')

    # Crop Overscan
    match system.config.get('nestopia_cropoverscan'):
        case "none":
            overscan_h = '0'
            overscan_v = '0'
        case "h":
            overscan_h = '8'
            overscan_v = '0'
        case "both":
            overscan_h = '8'
            overscan_v = '8'
        case _:
            overscan_h = '0'
            overscan_v = '8'
    _set(coreSettings, 'nestopia_overscan_h_left', overscan_h)
    _set(coreSettings, 'nestopia_overscan_h_right', overscan_h)
    _set(coreSettings, 'nestopia_overscan_v_top', overscan_v)
    _set(coreSettings, 'nestopia_overscan_v_bottom', overscan_v)

    # Palette Choice
    _set_from_system(coreSettings, 'nestopia_palette', system, 'nestopia_palette', default='consumer')

    # NTSC Filter
    _set_from_system(coreSettings, 'nestopia_blargg_ntsc_filter', system, 'nestopia_blargg_ntsc_filter', default='disabled')

    # CPU Overclock
    _set_from_system(coreSettings, 'nestopia_overclock', system, 'nestopia_overclock', default='1x')

    # 4 Player Adapter
    adapter = system.config.get('nestopia_select_adapter', 'automatic')
    _set(coreSettings, 'nestopia_select_adapter', 'auto' if adapter == 'automatic' else adapter)


def _fceumm_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # gun
    _set(coreSettings, 'fceumm_zapper_mode', 'lightgun' if system.config.use_guns and guns else 'mouse') # FCEumm Mouse mode for Zapper

    # gun cross
    _set_from_system(coreSettings, 'fceumm_show_crosshair', system, 'fceumm_show_crosshair', default='enabled' if guns_need_crosses(guns) else 'disabled')

    # Reduce Sprite Flickering
    _set_from_system(coreSettings, 'fceumm_nospritelimit', system, default='enabled')

    # Crop Overscan
    match system.config.get('fceumm_cropoverscan'):
        case "none":
            overscan_h = '0'
            overscan_v = '0'
        case "h":
            overscan_h = '8'
            overscan_v = '0'
        case "both":
            overscan_h = '8'
            overscan_v = '8'
        case _:
            overscan_h = '0'
            overscan_v = '8'
    _set(coreSettings, 'fceumm_overscan_h_left', overscan_h)
    _set(coreSettings, 'fceumm_overscan_h_right', overscan_h)
    _set(coreSettings, 'fceumm_overscan_v_top', overscan_v)
    _set(coreSettings, 'fceumm_overscan_v_bottom', overscan_v)

    # Palette Choice
    _set_from_system(coreSettings, 'fceumm_palette', system, 'fceumm_palette', default='default')

    # NTSC Filter
    _set_from_system(coreSettings, 'fceumm_ntsc_filter', system, 'fceumm_ntsc_filter', default='disabled')

    # Sound Quality
    _set_from_system(coreSettings, 'fceumm_sndquality', system, 'fceumm_sndquality', default='Low')

    # PPU Overclocking
    _set_from_system(coreSettings, 'fceumm_overclocking', system, 'fceumm_overclocking', default='disabled')


def _mesen_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    _set_from_system(coreSettings, 'mesen_region', system, 'mesen_region', default='Auto')

    # Screen rotation (for homebrew)
    _set_from_system(coreSettings, 'mesen_screenrotation', system, 'mesen_screenrotation', default='None')

    # NTSC Filter
    _set_from_system(coreSettings, 'mesen_ntsc_filter', system, 'mesen_ntsc_filter', default='Disabled')

    # Sprite limit removal
    _set_from_system(coreSettings, 'mesen_nospritelimit', system, 'mesen_nospritelimit', default='disabled')

    # Palette
    _set_from_system(coreSettings, 'mesen_palette', system, 'mesen_palette', default='Default')

    # HD texture replacements
    _set_from_system(coreSettings, 'mesen_hdpacks', system, 'mesen_hdpacks', default='enabled')

    # FDS Auto-insert side A
    _set_from_system(coreSettings, 'mesen_fdsautoinsertdisk', system, 'mesen_fdsautoinsertdisk', default='disabled')

    # FDS Fast forward floppy disk loading
    _set_from_system(coreSettings, 'mesen_fdsfastforwardload', system, 'mesen_fdsfastforwardload', default='disabled')

    # RAM init state (speedrunning)
    _set_from_system(coreSettings, 'mesen_ramstate', system, 'mesen_ramstate', default='All 0s (Default)')

    # NES CPU Overclock
    _set_from_system(coreSettings, 'mesen_overclock', system, 'mesen_overclock', default='None')

    # Overclocking type (compatibility)
    _set_from_system(coreSettings, 'mesen_overclock_type', system, 'mesen_overclock_type', default='Before NMI (Recommended)')


# Nintendo Pokemon Mini
def _pokemini_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # LCD Filter
    _set_from_system(coreSettings, 'pokemini_lcdfilter', system, 'pokemini_lcdfilter', default='dotmatrix')

    # LCD Ghosting Effects
    _set_from_system(coreSettings, 'pokemini_lcdmode', system, 'pokemini_lcdmode', default='analog')


# Nintendo SNES
def _snes9x_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Reduce sprite flickering (Hack, Unsafe)
    _set_from_system(coreSettings, 'snes9x_reduce_sprite_flicker', system, 'reduce_sprite_flicker', default='enabled')

    # Reduce Slowdown (Hack, Unsafe)
    _set_from_system(coreSettings, 'snes9x_overclock_cycles', system, 'reduce_slowdown', default='disabled')

    # SuperFX Overclocking
    _set_from_system(coreSettings, 'snes9x_overclock_superfx', system, 'overclock_superfx', default='100%')

    # Hi-Res Blending
    _set_from_system(coreSettings, 'snes9x_hires_blend', system, 'hires_blend', default='disabled')

    # Blargg NTSC Filter
    _set_from_system(coreSettings, 'snes9x_blargg', system, 'snes9x_blargg_filter', default='disabled')

    # Crosshair
    crosshair = system.config.get('superscope_crosshair') or ('2' if guns_need_crosses(guns) else '0')
    _set(coreSettings, 'snes9x_superscope_crosshair', crosshair)
    _set(coreSettings, 'snes9x_justifier1_crosshair', crosshair)
    _set(coreSettings, 'snes9x_justifier2_crosshair', crosshair)
    _set(coreSettings, 'snes9x_rifle_crosshair', crosshair)

    if system.config.use_guns and guns:
        _set(coreSettings, 'snes9x_superscope_reverse_buttons', 'disabled')


def _snes9x_next_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Reduce sprite flickering (Hack, Unsafe)
    _set_from_system(coreSettings, 'snes9x_2010_reduce_sprite_flicker', system, '2010_reduce_sprite_flicker', default='enabled')

    # Reduce Slowdown (Hack, Unsafe)
    _set_from_system(coreSettings, 'snes9x_2010_overclock_cycles', system, '2010_reduce_slowdown', default='disabled')

    # SuperFX Overclocking
    _set_from_system(coreSettings, 'snes9x_2010_overclock', system, '2010_overclock_superfx', default='10 MHz (Default)')

    # Blargg NTSC Filter
    _set_from_system(coreSettings, 'snes9x_2010_blargg', system, 'snes9x_2010_blargg_filter', default='disabled')

    # Crosshair
    _set_from_system(coreSettings, 'snes9x_2010_superscope_crosshair', system, 'superscope_crosshair', default='2' if guns_need_crosses(guns) else 'disabled')


# TODO: Add CORE options for BSnes and PocketSNES
def _bsnes_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    if system.config.use_guns and guns:
        _set(coreSettings, 'bsnes_touchscreen_lightgun_superscope_reverse', 'OFF')

    # Video Filters
    _set_from_system(coreSettings, 'bsnes_video_filter', system, 'bsnes_video_filter', default='disabled')


# Nintendo SNES/GB/GBC/SGB
def _mesen_s_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Force appropriate Game Boy mode for the system (unless overriden)
    gbmodel = system.config.get('mesen-s_gbmodel')
    if gbmodel is system.config.MISSING:
        if system.name == 'sgb':
            gbmodel = 'Super Game Boy'
        elif system.name == 'gb':
            gbmodel = 'Game Boy'
        elif system.name == 'gbc':
            gbmodel = 'Game Boy Color'
        else:
            gbmodel = 'Auto'
    _set(coreSettings, 'mesen-s_gbmodel', gbmodel)

    # SGB2 Enable
    _set_from_system(coreSettings, 'mesen-s_sgb2', system, 'mesen-s_sgb2', default='enabled')

    # NTSC Filter
    _set_from_system(coreSettings, 'mesen-s_ntsc_filter', system, 'mesen-s_ntsc_filter', default='disabled')

    # Blending for high-res mode (Kirby's Dream Land 3 pseudo-transparency)
    _set_from_system(coreSettings, 'mesen-s_blend_high_res', system, 'mesen-s_blend_high_res', default='disabled')

    # Change sound interpolation to cubic
    _set_from_system(coreSettings, 'mesen-s_cubic_interpolation', system, 'mesen-s_cubic_interpolation', default='disabled')

    # SNES CPU Overclock
    _set_from_system(coreSettings, 'mesen-s_overclock', system, 'mesen-s_overclock', default='None')

    # Overclocking type (compatibility)
    _set_from_system(coreSettings, 'mesen-s_overclock_type', system, 'mesen-s_overclock_type', default='Before NMI')

    # SuperFX Overclock
    _set_from_system(coreSettings, 'mesen-s_superfx_overclock', system, 'mesen-s_superfx_overclock', default='100%')


# Nintendo Virtual Boy
def _vb_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # 2D Color Mode
    _set_from_system(coreSettings, 'vb_color_mode', system, '2d_color_mode', default='black & red')

    # 3D Glasses Color Mode
    _set_from_system(coreSettings, 'vb_anaglyph_preset', system, '3d_color_mode', default='disabled')


# Panasonic 3DO
def _opera_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Audio Process on separate CPU thread
    _set(coreSettings, 'opera_dsp_threaded', 'enabled')

    # High Resolution (640x480)
    _set_from_system(coreSettings, 'opera_high_resolution', system, 'high_resolution', default='enabled')

    # CPU Overclock
    _set_from_system(coreSettings, 'opera_cpu_overclock', system, 'cpu_overclock', default='1.0x (12.50Mhz)')

    # Active Input Devices Fix
    _set_from_system(coreSettings, 'opera_active_devices', system, 'active_devices', default='1')

    # Additional game fixes
    timing_1 = 'disabled'
    timing_3 = 'disabled'
    timing_5 = 'disabled'
    timing_6 = 'disabled'

    match system.config.get('game_fixes_opera'):
        case 'timing_hack1':
            timing_1 = 'enabled'
        case 'timing_hack3':
            timing_3 = 'enabled'
        case 'timing_hack5':
            timing_5 = 'enabled'
        case 'timing_hack6':
            timing_6 = 'enabled'

    _set(coreSettings, 'opera_hack_timing_1',    timing_1)
    _set(coreSettings, 'opera_hack_timing_3',    timing_3)
    _set(coreSettings, 'opera_hack_timing_5',    timing_5)
    _set(coreSettings, 'opera_hack_timing_6',    timing_6)

    # Shared nvram
    # If ROM includes the word Disc, assume it's a multi disc game, and enable shared nvram if the option isn't set.
    storage = system.config.get('opera_nvram_storage')

    if not storage:
        storage = 'shared' if 'disc' in str(rom).casefold() else 'per game'

    _set(coreSettings, 'opera_nvram_storage', storage)


# Rick Dangerous
def _xrick_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Crop Borders
    _set_from_system_bool(coreSettings, 'xrick_crop_borders', system, default=True, values=('enabled', 'disabled'))

    # Cheat 1 (Trainer Mode)
    _set_from_system_bool(coreSettings, 'xrick_cheat1', system, values=('enabled', 'disabled'))

    # Cheat 2 (Invulnerablilty Mode)
    _set_from_system_bool(coreSettings, 'xrick_cheat2', system, values=('enabled', 'disabled'))

    # Cheat 3 (Expose Mode)
    _set_from_system_bool(coreSettings, 'xrick_cheat3', system, values=('enabled', 'disabled'))


# ScummVM CORE Options
def _scummvm_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Analog Deadzone
    _set_from_system(coreSettings, 'scummvm_analog_deadzone', system, 'scummvm_analog_deadzone', default='15')

    # Gamepad Cursor Speed
    _set_from_system(coreSettings, 'scummvm_gamepad_cursor_speed', system, 'scummvm_gamepad_cursor_speed', default='1.0')

    # Speed Hack (safe)
    _set_from_system(coreSettings, 'scummvm_speed_hack', system, 'scummvm_speed_hack', default='enabled')


# Sega Dreamcast / Atomiswave / Naomi
def _flycast_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # force vmu all, to save in saves (otherwise, it saves in game_dir, which is bios)
    _set(coreSettings, 'reicast_per_content_vmus',  'All VMUs')

    # Synchronous rendering
    _set_from_system(coreSettings, 'reicast_synchronous_rendering', system, 'reicast_synchronous_rendering', default='enabled')

    # DSP audio
    _set_from_system(coreSettings, 'reicast_enable_dsp', system, 'reicast_dsp', default='disabled')

    # Threaded Rendering
    _set(coreSettings, 'reicast_threaded_rendering',  'enabled')

    # Enable controller force feedback
    _set(coreSettings, 'reicast_enable_purupuru',  'enabled')

    # Crossbar Colors
    need_crosses = guns_need_crosses(guns)
    _set_from_system(coreSettings, 'reicast_lightgun1_crosshair', system, 'reicast_lightgun1_crosshair', default='Red' if need_crosses else 'disabled')
    _set_from_system(coreSettings, 'reicast_lightgun2_crosshair', system, 'reicast_lightgun2_crosshair', default='Blue' if need_crosses else 'disabled')
    _set_from_system(coreSettings, 'reicast_lightgun3_crosshair', system, 'reicast_lightgun3_crosshair', default='Green' if need_crosses else 'disabled')
    _set_from_system(coreSettings, 'reicast_lightgun4_crosshair', system, 'reicast_lightgun4_crosshair', default='White' if need_crosses else 'disabled')

    # Video resolution
    _set_from_system(coreSettings, 'reicast_internal_resolution', system, 'reicast_internal_resolution', default='640x480')

    # Textures Mip-mapping (blur)
    _set_from_system(coreSettings, 'reicast_mipmapping', system, 'reicast_mipmapping', default='disabled')

    # Anisotropic Filtering
    _set_from_system(coreSettings, 'reicast_anisotropic_filtering', system, 'reicast_anisotropic_filtering', default='off')

    # Texture Upscaling (xBRZ)
    _set_from_system(coreSettings, 'reicast_texupscale', system, 'reicast_texupscale', default='1')

    # Frame Skip
    _set_from_system(coreSettings, 'reicast_frame_skipping', system, 'reicast_frame_skipping', default='disabled')

    # Force Windows CE Mode
    _set_from_system(coreSettings, 'reicast_force_wince', system, 'reicast_force_wince', default='disabled')

    # Widescreen Cheat
    if (
        system.config.get('reicast_widescreen_cheats') == 'enabled'
        and system.config.get('ratio') == '16/9'
        and system.config.get('bezel') == 'none'
    ):
        widescreen_cheat = 'enabled'
    else:
        widescreen_cheat = 'disabled'

    _set(coreSettings, 'reicast_widescreen_cheats', widescreen_cheat)

    # Widescreen Hack (prefer Cheat)
    if (
        system.config.get('reicast_widescreen_hack') == 'enabled'
        and system.config.get('ratio') == '16/9'
        and system.config.get('bezel') == 'none'
        and system.config.get('reicast_widescreen_cheats') == 'disabled'
    ):
        widescreen_hack = 'enabled'
    else:
        widescreen_hack = 'disabled'

    _set(coreSettings, 'reicast_widescreen_hack', widescreen_hack)

    # Bios
    _set_from_system(coreSettings, 'reicast_language', system, 'reicast_language', default='Default')
    _set_from_system(coreSettings, 'reicast_region', system, 'reicast_region', default='Default')

    ## Atomiswave / Naomi

    # Screen Orientation
    if system.name == 'atomiswave':
        rotation = system.config.get('screen_rotation_atomiswave', 'horizontal')
    elif system.name == 'naomi':
        rotation = system.config.get('screen_rotation_naomi', 'horizontal')
    else:
        rotation = 'horizontal'

    _set(coreSettings, 'reicast_screen_rotation', rotation)

    # wheel
    _set(coreSettings, 'reicast_analog_stick_deadzone', '0%' if system.config.use_wheels and wheels else '15%')  # 15% = default value


# Sega SG1000 / Master System / Game Gear / Megadrive / Mega CD
def _genesisplusgx_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Allows each game to have its own one brm file for save without lack of space
    _set(coreSettings, 'genesis_plus_gx_system_bram', 'per game')

    # Sometimes needs to be forced to NTSC-U for MSU-MD to work (this is to avoid an intentionally coded lock-out screen):
    # https://arcadetv.github.io/msu-md-patches/wiki/Lockout-screen.html
    _set_from_system(coreSettings, 'genesis_plus_region_detect', system, 'gpgx_region', default='auto')

    # Reduce sprite flickering
    _set_from_system(coreSettings, 'genesis_plus_gx_no_sprite_limit', system, 'gpgx_no_sprite_limit', default='disabled')

    # Blargg NTSC filter
    if system.name == 'megadrive':
        ntsc_filter = system.config.get('gpgx_blargg_filter_md', 'Off')
    elif system.name == 'mastersystem':
        ntsc_filter = system.config.get('gpgx_blargg_filter_ms', 'Off')
    else:
        ntsc_filter = 'Off'

    _set(coreSettings, 'genesis_plus_gx_blargg_ntsc_filter', ntsc_filter)

    # Show Lightgun Crosshair
    if (system.name == 'megadrive' and (cursor := system.config.get('gun_cursor_md'))) or (system.name == 'mastersystem' and (cursor := system.config.get('gun_cursor_ms'))):
        gun_cursor = cursor
    else:
        gun_cursor = 'enabled' if guns_need_crosses(guns) else 'disabled'

    _set(coreSettings, 'genesis_plus_gx_gun_cursor', gun_cursor)

    # Megadrive FM (YM2612)
    _set_from_system(coreSettings, 'genesis_plus_gx_ym2612', system, 'gpgx_fm', default='mame (ym2612)')

    # system.name == 'mastersystem'
    # Master System FM (YM2413)
    ym2413 = system.config.get('ym2413', 'automatic')
    _set(coreSettings, 'genesis_plus_gx_ym2413', 'auto' if ym2413 == 'automatic' else ym2413)

    # system.name == 'gamegear'
    # Game Gear LCD Ghosting Filter
    _set_from_system(coreSettings, 'genesis_plus_gx_lcd_filter', system, 'lcd_filter', default='disabled')

    # Game Gear Extended Screen
    _set_from_system(coreSettings, 'genesis_plus_gx_gg_extra', system, 'gg_extra', default='disabled')

    # system.name == 'msu-md'
    # MSU-MD/MegaCD

    # Needs to be forced to sega/mega cd for MSU-MD to work.
    add_on = system.config.get('gpgx_cd_add_on', 'sega/mega cd' if system.name == 'msu-md' else 'auto')
    _set(coreSettings, 'genesis_plus_gx_add_on', add_on)

    # Volume setting is actually important, unlike MegaCD the MSU-MD is pre-amped at a different rate.
    # That is, the default level 100 will make the CD audio drown out the cartridge sound effects.
    cdda_volume = system.config.get('gpgx_cdda_volume', '70' if system.name == 'msu-md' else '100')
    _set(coreSettings, 'genesis_plus_gx_cdda_volume', cdda_volume)

    # gun
    if system.config.use_guns and guns:
        coreSettings.save('genesis_plus_gx_gun_input', '"lightgun"')


# Sega 32X (Sega Megadrive / MegaCD / Master System)
def _picodrive_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Reduce sprite flickering
    _set_from_system(coreSettings, 'picodrive_sprlim', system, default='enabled')

    # Crop Overscan: the setting in picodrive shows overscan when enabled
    _set_from_system_bool(coreSettings, 'picodrive_overscan', system, 'picodrive_cropoverscan', default=True, values=('disabled', 'enabled'))

    # 6 Button Controller 1
    _set_from_system(coreSettings, 'picodrive_input1', system, 'picodrive_controller1', default='6 button pad')

    # 6 Button Controller 2
    _set_from_system(coreSettings, 'picodrive_input2', system, 'picodrive_controller2', default='6 button pad')

    # Sega MegaCD
    # Emulate the Backup RAM Cartridge for games save (ex: Shining Force CD)
    _set(coreSettings, 'picodrive_ramcart', 'enabled' if system.name == 'megacd' else 'disabled')


# Sega Saturn
def _yabasanshiro_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Video Resolution
    _set_from_system(coreSettings, 'yabasanshiro_resolution_mode', system, 'resolution_mode', default='original')

    # Multitap
    port1 = 'disabled'
    port2 = 'disabled'

    match system.config.get('multitap_yabasanshiro'):
        case 'port1':
            port1 = 'enabled'
        case 'port2':
            port2 = 'enabled'
        case 'port12':
            port1 = 'enabled'
            port2 = 'enabled'

    _set(coreSettings, 'yabasanshiro_multitap_port1', port1)
    _set(coreSettings, 'yabasanshiro_multitap_port2', port2)

    # Language
    _set_from_system(coreSettings, 'yabasanshiro_system_language', system, 'yabasanshiro_language', default='english')


def _kronos_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Set best OpenGL renderer
    _set(coreSettings, 'kronos_videocoretype', 'opengl_cs')

    # Video Resolution
    _set_from_system(coreSettings, 'kronos_resolution_mode', system, 'kronos_resolution', default='original')

    # Mesh mode
    _set_from_system(coreSettings, 'kronos_meshmode', system, 'kronos_meshmode', default='disabled')

    # Banding mode
    _set_from_system(coreSettings, 'kronos_bandingmode', system, 'kronos_bandingmode', default='disabled')

    # Share saves with Beetle
    _set_from_system(coreSettings, 'kronos_use_beetle_saves', system, default='enabled')

    # Multitap
    port1 = 'disabled'
    port2 = 'disabled'

    match system.config.get('kronos_multitap'):
        case 'port1':
            port1 = 'enabled'
        case 'port2':
            port2 = 'enabled'
        case 'port12':
            port1 = 'enabled'
            port2 = 'enabled'

    _set(coreSettings, 'kronos_multitap_port1', port1)
    _set(coreSettings, 'kronos_multitap_port2', port2)

    # BIOS langauge
    _set_from_system(coreSettings, 'kronos_language_id', system, 'kronos_language_id', default='English')


def _beetle_saturn_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # gun cross / wheel
    # gun
    _set_from_system(coreSettings, 'beetle_saturn_virtuagun_crosshair', system, 'beetle-saturn_crosshair', default='Cross' if guns_need_crosses(guns) else 'Off')

    # wheel
    _set(coreSettings, 'beetle_saturn_analog_stick_deadzone', '0%' if system.config.use_wheels and wheels else '15%')


# Sharp X68000
def _px68k_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Fresh config file
    keropi_config = BIOS / 'keropi' / 'config'
    keropi_sram = BIOS / 'keropi' / 'sram.dat'
    for f in [ keropi_config, keropi_sram ]:
        if f.exists():
            f.unlink()
    with keropi_config.open("w") as fd:
        fd.write("[WinX68k]\n")
        fd.write(f"StartDir={ROMS / 'x68000'}\n")

    # To auto launch HDD games
    _set(coreSettings, 'px68k_disk_path', 'disabled')

    # CPU Speed (Overclock)
    _set_from_system(coreSettings, 'px68k_cpuspeed', system, 'px68k_cpuspeed', default='33Mhz (OC)')

    # RAM Size
    _set_from_system(coreSettings, 'px68k_ramsize', system, 'px68k_ramsize', default='12MB')

    # Frame Skip
    _set_from_system(coreSettings, 'px68k_frameskip', system, 'px68k_frameskip', default='Full Frame')

    # Joypad Type for two players
    joytype = system.config.get('px68k_joytype', 'Default (2 Buttons)')
    _set(coreSettings, 'px68k_joytype1', joytype)
    _set(coreSettings, 'px68k_joytype2', joytype)

# Sinclair ZX81
def _81_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Tape Fast Load
    _set(coreSettings, '81_fast_load', 'enabled')
    # Enables sound emulatio
    _set(coreSettings, '81_sound',     'Zon X-81')
    # Colorisation (Chroma 81)
    if chroma := system.config.get('81_chroma_81'):
        if chroma == "automatic":
            _set(coreSettings, '81_chroma_81', 'auto')
        else:
            _set(coreSettings, '81_chroma_81', chroma)
    else:
        _set(coreSettings, '81_chroma_81', 'enabled')
    # High Resolution
    if hires := system.config.get('81_highres'):
        if hires == "automatic":
            _set(coreSettings, '81_highres', 'auto')
        else:
            _set(coreSettings, '81_highres', hires)
    else:
        _set(coreSettings, '81_highres', 'WRX')


# Sinclair ZX Spectrum
def _fuse_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # The most common configuration same as ZX Spectrum+
    _set_from_system(coreSettings, 'fuse_machine', system, 'fuse_machine', default='Spectrum 128K')

    # Zoom, Hide Video Border
    _set_from_system(coreSettings, 'fuse_hide_border', system, 'fuse_hide_border', default='disabled')


# SNK Neogeo AES MVS / Neogeo CD
def _fbneo_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Diagnostic input
    _set(coreSettings, 'fbneo-diagnostic-input', 'Start + L + R')

    # Allow RetroAchievements in hardcore mode with FBNeo
    _set(coreSettings, 'fbneo-allow-patched-romsets', 'disabled')

    # CPU Clock
    _set_from_system(coreSettings, 'fbneo-cpu-speed-adjust', system, 'fbneo-cpu-speed-adjust', default='100%')

    # Frameskip
    _set_from_system(coreSettings, 'fbneo-frameskip', system, 'fbneo-frameskip', default='0')

    # Crosshair (Lightgun)
    _set_from_system(coreSettings, 'fbneo-lightgun-crosshair-emulation', system, default='always show' if guns_need_crosses(guns) else 'always hide')
    _set(coreSettings, f"fbneo-dipswitch-{rom.stem}-Controls", 'Light Gun' if system.config.use_guns and guns else 'Joystick')

    # NEOGEO
    if system.name == 'neogeo':
        # Neogeo Mode
        if mode_switch := system.config.get('fbneo-neogeo-mode-switch'):
            _set(coreSettings, "fbneo-neogeo-mode", 'DIPSWITCH')
            if mode_switch == 'MVS Asia/Europe':
                _set(coreSettings, f"fbneo-dipswitch-{rom.stem}-BIOS",  'MVS Asia/Europe ver. 5 (1 slot)')
            elif mode_switch == 'MVS USA':
                _set(coreSettings, f"fbneo-dipswitch-{rom.stem}-BIOS",  'MVS USA ver. 5 (2 slot)')
            elif mode_switch == 'MVS Japan':
                _set(coreSettings, f"fbneo-dipswitch-{rom.stem}-BIOS",  'MVS Japan ver. 5 (? slot)')
            elif mode_switch == 'AES Asia':
                _set(coreSettings, f"fbneo-dipswitch-{rom.stem}-BIOS",  'AES Asia')
            elif mode_switch == 'AES Japan':
                _set(coreSettings, f"fbneo-dipswitch-{rom.stem}-BIOS",  'AES Japan')
            else:
                _set(coreSettings, "fbneo-neogeo-mode", 'UNIBIOS')
        else:
            _set(coreSettings, "fbneo-neogeo-mode",     'UNIBIOS')
            # _set(coreSettings, f"fbneo-dipswitch-{rom.stem}-BIOS",      'Universe BIOS ver. 4.0')
        # Memory card mode
        _set_from_system(coreSettings, 'fbneo-memcard-mode', system, 'fbneo-memcard-mode', default='per-game')


# SNK Neogeo CD
def _neocd_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Console region
    _set_from_system(coreSettings, 'neocd_region', system, 'neocd_region', default='Japan')

    # BIOS Select
    _set_from_system(coreSettings, 'neocd_bios', system, 'neocd_bios', default='neocd_z.rom (CDZ)')

    # Per-Game saves
    _set_from_system_bool(coreSettings, 'neocd_per_content_saves', system, default=True, values=('On', 'Off'))


# Sony PSP
def _ppsspp_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    _set_from_system(coreSettings, 'ppsspp_internal_resolution', system, 'ppsspp_resolution', default='480x272')


# Sony PSX
def _mednafen_psx_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # CPU Frequency Scaling (Overclock)
    _set_from_system(coreSettings, 'beetle_psx_hw_cpu_freq_scale', system, 'beetle_psx_hw_cpu_freq_scale', default='110%') # If not 110% NO options are working!

    # Show official Bootlogo
    _set_from_system(coreSettings, 'beetle_psx_hw_skip_bios', system, 'beetle_psx_hw_skip_bios', default='disabled')

    # Video Resolution
    _set_from_system(coreSettings, 'beetle_psx_hw_internal_resolution', system, 'beetle_psx_hw_internal_resolution', default='1x(native)')

    # Widescreen Hack
    if system.config.get('beetle_psx_hw_widescreen_hack') == 'enabled' and system.config.get('ratio') == "16/9" and system.config.get('bezel') == "none":
        _set(coreSettings, 'beetle_psx_hw_widescreen_hack', 'enabled')
    else:
        _set(coreSettings, 'beetle_psx_hw_widescreen_hack', 'disabled')

    # Frame Duping (Speedup)
    _set_from_system(coreSettings, 'beetle_psx_hw_frame_duping', system, 'beetle_psx_hw_frame_duping', default='disabled')

    # CPU Dynarec (Speedup)
    _set_from_system(coreSettings, 'beetle_psx_hw_cpu_dynarec', system, 'beetle_psx_hw_cpu_dynarec', default='disabled')

    # Dynarec Code Invalidation
    _set_from_system(coreSettings, 'beetle_psx_hw_dynarec_invalidate', system, 'beetle_psx_hw_dynarec_invalidate', default='full')

    # Analog Stick self calibration
    _set(coreSettings, 'beetle_psx_hw_analog_calibration', 'enabled')

    # Multitap
    match system.config.get('multitap_mednafen'):
        case 'port1':
            _set(coreSettings, 'beetle_psx_hw_enable_multitap_port1', 'enabled')
            _set(coreSettings, 'beetle_psx_hw_enable_multitap_port2', 'disabled')
        case 'port2':
            _set(coreSettings, 'beetle_psx_hw_enable_multitap_port1', 'disabled')
            _set(coreSettings, 'beetle_psx_hw_enable_multitap_port2', 'enabled')
        case 'port12':
            _set(coreSettings, 'beetle_psx_hw_enable_multitap_port1', 'enabled')
            _set(coreSettings, 'beetle_psx_hw_enable_multitap_port2', 'enabled')
        case _:
            _set(coreSettings, 'beetle_psx_hw_enable_multitap_port1', 'disabled')
            _set(coreSettings, 'beetle_psx_hw_enable_multitap_port2', 'disabled')


def _duckstation_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # renderer
    if system.config.get_bool("gpu_software"):
        _set(coreSettings, 'swanstation_GPU_Renderer', 'Software')
    else:
        if gfxbackend := system.config.get("gfxbackend"):
            if gfxbackend == "vulkan":
                _set(coreSettings, 'swanstation_GPU_Renderer', 'Vulkan')
            elif gfxbackend == "gl" or gfxbackend == "glcore":
                _set(coreSettings, 'swanstation_GPU_Renderer', 'OpenGL')
            else:
                _set(coreSettings, 'swanstation_GPU_Renderer', 'Auto')
        else:
            _set(coreSettings, 'swanstation_GPU_Renderer', 'Auto')

    # Show official Bootlogo
    _set_from_system(coreSettings, 'swanstation_BIOS_PatchFastBoot', system, 'swanstation_PatchFastBoot', default='false')

    # Video Resolution
    _set_from_system(coreSettings, 'swanstation_GPU_ResolutionScale', system, 'swanstation_resolution_scale', default='1')

    # PGXP Geometry Correction
    _set_from_system(coreSettings, 'swanstation_GPU_PGXPEnable', system, 'swanstation_pgxp', default='true')

    # Anti-aliasing (MSAA/SSAA)
    _set_from_system(coreSettings, 'swanstation_GPU_MSAA', system, 'swanstation_antialiasing', default='1')

    # Texture Filtering
    _set_from_system(coreSettings, 'swanstation_GPU_TextureFilter', system, 'swanstation_texture_filtering', default='Nearest')

    # Widescreen Hack
    if system.config.get('swanstation_widescreen_hack') == 'true' and system.config.get('ratio') == "16/9" and system.config.get('bezel') == "none":
        _set(coreSettings, 'swanstation_GPU_WidescreenHack',  'true')
        _set(coreSettings, 'swanstation_Display_AspectRatio', '16:9')
    else:
        _set(coreSettings, 'swanstation_GPU_WidescreenHack',  'false')
        _set(coreSettings, 'swanstation_Display_AspectRatio', '4:3')

    # Crop Mode
    _set_from_system(coreSettings, 'swanstation_Display_CropMode', system, 'swanstation_CropMode', default='Overscan')

    # Gun crosshairs
    _set_from_system(coreSettings, 'swanstation_Controller_ShowCrosshair', system, 'swanstation_Controller_ShowCrosshair', default='true' if guns_need_crosses(guns) else 'false')


def _pcsx2_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Fast Boot
    _set_from_system(coreSettings, 'pcsx2_fast_boot', system, 'lr_pcsx2_fast_boot', default='disabled')


def _pcsx_rearmed_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Display Games Hack Options
    _set(coreSettings, 'pcsx_rearmed_show_gpu_peops_settings', 'enabled')

    # Display Multitap/Gamepad Options
    _set(coreSettings, 'pcsx_rearmed_show_other_input_settings', 'enabled')

    # Enable Vibration
    _set(coreSettings, 'pcsx_rearmed_vibration', 'enabled')

    # Show Bios Bootlogo (Breaks some games)
    _set_from_system(coreSettings, 'pcsx_rearmed_show_bios_bootlogo', system, 'show_bios_bootlogo', default='disabled')

    # Frameskip
    _set_from_system(coreSettings, 'pcsx_rearmed_frameskip', system, 'frameskip_pcsx', default='0')

    # Enhanced resolution at the cost of lower performance
    match system.config.get('neon_enhancement'):
        case 'enabled':
            _set(coreSettings, 'pcsx_rearmed_neon_enhancement_enable',  'enabled')
            _set(coreSettings, 'pcsx_rearmed_neon_enhancement_no_main', 'disabled')
        case 'enabled_with_speedhack':
            _set(coreSettings, 'pcsx_rearmed_neon_enhancement_enable',  'enabled')
            _set(coreSettings, 'pcsx_rearmed_neon_enhancement_no_main', 'enabled')
        case _:
            _set(coreSettings, 'pcsx_rearmed_neon_enhancement_enable',  'disabled')
            _set(coreSettings, 'pcsx_rearmed_neon_enhancement_no_main', 'disabled')

    # Multitap
    _set_from_system(coreSettings, 'pcsx_rearmed_multitap', system, 'pcsx_rearmed_multitap', default='disabled')

    # Additional game fixes
    _set(coreSettings, 'pcsx_rearmed_idiablofix',                    'disabled')
    _set(coreSettings, 'pcsx_rearmed_pe2_fix',                       'disabled')
    _set(coreSettings, 'pcsx_rearmed_inuyasha_fix',                  'disabled')
    _set(coreSettings, 'pcsx_rearmed_gpu_peops_odd_even_bit',        'disabled')
    _set(coreSettings, 'pcsx_rearmed_gpu_peops_expand_screen_width', 'disabled')
    _set(coreSettings, 'pcsx_rearmed_gpu_peops_ignore_brightness',   'disabled')
    _set(coreSettings, 'pcsx_rearmed_gpu_peops_lazy_screen_update',  'disabled')
    _set(coreSettings, 'pcsx_rearmed_gpu_peops_repeated_triangles',  'disabled')
    if (fixes := system.config.get('game_fixes_pcsx')) != 'disabled':
        if fixes == 'Diablo_Music_Fix':
            _set(coreSettings, 'pcsx_rearmed_idiablofix',                    'enabled')
        elif fixes == 'Parasite_Eve':
            _set(coreSettings, 'pcsx_rearmed_pe2_fix',                       'enabled')
        elif fixes == 'InuYasha_Sengoku':
            _set(coreSettings, 'pcsx_rearmed_inuyasha_fix',                  'enabled')
        elif fixes == 'Chrono_Chross':
            _set(coreSettings, 'pcsx_rearmed_gpu_peops_odd_even_bit',        'enabled')
        elif fixes == 'Capcom_fighting':
            _set(coreSettings, 'pcsx_rearmed_gpu_peops_expand_screen_width', 'enabled')
        elif fixes == 'Lunar':
            _set(coreSettings, 'pcsx_rearmed_gpu_peops_ignore_brightness',   'enabled')
        elif fixes == 'Pandemonium':
            _set(coreSettings, 'pcsx_rearmed_gpu_peops_lazy_screen_update',  'enabled')
        elif fixes == 'Dark_Forces':
            _set(coreSettings, 'pcsx_rearmed_gpu_peops_repeated_triangles',  'enabled')

    # gun cross
    # Crossbar Colors
    need_crosses = guns_need_crosses(guns)
    for player, color in enumerate(["red", "blue"], start=1):
        _set_from_system(coreSettings, f'pcsx_rearmed_crosshair{player}', system, f'pcsx_rearmed_crosshair{player}', default=color if need_crosses else 'disabled')


# Thomson MO5 / TO7
def _theodore_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Auto run games
    _set(coreSettings, 'theodore_autorun',   'enabled')


# Watara SuperVision
def _potator_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Watara Color Palette
    _set_from_system(coreSettings, 'potator_palette', system, 'watara_palette', default='gameking')

    # Watara Ghosting
    _set_from_system(coreSettings, 'potator_lcd_ghosting', system, 'watara_ghosting', default='0')


## PORTs

# DOOM
def _prboom_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Internal resolution
    _set_from_system(coreSettings, 'prboom-resolution', system, 'prboom-resolution', default='320x200')


# QUAKE
def _tyrquake_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Resolution
    _set_from_system(coreSettings, 'tyrquake_resolution', system, 'tyrquake_resolution', default='640x480')

    # Frame rate
    framerate = system.config.get('tyrquake_framerate', 'automatic')
    _set(coreSettings, 'tyrquake_framerate', 'Auto' if framerate == 'automatic' else framerate)

    # Rumble
    _set_from_system(coreSettings, 'tyrquake_rumble', system, 'tyrquake_rumble', default='disabled')


# BOMBERMAN
def _mrboom_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Team mode
    _set_from_system(coreSettings, 'mrboom-aspect', system, 'mrboom-aspect', default='Native')


# HatariB
def _hatarib_options(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    # Defaults
    _set(coreSettings, 'hatarib_statusbar', '0')
    _set(coreSettings, 'hatarib_fast_floppy', '1')
    _set(coreSettings, 'hatarib_show_welcome', '0')
    _set(coreSettings, 'hatarib_tos', '<etos1024k>')

    # Machine Type
    _set_from_system(coreSettings, 'hatarib_machine', system, 'hatarib_machine', default='0')

    # Language/Region
    _set_from_system(coreSettings, 'hatarib_region', system, 'hatarib_language', default='127')

    # CPU
    _set_from_system(coreSettings, 'hatarib_cpu', system, 'hatarib_cpu', default='-1')

    # CPU Clock
    _set_from_system(coreSettings, 'hatarib_cpu_clock', system, 'hatarib_cpu_clock', default='-1')

    # ST Memory Size
    _set_from_system(coreSettings, 'hatarib_memory', system, 'hatarib_memory', default='1024')

    # Pause Screen
    _set_from_system(coreSettings, 'hatarib_pause_osk', system, 'hatarib_pause', default='2')

    # Aspect Ratio
    _set_from_system(coreSettings, 'hatarib_aspect', system, 'hatarib_ratio', default='0')

    # Borders
    _set_from_system(coreSettings, 'hatarib_borders', system, 'hatarib_borders', default='0')

    # Harddrive image support
    rom_extension = rom.suffix.lower()
    if rom_extension == '.hd':
        _set(coreSettings, 'hatarib_hardimg', 'hatarib/hdd')
        _set(coreSettings, 'hatarib_hardboot', '1')
        _set(coreSettings, 'hatarib_hard_readonly', '1')
        match system.config.get("hatarib_drive"):
            case "ACSI":
                _set(coreSettings, 'hatarib_hardtype', '2')
            case "SCSI":
                _set(coreSettings, 'hatarib_hardtype', '3')
            case _:
                _set(coreSettings, 'hatarib_hardtype', '4')
    elif rom_extension == '.gemdos':
        _set(coreSettings, 'hatarib_hardimg', 'hatarib/hdd')
        _set(coreSettings, 'hatarib_hardboot', '1')
        _set(coreSettings, 'hatarib_hardtype', '0')
        _set(coreSettings, 'hatarib_hard_readonly', '0')
    else:
        _set(coreSettings, 'hatarib_hardimg', None)
        _set(coreSettings, 'hatarib_hardtype', '0')
        _set(coreSettings, 'hatarib_hardboot', '0')
        _set(coreSettings, 'hatarib_hard_readonly', '1')


_option_functions: dict[str, Callable[[UnixSettings, Emulator, Path, Guns, DeviceInfoMapping], None]] = {
    'cap32': _cap32_options,
    'atari800': _atari800_options,
    'virtualjaguar': _virtualjaguar_options,
    'handy': _handy_options,
    'vice_x64': _vice_x64_options,
    'vice_x64sc': _vice_x64_options,
    'vice_xscpu64': _vice_x64_options,
    'vice_x128': _vice_x128_options,
    'vice_xplus4': _vice_xplus4_options,
    'vice_xvic': _vice_xvic_options,
    'vice_xpet': _vice_xpet_options,
    'puae': _puae_options,
    'puae2021': _puae_options,
    'dolphin': _dolphin_options,
    'o2em': _o2em_options,
    'mame': _mame_options,
    'mess': _mame_options,
    'mamevirtual': _mame_options,
    'same_cdi': _same_cdi_options,
    'mame078plus': _mame078plus_options,
    'vecx': _vecx_options,
    'dosbox_pure': _dosbox_pure_options,
    'bluemsx': _bluemsx_options,
    'pce': _pce_options,
    'pce_fast': _pce_options,
    'quasi88': _quasi88_options,
    'np2kai': _np2kai_options,
    'mednafen_supergrafx': _mednafen_supergrafx_options,
    'pcfx': _pcfx_options,
    'mupen64plus-next': _mupen64plus_next_options,
    'parallel_n64': _parallel_n64_options,
    'dice': _dice_options,
    'desmume': _desmume_options,
    'melonds': _melonds_options,
    'melondsds': _melondsds_options,
    'tgbdual': _tgbdual_options,
    'gambatte': _gambatte_options,
    'mgba': _mgba_options,
    'vba-m': _vba_m_options,
    'nestopia': _nestopia_options,
    'fceumm': _fceumm_options,
    'mesen': _mesen_options,
    'pokemini': _pokemini_options,
    'snes9x': _snes9x_options,
    'snes9x_next': _snes9x_next_options,
    'bsnes': _bsnes_options,
    'mesen-s': _mesen_s_options,
    'vb': _vb_options,
    'opera': _opera_options,
    'xrick': _xrick_options,
    'scummvm': _scummvm_options,
    'flycast': _flycast_options,
    'genesisplusgx': _genesisplusgx_options,
    'picodrive': _picodrive_options,
    'yabasanshiro': _yabasanshiro_options,
    'kronos': _kronos_options,
    'beetle-saturn': _beetle_saturn_options,
    'px68k': _px68k_options,
    '81': _81_options,
    'fuse': _fuse_options,
    'fbneo': _fbneo_options,
    'neocd': _neocd_options,
    'ppsspp': _ppsspp_options,
    'mednafen_psx': _mednafen_psx_options,
    'swanstation': _duckstation_options,
    'duckstation': _duckstation_options,
    'pcsx2': _pcsx2_options,
    'pcsx_rearmed': _pcsx_rearmed_options,
    'theodore': _theodore_options,
    'potator': _potator_options,
    'prboom': _prboom_options,
    'tyrquake': _tyrquake_options,
    'mrboom': _mrboom_options,
    'hatarib': _hatarib_options,
    'mednafen_wswan': _mednafen_wswan_options,
}


def generateCoreSettings(
    coreSettings: UnixSettings, system: Emulator, rom: Path, guns: Guns, wheels: DeviceInfoMapping, /,
) -> None:
    if set_options := _option_functions.get(system.config.core):
        set_options(coreSettings, system, rom, guns, wheels)

    # Custom : Allow the user to configure directly retroarchcore.cfg via batocera.conf via lines like : snes.retroarchcore.opt=val
    for user_config, value in system.config.items(starts_with='retroarchcore.'):
        coreSettings.save(user_config, f'"{value}"')

def generateHatariConf(hatariConf: Path) -> None:
    hatariConfig = CaseSensitiveConfigParser(interpolation=None)
    if hatariConf.exists():
        hatariConfig.read(hatariConf)

    # update the configuration file
    with ensure_parents_and_open(hatariConf, 'w') as configfile:
        hatariConfig.write(configfile)
