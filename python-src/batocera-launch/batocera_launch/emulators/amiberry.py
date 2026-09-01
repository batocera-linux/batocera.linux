from __future__ import annotations

import logging
import zipfile
from pathlib import Path
from typing import Final

from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.key_value_config import KeyValueConfig
from batocera_common.paths import BIOS, CONFIGS, LOGS, SAVES, SCREENSHOTS
from batocera_launch import (
    BatoceraException,
    Command,
    Controller,
    Emulator,
    HotkeysContext,
    Input,
    LibretroConfig,
)

_logger = logging.getLogger(__name__)

_AMIBERRY_BIN: Final = Path('/usr/bin/amiberry')
_AMIBERRY_DATA: Final = Path('/usr/share/amiberry/data')

# saves/bios are shared across all amiga500/amiga1200/amigacd32/amigacdtv systems,
# deliberately not per-system (self.saves_dir / self.bios_dir)
_LOG_FILE: Final = LOGS / 'amiberry.log'

# default cpu model for each system
_MODEL_CPU: Final = {
    'A500': '68000',
    'A500+': '68000',
    'A1200': '68020',
    'A4000': '68030',
    'CD32': '68020',
    'CDTV': '68000',
}

# accelerator cards presets hints : (cpu, cpu multiplier, zorro III fast ram in MB)
_ACCELERATORS: Final[dict[str, tuple[str, int, int]]] = {
    'tf330': ('68030', 14, 128),
}


# --- Retroarch-style controller config, ported from configgen's libretroControllers.py -----
# Amiberry reads a retroarch-formatted overlay.cfg for its own controller mapping, hence the
# reuse of the same key names/format used for libretro cores. This is amiberry-specific here
# (not shared with the still-unmigrated retroarch generator); amiberry always calls this with
# lightgun support enabled, so (unlike the old generic helper) that's not a parameter here.

_RETROARCH_DIRS: Final = ('up', 'down', 'left', 'right')
_RETROARCH_JOYSTICKS: Final = {
    'joystick1up': 'l_y',
    'joystick1left': 'l_x',
    'joystick2up': 'r_y',
    'joystick2left': 'r_x',
}
_TYPE_TO_NAME: Final = {'button': 'btn', 'hat': 'btn', 'axis': 'axis', 'key': 'key'}
_HATS_TO_NAME: Final = {'1': 'up', '2': 'right', '4': 'down', '8': 'left'}

_CLEARED_INPUT_PREFIXES: Final = (
    'state_slot_increase',
    'load_state',
    'save_state',
    'state_slot_decrease',
    'reset',
    'exit_emulator',
    'rewind',
    'hold_fast_forward',
    'toggle_fast_forward',
    'screenshot',
    'disk_prev',
    'disk_next',
    'disk_eject_toggle',
    'shader_prev',
    'shader_next',
    'ai_service',
    'menu_toggle',
)


def _get_config_value(input: Input, /) -> str | None:
    if input.type == 'button':
        return input.id
    if input.type == 'axis':
        return f'-{input.id}' if input.value == '-1' else f'+{input.id}'
    if input.type == 'hat':
        return f'h{input.id}{_HATS_TO_NAME[input.value]}'
    if input.type == 'key':
        return input.id
    return None


def _get_analog_mode(controller: Controller, /) -> str:
    for dirkey in _RETROARCH_DIRS:
        if dirkey in controller.inputs and controller.inputs[dirkey].type in ('button', 'hat'):
            return '1'
    return '0'


# --- ROM handling, ported verbatim from amiberryGenerator ----------------------------------


def _get_rom_type(filepath: Path, /) -> str:
    extension = filepath.suffix[1:].lower()

    if extension == 'lha':
        return 'WHDL'
    if extension == 'hdf':
        return 'HDF'
    if extension == 'uae':
        return 'UAE'
    if extension in ('iso', 'cue', 'chd'):
        return 'CD'
    if extension in ('adf', 'ipf'):
        return 'DISK'
    if extension == 'zip':
        # can be either whdl or adf
        with zipfile.ZipFile(filepath) as zip_file:
            for zip_filename in zip_file.namelist():
                if zip_filename.find('/') == -1:  # at the root
                    inner_extension = Path(zip_filename).suffix[1:]
                    if inner_extension == 'info':
                        return 'WHDL'
                    if inner_extension == 'lha':
                        _logger.warning("Amiberry doesn't support .lha inside a .zip")
                        return 'UNKNOWN'
                    if inner_extension in ('adf', 'ipf'):
                        return 'DISK'
        # no info or adf file found
        return 'UNKNOWN'

    return 'UNKNOWN'


def _floppies_from_rom(rom: Path, /) -> list[Path]:
    floppies: list[Path] = []
    index_disk = rom.name.rfind('(Disk 1')

    # from one file (x1.zip), get the list of all existing files with the same extension + last
    # char (as number) suffix, e.g. "/path/toto0.zip" -> ["/path/toto0.zip", "/path/toto1.zip", ...]
    if rom.stem[-1:].isdigit():
        fileprefix = rom.stem[:-1]

        # special case for 0 while numerotation can start at 1
        zero_file = rom.with_name(f'{fileprefix}0{rom.suffix}')
        if zero_file.is_file():
            floppies.append(zero_file)

        n = 1
        while (floppy := rom.with_name(f'{fileprefix}{n}{rom.suffix}')).is_file():
            floppies.append(floppy)
            n += 1
    # (Disk 1 of 2) format
    elif index_disk != -1:
        floppies.append(rom)
        prefix = rom.name[0 : index_disk + 6]
        postfix = rom.name[index_disk + 7 :]
        n = 2
        while (floppy := rom.with_name(f'{prefix}{n}{postfix}')).is_file():
            floppies.append(floppy)
            n += 1
    else:
        # Single ADF
        return [rom]

    return floppies


@cached_dataclass
class Amiberry(Emulator):
    needs_sdl_game_controller_config = True
    needs_sdl_controller_db = True

    @cached_property
    def sdl_controller_db_path(self) -> Path:
        return self.retroarch_inputs_dir / 'gamecontrollerdb.txt'

    @cached_property
    def bios_dir(self) -> Path:
        return BIOS / 'amiga'

    @cached_property
    def saves_dir(self) -> Path:
        return SAVES / 'amiga'

    @cached_property
    def retroarch_dir(self) -> Path:
        return self.config_dir / 'retroarch'

    @cached_property
    def retroarch_inputs_dir(self) -> Path:
        return self.retroarch_dir / 'inputs'

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'amiberry',
            'keys': {
                'exit': 'KEY_F9',
                'menu': 'KEY_F8',
                'pause': 'KEY_PAUSE',
            },
        }

    def _write_controller_config(self, retroconfig: LibretroConfig, controller: Controller, /) -> None:
        # Map an emulationstation button name to the corresponding retroarch name
        retroarch_btns = {
            'a': 'a',
            'b': 'b',
            'x': 'x',
            'y': 'y',
            'pageup': 'l',
            'pagedown': 'r',
            'l2': 'l2',
            'r2': 'r2',
            'l3': 'l3',
            'r3': 'r3',
            'start': 'start',
            'select': 'select',
        }
        # X Y L1 L2  ---> X Y R1 L1
        # A B R1 R2  ---> A B R2 L2
        if self.config.get('altlayout') == 'fightstick':
            retroarch_btns['pageup'] = 'l2'
            retroarch_btns['pagedown'] = 'l'
            retroarch_btns['l2'] = 'r2'
            retroarch_btns['r2'] = 'r'

        retroarch_gun_btns = {
            'a': 'aux_a',
            'b': 'aux_b',
            'y': 'aux_c',
            'pageup': 'offscreen_shot',
            'pagedown': 'trigger',
            'start': 'start',
            'select': 'select',
        }

        for btnkey, btnvalue in retroarch_btns.items():
            if (input := controller.inputs.get(btnkey)) is not None:
                retroconfig.set(
                    f'input_player{controller.player_number}_{btnvalue}_{_TYPE_TO_NAME[input.type]}',
                    _get_config_value(input),
                )

        for btnkey, btnvalue in retroarch_gun_btns.items():
            if (input := controller.inputs.get(btnkey)) is not None:
                retroconfig.set(
                    f'input_player{controller.player_number}_gun_{btnvalue}_{_TYPE_TO_NAME[input.type]}',
                    _get_config_value(input),
                )

        for direction in _RETROARCH_DIRS:
            if (input := controller.inputs.get(direction)) is not None:
                retroconfig.set(
                    f'input_player{controller.player_number}_{direction}_{_TYPE_TO_NAME[input.type]}',
                    _get_config_value(input),
                )
                retroconfig.set(
                    f'input_player{controller.player_number}_gun_dpad_{direction}_{_TYPE_TO_NAME[input.type]}',
                    _get_config_value(input),
                )

        for jskey, jsvalue in _RETROARCH_JOYSTICKS.items():
            if (input := controller.inputs.get(jskey)) is not None:
                if input.value == '-1':
                    retroconfig.set(f'input_player{controller.player_number}_{jsvalue}_minus_axis', f'-{input.id}')
                    retroconfig.set(f'input_player{controller.player_number}_{jsvalue}_plus_axis', f'+{input.id}')
                else:
                    retroconfig.set(f'input_player{controller.player_number}_{jsvalue}_minus_axis', f'+{input.id}')
                    retroconfig.set(f'input_player{controller.player_number}_{jsvalue}_plus_axis', f'-{input.id}')

        # note: the old generic helper skips writing mouse_index when lightgun support is
        # requested; amiberry always requests it, so mouse_index is never written here either.
        retroconfig.set(f'input_player{controller.player_number}_joypad_index', controller.index)
        retroconfig.set(f'input_player{controller.player_number}_analog_dpad_mode', _get_analog_mode(controller))

    def _write_controllers_config(self, config_path: Path, /) -> None:
        retroconfig = LibretroConfig(config_path, self.config)

        # Clean the config
        retroconfig.remove_all_starting_with('input_player')
        for name in _CLEARED_INPUT_PREFIXES:
            retroconfig.remove_all_starting_with(f'input_{name}')

        # hotkeys, forced to match with the hotkeys system
        retroconfig.set('input_enable_hotkey', 'shift')
        retroconfig.set('input_menu_toggle', 'f1')
        retroconfig.set('input_fps_toggle', 'f2')
        retroconfig.set('input_exit_emulator', 'escape')
        retroconfig.set('input_pause_toggle', 'p')
        retroconfig.set('input_save_state', 'f3')
        retroconfig.set('input_load_state', 'f4')
        retroconfig.set('input_state_slot_decrease', 'f5')
        retroconfig.set('input_state_slot_increase', 'f6')
        retroconfig.set('input_ai_service', 'f9')
        retroconfig.set('input_reset', 'f10')
        retroconfig.set('input_rewind', 'f11')

        # See if FF is toggle or hold
        ff_action = 'toggle_fast_forward' if self.config.get_bool('toggle_fast_forward') else 'hold_fast_forward'
        retroconfig.set(f'input_{ff_action}', 'f12')
        retroconfig.set('input_screenshot', 'nul')
        retroconfig.set('input_audio_mute', 'nul')
        retroconfig.set('input_grab_mouse_toggle', 'nul')

        for controller in self.controllers:
            self._write_controller_config(retroconfig, controller)

        if (
            self.controllers
            and 'hotkey' in self.controllers[0].inputs
            and self.controllers[0].inputs['hotkey'].type == 'button'
        ):
            # Write the hotkey config for controller 1
            retroconfig.set('input_enable_hotkey_btn', self.controllers[0].inputs['hotkey'].id)

        retroconfig.write()

    async def configure(self) -> Command:
        retroarch_custom = self.retroarch_dir / 'overlay.cfg'
        plugins_dir = self.config_dir / 'plugins'
        whdboot_dir = self.config_dir / 'whdboot'

        plugins_dir.mkdir(parents=True, exist_ok=True)

        amiberryconf = KeyValueConfig(self.config_dir / 'amiberry.conf', separator=' ')

        amiberryconf['default_quit_key'] = 'F9'
        amiberryconf['default_open_gui_key'] = 'F8'
        amiberryconf['saveimage_dir'] = self.saves_dir
        amiberryconf['savestate_dir'] = self.saves_dir
        amiberryconf['screenshot_dir'] = SCREENSHOTS
        amiberryconf['nvram_dir'] = self.saves_dir / 'nvram'
        amiberryconf['rom_path'] = self.bios_dir
        amiberryconf['whdboot_path'] = whdboot_dir
        amiberryconf['logfile_path'] = _LOG_FILE
        amiberryconf['controllers_path'] = self.retroarch_inputs_dir
        amiberryconf['retroarch_config'] = retroarch_custom
        amiberryconf['default_vkbd_enabled'] = self.config.get_bool('amiberry_virtual_keyboard', return_values=(1, 0))

        # NOTE: as of amiberry v8.3.0 upstream treats default_vkbd_hires as a legacy,
        # accepted-but-never-applied key (the bitmap "hi-res keyboard" concept was dropped
        # from the rewritten virtual keyboard) -- amiberry_hires_keyboard is effectively a
        # no-op now. Kept as a harmless write pending a decision on removing the .yml option.
        amiberryconf['default_vkbd_hires'] = self.config.get_bool('amiberry_hires_keyboard', return_values=(1, 0))
        amiberryconf['default_vkbd_transparency'] = self.config.get_str('amiberry_vkbd_transparency', '60')
        amiberryconf['default_vkbd_language'] = self.config.get_str('amiberry_vkbd_language', 'US')
        amiberryconf['default_vkbd_toggle'] = 'leftstick'
        amiberryconf['default_fullscreen_mode'] = '2'
        amiberryconf['default_auto_crop'] = self.config.get_bool('amiberry_auto_crop', return_values=('true', 'false'))
        # NOTE: there is no amiberry.conf "default_keep_aspect" key upstream -- gfx_keep_aspect
        # is a per-config UAE option only, applied on the command line below instead.
        amiberryconf['shader'] = self.config.get_str('amiberry_shader', 'none')

        amiberryconf['write_logfile'] = 'yes'
        amiberryconf.write()

        rom_type = _get_rom_type(self.rom)
        _logger.debug('romType: %s', rom_type)

        if rom_type == 'UNKNOWN':
            # otherwise, unknown format
            return Command([])

        args: list[str | Path] = [_AMIBERRY_BIN]

        if rom_type != 'WHDL':
            args.append('--model')
            args.append(self.config.core)
        if rom_type == 'WHDL':
            args.append('--autoload')
            args.append(self.rom)
        elif rom_type == 'HDF':
            args.append('-s')
            args.append(f'hardfile2=rw,DH0:"{self.rom}",32,1,2,512,0,,uae0')
            args.append('-s')
            args.append(f'uaehf0=hdf,rw,DH0:"{self.rom}",32,1,2,512,0,,uae0')
        elif rom_type == 'UAE':
            args.append('-f')
            args.append(self.rom)
        elif rom_type == 'CD':
            args.append('--cdimage')
            args.append(self.rom)
        elif rom_type == 'DISK':
            # floppies
            for n, img in enumerate(_floppies_from_rom(self.rom)[:4]):
                args.append(f'-{n}')
                args.append(img)
            # floppy path: use disk folder as floppy path
            args.append('-s')
            args.append(f'amiberry.floppy_path={self.rom.parent}')

        # controller
        self._write_controllers_config(retroarch_custom)

        is_player2 = False
        for pad in self.controllers:
            replacements = {f'_player{pad.player_number}_': '_'}
            # amiberry remove / included in pads names like "USB Downlo01.80 PS3/USB Corded Gamepad"
            padfilename = pad.real_name.replace('/', '')
            player_input_filename = self.retroarch_inputs_dir / f'{padfilename}.cfg'
            with retroarch_custom.open() as infile, player_input_filename.open('w') as outfile:
                for line in infile:
                    for src, target in replacements.items():
                        newline = line.replace(src, target)
                        if not newline.isspace():
                            outfile.write(newline)
            if pad.player_number == 1:  # 1 = joystick port
                args.append('-s')
                args.append('joyport1=joy0')
                args.append('-s')
                args.append(f'joyportfriendlyname1={padfilename}')
                args.append('-s')
                args.append('joyportname1=')
                if rom_type == 'CD':
                    args.append('-s')
                    args.append('joyport1mode=cd32joy')
            if pad.player_number == 2:  # 0 = mouse for the player 2
                is_player2 = True
                args.append('-s')
                args.append('joyport0=joy1')
                args.append('-s')
                args.append(f'joyportfriendlyname0="{padfilename}"')
                args.append('-s')
                args.append('joyportname0=')

        # set default mouse if no player2 gamepad is configured
        # when gamepad is configured on joyport0, autoswitch between gamepad<->mouse is enabled by default
        if not is_player2:
            args.append('-s')
            args.append('joyport0=mouse')
            args.append('-s')
            args.append('joyportfriendlyname0="System mouse"')
            args.append('-s')
            args.append('joyportname0=MOUSE0')

        # fps
        if self.config.show_fps:
            args.append('-s')
            args.append('show_leds=true')

        # disable port 2 (otherwise, the joystick goes on it)
        args.append('-s')
        args.append('joyport2=')

        # remove interlace artifacts (gfx_scandoubler was renamed to gfx_flickerfixer upstream)
        if amiberry_scandoubler := self.config.get_str('amiberry_scandoubler'):
            args.append('-s')
            args.append(f'gfx_flickerfixer={amiberry_scandoubler}')

        # auto_crop (previously auto_height)
        if amiberry_auto_crop := self.config.get_str('amiberry_auto_crop'):
            args.append('-s')
            args.append(f'gfx_auto_crop={amiberry_auto_crop}')

        # keep aspect ratio: this is a per-config UAE key (gfx_keep_aspect), there's no
        # amiberry.conf-level default for it upstream
        if amiberry_keep_aspect := self.config.get_str('amiberry_keep_aspect'):
            args.append('-s')
            args.append(f'gfx_keep_aspect={amiberry_keep_aspect}')

        # line mode
        if amiberry_linemode := self.config.get_str('amiberry_linemode'):
            args.append('-s')
            args.append(f'gfx_linemode={amiberry_linemode}')

        # video resolution
        if amiberry_resolution := self.config.get_str('amiberry_resolution'):
            args.append('-s')
            args.append(f'gfx_resolution={amiberry_resolution}')

        # accelerator hint in rom filename like [TF330] change cpu,frequency && z3 memory
        default_cpu, default_multiplier, default_z3_fastram = '', 0, 0
        for accelerator, specs in _ACCELERATORS.items():
            if accelerator in self.rom.stem.lower():
                _logger.debug(
                    '%s found in the rom name, %s at x%s with %sMB of zorro III fast ram', accelerator, *specs
                )
                default_cpu, default_multiplier, default_z3_fastram = specs
                break

        amiberry_cpu = self.config.get_str('amiberry_cpu', default_cpu)
        amiberry_z3_fastram = self.config.get_int('amiberry_z3_fastram', default_z3_fastram)

        cpu = amiberry_cpu or _MODEL_CPU.get(self.config.core, '')
        wants_z3 = amiberry_z3_fastram > 0

        # Zorro III fast ram need a 32bit cpu >= 68020
        if wants_z3 and cpu in ('', '68000', '68010'):
            raise BatoceraException(
                f'Zorro III fast ram needs a 68020 or better, {cpu or self.config.core} only addresses 24 bits: set amiberry_cpu'
            )

        # cpu override different than default cpu machine model
        if amiberry_cpu:
            args.append('-s')
            args.append(f'cpu_model={amiberry_cpu}')

        if amiberry_cpu or wants_z3:
            args.append('-s')
            args.append(f'cpu_24bit_addressing={"true" if cpu in ("68000", "68010") else "false"}')

        # cpu frenquency multiplier
        if amiberry_cpu_multiplier := self.config.get_int('amiberry_cpu_multiplier', default_multiplier):
            args.append('-s')
            args.append(f'cpu_multiplier={amiberry_cpu_multiplier}')

        # left to the model preset by default: it is what gives a 68020 or a 68030 its real
        # instruction timings. Turning it off falls back to 68000 timings scaled down
        # (adjust_cycles), which is *slower* on a big cpu, and is only worth it together with the jit.
        match self.config.get_str('amiberry_cycle_exact'):
            case 'off':
                args.append('-s')
                args.append('cpu_cycle_exact=false')
                args.append('-s')
                args.append('blitter_cycle_exact=false')
            case _:  # on
                args.append('-s')
                args.append('cpu_cycle_exact=true')
                args.append('-s')
                args.append('blitter_cycle_exact=true')

        # default fastram to 8MB
        args.append('-s')
        args.append('fastmem_size=8')

        # extra fastram on zorro III bus
        if wants_z3:
            args.append('-s')
            args.append(f'z3mem_size={amiberry_z3_fastram}')

        # disable cdrom seek && transfert delays
        if self.config.get_bool('amiberry_cd_turbo'):
            args.append('-s')
            args.append('cd_speed=0')

        # Scaling method
        match self.config.get_str('amiberry_scalingmethod'):
            case 'pixelated':
                args.append('-s')
                args.append('amiberry.scaling_method=0')
            case 'smooth':
                args.append('-s')
                args.append('amiberry.scaling_method=1')
            case 'integer':
                args.append('-s')
                args.append('amiberry.scaling_method=2')
            case _:  # none
                args.append('-s')
                args.append('amiberry.scaling_method=-1')

        # display vertical centering
        args.append('-s')
        args.append('gfx_center_vertical=smart')

        # force ntsc
        # detect ntsc from rom filename hint
        amiberry_default_ntsc = 'ntsc' in self.rom.stem.lower()

        if self.config.get_bool('amiberry_ntsc', amiberry_default_ntsc):
            args.append('-s')
            args.append('ntsc=true')
            args.append('-s')
            args.append('chipset_refreshrate=60.000000')

        # memory
        args.append('-F 8')

        # fix sound buffer and frequency
        args.append('-s')
        args.append('sound_max_buff=4096')
        args.append('-s')
        args.append('sound_frequency=48000')

        # Disable GUI at launch
        if not args or args[-1] != '-G':
            args.append('-G')

        return Command(
            args,
            env={
                'AMIBERRY_DATA_DIR': _AMIBERRY_DATA,
                'AMIBERRY_HOME_DIR': self.config_dir,
                'AMIBERRY_CONFIG_DIR': self.config_dir,
                'AMIBERRY_PLUGINS_DIR': plugins_dir,
                'XDG_DATA_HOME': CONFIGS,
                'XDG_CONFIG_HOME': CONFIGS,
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )
