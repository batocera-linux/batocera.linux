from __future__ import annotations

import logging
import platform
import re
import shutil
from pathlib import Path
from shutil import copyfile
from typing import TYPE_CHECKING, Final

from batocera_common.configparser import CaseSensitiveConfigParser
from batocera_common.dataclasses import cached_dataclass, cached_property
from batocera_common.paths import LOGS, SAVES, SCREENSHOTS
from batocera_common.vulkan import get_version as vulkan_get_version, is_available as vulkan_is_available
from batocera_launch import Command, Emulator, HotkeysContext, guns_need_crosses

if TYPE_CHECKING:
    from batocera_launch import Controller

_logger = logging.getLogger(__name__)

_SUPERMODEL_SHARE: Final = Path('/usr/share/supermodel')

_AXIS_NAMES: Final = {
    0: 'XAXIS',
    1: 'YAXIS',
    2: 'ZAXIS',
    3: 'RXAXIS',
    4: 'RYAXIS',
    5: 'RZAXIS',
    6: 'SLIDER1',
    7: 'SLIDER2',
}

_HAT_DIRECTIONS: Final = {'1': 'UP', '2': 'RIGHT', '4': 'DOWN', '8': 'LEFT'}

# binding axis names to calibration key ids, eg. RZAXIS -> InputJoy1RZMinVal
_INI_AXIS_IDS: Final = {
    'XAXIS': 'X',
    'YAXIS': 'Y',
    'ZAXIS': 'Z',
    'RXAXIS': 'RX',
    'RYAXIS': 'RY',
    'RZAXIS': 'RZ',
    'SLIDER1': 'S1',
    'SLIDER2': 'S2',
}

_JOY_AXIS_BINDING: Final = re.compile(r'^JOY(\d+)_([A-Z0-9]+?)(?:_POS|_NEG|_INV)?$')

# pedals, in the order _get_pad_input() resolves them
_ACCELERATOR_INPUTS: Final = ['r2', 'right_trigger']
_BRAKE_INPUTS: Final = ['l2', 'left_trigger']


def _get_pad_input(
    pad: Controller | None,
    name_or_names: str | list[str],
    /,
    *,
    full_axis: bool = False,
    force_pos: bool = False,
) -> str | None:
    if pad is None:
        return None

    names = [name_or_names] if isinstance(name_or_names, str) else name_or_names

    input = None
    for name in names:
        if name in pad.inputs:
            input = pad.inputs[name]
            break

    if input is None:
        return None

    # supermodel numbers joysticks in sdl order, whichever input system is in use
    prefix = f'JOY{pad.index + 1}'

    if input.type == 'button':
        return f'{prefix}_BUTTON{int(input.id) + 1}'

    if input.type == 'axis':
        # supermodel's AXISn names are 1 based, unlike the sdl axis index
        axis_name = _AXIS_NAMES.get(int(input.id), f'AXIS{int(input.id) + 1}')

        if full_axis:
            return f'{prefix}_{axis_name}'

        if force_pos:
            return f'{prefix}_{axis_name}_POS'

        direction = '_POS' if str(input.value) in ('1', '+1') else '_NEG'
        return f'{prefix}_{axis_name}{direction}'

    if input.type == 'hat':
        hat_dir = _HAT_DIRECTIONS.get(str(input.value), 'UP')
        return f'{prefix}_POV{int(input.id) + 1}_{hat_dir}'

    return None


def _build_binding(default_keys: str, pad_bind: str | None, /) -> str:
    if pad_bind:
        # Prevent duplicate entries if pad_bind is already in default_keys
        if pad_bind in default_keys.split(','):
            return default_keys
        return f'{default_keys},{pad_bind}' if default_keys else pad_bind
    return default_keys


def _find_pad_input_name(pad: Controller, names: list[str], /) -> str | None:
    return next((name for name in names if name in pad.inputs), None)


def _set_pedal_calibration(
    target_config: CaseSensitiveConfigParser,
    pad: Controller,
    binding: str | None,
    input_name: str,
    is_reversed: bool,
    /,
    *,
    gamepad_mode: bool,
) -> None:
    """Writes a pedal's raw range; MinVal > MaxVal makes Supermodel invert the axis."""
    if binding is None or (match := _JOY_AXIS_BINDING.match(binding)) is None:
        return
    if (axis_id := _INI_AXIS_IDS.get(match.group(2))) is None:
        return

    # the sdl game controller mapping already inverts inputs recorded with a negative value
    if gamepad_mode and int(pad.inputs[input_name].value) < 0:
        is_reversed = not is_reversed

    # sdlgamepad reports triggers as 0..32767, raw sdl/evdev joystick axes as -32768..32767
    released = 0 if gamepad_mode else -32768
    rest = 32767 if is_reversed else released
    pressed = released if is_reversed else 32767

    key = f'InputJoy{match.group(1)}{axis_id}'
    target_config.set('Global', f'{key}MinVal', str(rest))
    target_config.set('Global', f'{key}OffVal', str(rest))
    target_config.set('Global', f'{key}MaxVal', str(pressed))
    _logger.info('supermodel: %s of %s calibrated %s to %s..%s', input_name, pad.real_name, key, rest, pressed)


@cached_dataclass
class Supermodel(Emulator):
    needs_sdl_game_controller_config = True

    @cached_property
    def hotkeygen_context(self) -> HotkeysContext:
        return {
            'name': 'supermodel',
            'keys': {
                'exit': 'KEY_ESC',
                'menu': ['KEY_LEFTALT', 'KEY_P'],
                'pause': ['KEY_LEFTALT', 'KEY_P'],
                'reset': ['KEY_LEFTALT', 'KEY_R'],
                'save_state': 'KEY_F5',
                'restore_state': 'KEY_F7',
                'next_state': 'KEY_F6',
            },
        }

    @cached_property
    def saves_dir(self) -> Path:
        # Historically pinned to the emulator's own name rather than the "model3" system name
        return SAVES / self.name

    @cached_property
    def screenshot_dir(self) -> Path:
        return SCREENSHOTS / self.name

    @cached_property
    def in_game_ratio(self) -> float:
        if self.config.get_bool('m3_stretch'):
            return 16 / 9
        if self.config.get_bool('m3_wideScreen'):
            return 16 / 9
        return 4 / 3

    async def configure(self) -> Command:
        # Detect if we are running on an ARM system (uses GLES)
        is_arm = platform.machine().startswith(('arm', 'aarch'))

        # Configure audio channels (defaults to Stereo / 2-channel)
        audio_channels = self.config.get_str('m3_audio_channels', '2')
        args: list[str | Path] = ['supermodel', '-fullscreen', f'-channels={audio_channels}']

        # Graphics Backend selection (OpenGL or Vulkan)
        graphics_backend = self.config.get_str('graphics_backend')
        if graphics_backend == 'Vulkan':
            if vulkan_is_available():
                vulkan_version = vulkan_get_version()
                if vulkan_version >= '1.1':
                    _logger.debug('Vulkan driver is available. Using Vulkan version: %s', vulkan_version)
                    args.append('-graphics-backend=Vulkan')
                else:
                    _logger.debug('Vulkan version %s is lower than 1.1! Falling back to OpenGL.', vulkan_version)
                    args.append('-graphics-backend=OpenGL')
            else:
                _logger.debug('*** Vulkan driver is not available on the system! Falling back to OpenGL. ***')
                args.append('-graphics-backend=OpenGL')
        elif graphics_backend:
            args.append(f'-graphics-backend={graphics_backend}')

        # 3D Engine selection (force New3D on ARM/GLES devices to prevent exit)
        if is_arm or self.config.get_str('engine3D') == 'new3d':
            args.append('-new3d')
        else:
            args.extend(['-multi-texture', '-legacy3d'])

        # SCSP Sound Engine selection, left to the ini (per-game LegacySoundDSP) unless chosen
        if (scsp := self.config.get_str('m3_scsp')) == 'legacy':
            args.append('-legacy-scsp')
        elif scsp:
            args.append('-new-scsp')

        # Widescreen
        if self.config.get_bool('m3_wideScreen'):
            args.append('-wide-screen')
            args.append('-wide-bg')
            self.config['bezel'] = 'none'

        # Quad rendering (Automatically disabled on ARM/GLES due to performance constraints)
        if not is_arm and self.config.get_bool('quadRendering'):
            args.append('-quad-rendering')

        # Supersampling
        if (ss := self.config.get_str('m3_supersampling')) and ss != '1':  # 1 represents "Off"
            args.append(f'-ss={ss}')

        # Render scale (defaults to 1 for ARM, 0 for x86_64)
        default_renderscale = '1' if is_arm else '0'
        renderscale = self.config.get_str('m3_renderscale', default_renderscale)
        if renderscale != '0':
            args.append(f'-render-scale={renderscale}')

        # Stretch to fill
        if self.config.get_bool('m3_stretch'):
            args.append('-stretch')

        # Vsync
        if not self.config.get_bool('m3_vsync', True):
            args.append('-no-vsync')
        else:
            args.append('-vsync')

        # Accurate refresh rate (true model 3 hz)
        if self.config.get_bool('m3_true_hz'):
            args.append('-true-hz')

        # Disable white flashes
        if self.config.get_bool('m3_no_white_flash'):
            args.append('-no-white-flash')

        # Crosshairs
        if crosshairs := self.config.get_str('crosshairs'):
            args.append(f'-crosshairs={crosshairs}')
        elif guns_need_crosses(self.guns):
            args.append('-crosshairs=1' if len(self.guns) == 1 else '-crosshairs=3')

        # Force feedback (the template bakes ForceFeedback = 1, so the "off" case must
        # be passed explicitly or the ini's default silently wins)
        if self.config.get_bool('forceFeedback'):
            args.append('-force-feedback')
        else:
            args.append('-no-force-feedback')

        # PowerPC frequency
        if freq := self.config.get_str('ppcFreq'):
            args.append(f'-ppc-frequency={freq}')

        # CRT colour
        if color := self.config.get_str('crt_colour'):
            args.append(f'-crtcolors={color}')

        # Upscale mode
        if upscale_mode := self.config.get_str('upscale_mode'):
            args.append(f'-upscalemode={upscale_mode}')

        # Set Resolution
        args.append(f'-res={self.resolution.width},{self.resolution.height}')
        # Logs
        args.extend([f'-log-output={LOGS / "Supermodel.log"}', self.rom])

        # Copy nvram/asset/xml files as needed
        self._copy_nvram_files()
        self._copy_asset_files()
        self._copy_xml()

        # Do the controller configs
        self._configure_pads_ini()

        return Command(
            args,
            env={
                'SUPERMODEL_CONFIG_PATH': self.config_dir,
                'SDL_JOYSTICK_HIDAPI': '0',
            },
        )

    def _copy_nvram_files(self) -> None:
        source_dir = _SUPERMODEL_SHARE / 'NVRAM'
        target_dir = self.saves_dir / 'NVRAM'

        target_dir.mkdir(parents=True, exist_ok=True)

        # create nv files which are in source and have a newer modification time than in target
        for source_file in source_dir.iterdir():
            if source_file.suffix == '.nv':
                target_file = target_dir / source_file.name
                if not target_file.exists():
                    # if the target file doesn't exist, just copy the source file
                    copyfile(source_file, target_file)
                elif source_file.stat().st_mtime > target_file.stat().st_mtime:
                    # if the target file exists and has an older modification time than the source
                    # file, create a backup and copy the new file
                    backup_file = target_file.with_suffix(f'{target_file.suffix}.bak')
                    if backup_file.exists():
                        backup_file.unlink()
                    target_file.rename(backup_file)
                    copyfile(source_file, target_file)

    def _copy_asset_files(self) -> None:
        source_dir = _SUPERMODEL_SHARE / 'Assets'
        target_dir = self.config_dir / 'Assets'
        if not source_dir.exists():
            return
        target_dir.mkdir(parents=True, exist_ok=True)

        # create asset files which are in source and have a newer modification time than in target
        for source_file in source_dir.iterdir():
            target_file = target_dir / source_file.name
            if not target_file.exists() or source_file.stat().st_mtime > target_file.stat().st_mtime:
                copyfile(source_file, target_file)

    def _copy_xml(self) -> None:
        source_path = _SUPERMODEL_SHARE / 'Games.xml'
        dest_path = self.config_dir / 'Games.xml'
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        if not dest_path.exists() or source_path.stat().st_mtime > dest_path.stat().st_mtime:
            shutil.copy2(source_path, dest_path)

    def _configure_pads_ini(self) -> None:
        template_file = _SUPERMODEL_SHARE / 'Supermodel.ini.template'
        target_file = self.config_dir / 'Supermodel.ini'

        # Ensure required target directories exist
        (self.saves_dir / 'Saves').mkdir(parents=True, exist_ok=True)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        (self.config_dir / 'Analysis').mkdir(parents=True, exist_ok=True)

        # template
        template_config = CaseSensitiveConfigParser(interpolation=None)
        template_config.read(template_file, encoding='utf_8_sig')

        # target
        target_config = CaseSensitiveConfigParser(interpolation=None)

        for section in template_config.sections():
            target_config.add_section(section)
            for key, value in template_config.items(section):
                target_config.set(section, key, value)

        if not target_config.has_section('Global'):
            target_config.add_section('Global')

        # Batocera directory path configuration
        target_config.set('Global', 'AnalysisPath', str(self.config_dir / 'Analysis'))
        target_config.set('Global', 'NVRAMPath', str(self.saves_dir / 'NVRAM'))
        target_config.set('Global', 'SavesPath', str(self.saves_dir / 'Saves'))
        target_config.set('Global', 'ScreenshotsPath', str(self.screenshot_dir))
        target_config.set('Global', 'AssetsPath', str(self.config_dir / 'Assets'))
        target_config.set('Global', 'LogPath', str(LOGS))

        # evdev for guns, raw sdl joystick for wheels (all axes, real ranges), sdlgamepad otherwise
        use_guns = self.config.use_guns and bool(self.guns)
        if use_guns:
            input_system = 'evdev'
        elif self.config.use_wheels and any(pad.device_path in self.wheels for pad in self.controllers):
            input_system = 'sdl'
        else:
            input_system = 'sdlgamepad'
        gamepad_mode = input_system == 'sdlgamepad'
        # set explicitly: the template has no InputSystem key for the loop below to update
        target_config.set('Global', 'InputSystem', input_system)

        # Network Outputs configuration (MAME-compatible outputs)
        m3_outputs = self.config.get_str('m3_outputs', 'none')
        target_config.set('Global', 'Outputs', m3_outputs)

        if m3_outputs == 'net':
            outputs_lf = 'true' if self.config.get_bool('m3_outputs_lf') else 'false'
            target_config.set('Global', 'OutputsWithLF', outputs_lf)

            tcp_port = self.config.get_str('m3_outputs_tcp', '0')
            target_config.set('Global', 'OutputsTCPPort', tcp_port)

            udp_port = self.config.get_str('m3_outputs_udp', '0')
            target_config.set('Global', 'OutputsUDPBroadcastPort', udp_port)
        else:
            target_config.set('Global', 'Outputs', 'none')

        # Locate Player 1 and Player 2 controllers
        pad1 = next((pad for pad in self.controllers if pad.player_number == 1), None)
        pad2 = next((pad for pad in self.controllers if pad.player_number == 2), None)

        # template per-game steering saturation targets JOY1 and is tuned for gamepads, not wheels
        game_section = next((section for section in target_config.sections() if section.strip() == self.rom.stem), None)
        if game_section is not None and target_config.has_option(game_section, 'InputJoy1XSaturation'):
            saturation = target_config.get(game_section, 'InputJoy1XSaturation')
            target_config.remove_option(game_section, 'InputJoy1XSaturation')
            if pad1 is not None and not (self.config.use_wheels and pad1.device_path in self.wheels):
                target_config.set(game_section, f'InputJoy{pad1.index + 1}XSaturation', saturation)

        def fallback(pad: Controller, part: str) -> str | None:
            # raw joysticks have no standard layout, so only sdlgamepad gets guessed bindings
            return f'JOY{pad.index + 1}_{part}' if gamepad_mode else None

        def set_input(key: str, binding: str | None) -> None:
            if binding:
                target_config.set('Global', key, binding)

        p1_start: str | None = None
        p1_select: str | None = None
        p1_south: str | None = None
        p1_l2: str | None = None
        p2_start: str | None = None
        p2_select: str | None = None

        # Dynamically bind Player 1
        if pad1:
            p1_start = _get_pad_input(pad1, 'start')
            p1_select = _get_pad_input(pad1, 'select')
            p1_up = _get_pad_input(pad1, 'up') or fallback(pad1, 'POV1_UP')
            p1_down = _get_pad_input(pad1, 'down') or fallback(pad1, 'POV1_DOWN')
            p1_left = _get_pad_input(pad1, 'left') or fallback(pad1, 'POV1_LEFT')
            p1_right = _get_pad_input(pad1, 'right') or fallback(pad1, 'POV1_RIGHT')

            p1_south = _get_pad_input(pad1, 'b') or fallback(pad1, 'BUTTON1')
            p1_east = _get_pad_input(pad1, 'a') or fallback(pad1, 'BUTTON2')
            p1_west = _get_pad_input(pad1, 'y') or fallback(pad1, 'BUTTON3')
            p1_north = _get_pad_input(pad1, 'x') or fallback(pad1, 'BUTTON4')

            p1_l1 = _get_pad_input(pad1, ['pageup', 'l1', 'left_shoulder']) or fallback(pad1, 'BUTTON5')
            p1_r1 = _get_pad_input(pad1, ['pagedown', 'r1', 'right_shoulder']) or fallback(pad1, 'BUTTON6')
            p1_l2 = _get_pad_input(pad1, ['l2', 'left_trigger'], force_pos=True) or fallback(pad1, 'ZAXIS_POS')
            p1_r2 = _get_pad_input(pad1, ['r2', 'right_trigger'], force_pos=True) or fallback(pad1, 'RZAXIS_POS')
            p1_l3 = _get_pad_input(pad1, 'l3') or fallback(pad1, 'BUTTON9')
            p1_r3 = _get_pad_input(pad1, 'r3') or fallback(pad1, 'BUTTON10')

            p1_lstick_x = _get_pad_input(pad1, ['joystick1left', 'joystick1right'], full_axis=True) or fallback(
                pad1, 'XAXIS'
            )
            p1_lstick_y = _get_pad_input(pad1, ['joystick1up', 'joystick1down'], full_axis=True) or fallback(
                pad1, 'YAXIS'
            )
            p1_rstick_x = _get_pad_input(pad1, ['joystick2left', 'joystick2right'], full_axis=True) or fallback(
                pad1, 'RXAXIS'
            )
            p1_rstick_y = _get_pad_input(pad1, ['joystick2up', 'joystick2down'], full_axis=True) or fallback(
                pad1, 'RYAXIS'
            )

            p1_rstick_left = _get_pad_input(pad1, 'joystick2left') or fallback(pad1, 'RXAXIS_NEG')
            p1_rstick_down = _get_pad_input(pad1, 'joystick2down') or fallback(pad1, 'RYAXIS_POS')
            p1_rstick_up = _get_pad_input(pad1, 'joystick2up') or fallback(pad1, 'RYAXIS_NEG')
            p1_rstick_right = _get_pad_input(pad1, 'joystick2right') or fallback(pad1, 'RXAXIS_POS')

            target_config.set('Global', 'InputStart1', _build_binding('KEY_1', p1_start or fallback(pad1, 'BUTTON8')))
            target_config.set('Global', 'InputCoin1', _build_binding('KEY_3', p1_select or fallback(pad1, 'BUTTON7')))

            target_config.set('Global', 'InputJoyUp', _build_binding('KEY_UP', p1_up))
            target_config.set('Global', 'InputJoyDown', _build_binding('KEY_DOWN', p1_down))
            target_config.set('Global', 'InputJoyLeft', _build_binding('KEY_LEFT', p1_left))
            target_config.set('Global', 'InputJoyRight', _build_binding('KEY_RIGHT', p1_right))

            target_config.set('Global', 'InputPunch', _build_binding('KEY_A', p1_west))
            target_config.set('Global', 'InputKick', _build_binding('KEY_S', p1_north))
            target_config.set('Global', 'InputGuard', _build_binding('KEY_D', p1_south))
            target_config.set('Global', 'InputEscape', _build_binding('KEY_F', p1_east))

            target_config.set('Global', 'InputShift', _build_binding('KEY_A', p1_south))
            target_config.set('Global', 'InputBeat', _build_binding('KEY_S', p1_west))
            target_config.set('Global', 'InputCharge', _build_binding('KEY_D', p1_north))
            target_config.set('Global', 'InputJump', _build_binding('KEY_F', p1_east))

            target_config.set('Global', 'InputShortPass', _build_binding('KEY_A', p1_south))
            target_config.set('Global', 'InputLongPass', _build_binding('KEY_S', p1_west))
            target_config.set('Global', 'InputShoot', _build_binding('KEY_D', p1_east))

            is_wheel_pad = self.config.use_wheels and pad1.device_path in self.wheels

            set_input('InputSteering', p1_lstick_x)
            target_config.set('Global', 'InputAccelerator', _build_binding('KEY_UP', p1_r2))
            target_config.set('Global', 'InputBrake', _build_binding('KEY_DOWN', p1_l2))

            # raw axes rest at one end of -32768..32767, so pedals need their range declared
            if not gamepad_mode or is_wheel_pad:
                relaxed = pad1.get_mapping_axis_relaxed_values()
                for binding, names in ((p1_r2, _ACCELERATOR_INPUTS), (p1_l2, _BRAKE_INPUTS)):
                    if (name := _find_pad_input_name(pad1, names)) and (axis := relaxed.get(name)):
                        _set_pedal_calibration(
                            target_config, pad1, binding, name, axis['reversed'], gamepad_mode=gamepad_mode
                        )

            target_config.set('Global', 'InputGearShiftUp', _build_binding('KEY_Y', p1_r1))
            target_config.set('Global', 'InputGearShiftDown', _build_binding('KEY_H', p1_l1))

            if is_wheel_pad:
                # A wheel has no second stick for the 4-speed H-pattern (gamepad default,
                # below) or a d-pad free for view-select (it's needed for gears instead), so
                # re-lay these onto what a wheel actually has: the d-pad and face buttons/l3/r3
                target_config.set('Global', 'InputGearShift1', _build_binding('KEY_Q', p1_left))
                target_config.set('Global', 'InputGearShift2', _build_binding('KEY_W', p1_down))
                target_config.set('Global', 'InputGearShift3', _build_binding('KEY_E', p1_up))
                target_config.set('Global', 'InputGearShift4', _build_binding('KEY_R', p1_right))

                target_config.set('Global', 'InputVR1', _build_binding('KEY_A', p1_south))
                target_config.set('Global', 'InputVR2', _build_binding('KEY_S', p1_east))
                target_config.set('Global', 'InputVR3', _build_binding('KEY_D', p1_north))
                target_config.set('Global', 'InputVR4', _build_binding('KEY_F', p1_west))

                target_config.set('Global', 'InputViewChange', _build_binding('KEY_A', p1_south))
                target_config.set('Global', 'InputHandBrake', _build_binding('KEY_S', p1_l3))
                target_config.set('Global', 'InputRearBrake', _build_binding('KEY_S', p1_l3))
                target_config.set('Global', 'InputMusicSelect', _build_binding('KEY_D', p1_r3))
            else:
                target_config.set('Global', 'InputGearShift1', _build_binding('KEY_Q', p1_rstick_left))
                target_config.set('Global', 'InputGearShift2', _build_binding('KEY_W', p1_rstick_down))
                target_config.set('Global', 'InputGearShift3', _build_binding('KEY_E', p1_rstick_up))
                target_config.set('Global', 'InputGearShift4', _build_binding('KEY_R', p1_rstick_right))

                target_config.set('Global', 'InputVR1', _build_binding('KEY_A', p1_up))
                target_config.set('Global', 'InputVR2', _build_binding('KEY_S', p1_down))
                target_config.set('Global', 'InputVR3', _build_binding('KEY_D', p1_left))
                target_config.set('Global', 'InputVR4', _build_binding('KEY_F', p1_right))

                target_config.set('Global', 'InputViewChange', _build_binding('KEY_A', p1_south))
                target_config.set('Global', 'InputHandBrake', _build_binding('KEY_S', p1_east))
                target_config.set('Global', 'InputRearBrake', _build_binding('KEY_S', p1_east))
                target_config.set('Global', 'InputMusicSelect', _build_binding('KEY_D', p1_north))

            if not (self.config.use_guns and self.guns):
                target_config.set('Global', 'InputAnalogJoyX', _build_binding('MOUSE_XAXIS', p1_lstick_x))
                target_config.set('Global', 'InputAnalogJoyY', _build_binding('MOUSE_YAXIS', p1_lstick_y))
                target_config.set('Global', 'InputGunX', _build_binding('MOUSE_XAXIS', p1_rstick_x))
                target_config.set('Global', 'InputGunY', _build_binding('MOUSE_YAXIS', p1_rstick_y))
                target_config.set('Global', 'InputAnalogGunX', _build_binding('MOUSE_XAXIS', p1_rstick_x))
                target_config.set('Global', 'InputAnalogGunY', _build_binding('MOUSE_YAXIS', p1_rstick_y))
                target_config.set('Global', 'InputAnalogJoyTrigger', _build_binding('KEY_A,MOUSE_LEFT_BUTTON', p1_r2))
                target_config.set('Global', 'InputTrigger', _build_binding('KEY_A,MOUSE_LEFT_BUTTON', p1_r2))
                target_config.set('Global', 'InputAnalogTriggerLeft', _build_binding('KEY_A,MOUSE_LEFT_BUTTON', p1_r2))
                target_config.set('Global', 'InputAnalogJoyEvent', _build_binding('KEY_S,MOUSE_RIGHT_BUTTON', p1_l2))
                target_config.set('Global', 'InputOffscreen', _build_binding('KEY_S,MOUSE_RIGHT_BUTTON', p1_l2))
                target_config.set(
                    'Global', 'InputAnalogTriggerRight', _build_binding('KEY_S,MOUSE_RIGHT_BUTTON', p1_l2)
                )

        # Dynamically bind Player 2
        if pad2:
            p2_start = _get_pad_input(pad2, 'start')
            p2_select = _get_pad_input(pad2, 'select')
            p2_up = _get_pad_input(pad2, 'up') or fallback(pad2, 'POV1_UP')
            p2_down = _get_pad_input(pad2, 'down') or fallback(pad2, 'POV1_DOWN')
            p2_left = _get_pad_input(pad2, 'left') or fallback(pad2, 'POV1_LEFT')
            p2_right = _get_pad_input(pad2, 'right') or fallback(pad2, 'POV1_RIGHT')

            p2_south = _get_pad_input(pad2, 'b') or fallback(pad2, 'BUTTON1')
            p2_east = _get_pad_input(pad2, 'a') or fallback(pad2, 'BUTTON2')
            p2_west = _get_pad_input(pad2, 'y') or fallback(pad2, 'BUTTON3')
            p2_north = _get_pad_input(pad2, 'x') or fallback(pad2, 'BUTTON4')

            target_config.set('Global', 'InputStart2', _build_binding('KEY_2', p2_start or fallback(pad2, 'BUTTON8')))
            target_config.set('Global', 'InputCoin2', _build_binding('KEY_4', p2_select or fallback(pad2, 'BUTTON7')))

            set_input('InputJoyUp2', p2_up)
            set_input('InputJoyDown2', p2_down)
            set_input('InputJoyLeft2', p2_left)
            set_input('InputJoyRight2', p2_right)

            set_input('InputPunch2', p2_west)
            set_input('InputKick2', p2_north)
            set_input('InputGuard2', p2_south)
            set_input('InputEscape2', p2_east)

            set_input('InputShortPass2', p2_south)
            set_input('InputLongPass2', p2_west)
            set_input('InputShoot2', p2_east)

        # Evdev for guns or sdlgamepad for controllers
        for section in target_config.sections():
            if section.strip() not in ('Global', self.rom.stem):
                continue

            # for an input system
            if section.strip() != 'Global':
                target_config.set(section, 'InputSystem', 'to be defined')

            for key, _ in target_config.items(section):
                if key == 'InputSystem':
                    target_config.set(section, key, input_system)
                elif use_guns:
                    # Player 1 gun bindings
                    if key == 'InputAnalogJoyX':
                        target_config.set(section, key, 'MOUSE1_XAXIS_INV')
                    elif key == 'InputAnalogJoyY':
                        target_config.set(section, key, 'MOUSE1_YAXIS_INV')
                    elif key in ('InputGunX', 'InputAnalogGunX'):
                        target_config.set(section, key, 'MOUSE1_XAXIS')
                    elif key in ('InputGunY', 'InputAnalogGunY'):
                        target_config.set(section, key, 'MOUSE1_YAXIS')
                    elif key in ('InputTrigger', 'InputAnalogTriggerLeft', 'InputAnalogJoyTrigger'):
                        target_config.set(section, key, 'MOUSE1_LEFT_BUTTON')
                    elif key in ('InputOffscreen', 'InputAnalogTriggerRight'):
                        target_config.set(section, key, 'MOUSE1_RIGHT_BUTTON')
                    elif key == 'InputStart1':
                        target_config.set(section, key, f'MOUSE1_BUTTONX1,{p1_start or "JOY1_BUTTON8"}')
                    elif key == 'InputCoin1':
                        target_config.set(section, key, f'MOUSE1_BUTTONX2,{p1_select or "JOY1_BUTTON7"}')
                    elif key == 'InputAnalogJoyEvent':
                        target_config.set(section, key, 'KEY_S,MOUSE1_MIDDLE_BUTTON')
                    # Player 2 gun bindings
                    elif len(self.guns) >= 2:
                        p2_gun_start = p2_start or 'JOY2_BUTTON8'
                        p2_gun_select = p2_select or 'JOY2_BUTTON7'
                        if key == 'InputAnalogJoyX2':
                            target_config.set(section, key, 'MOUSE2_XAXIS_INV')
                        elif key == 'InputAnalogJoyY2':
                            target_config.set(section, key, 'MOUSE2_YAXIS_INV')
                        elif key in ('InputGunX2', 'InputAnalogGunX2'):
                            target_config.set(section, key, 'MOUSE2_XAXIS')
                        elif key in ('InputGunY2', 'InputAnalogGunY2'):
                            target_config.set(section, key, 'MOUSE2_YAXIS')
                        elif key in ('InputTrigger2', 'InputAnalogTriggerLeft2', 'InputAnalogJoyTrigger2'):
                            target_config.set(section, key, 'MOUSE2_LEFT_BUTTON')
                        elif key in ('InputOffscreen2', 'InputAnalogTriggerRight2'):
                            target_config.set(section, key, 'MOUSE2_RIGHT_BUTTON')
                        elif key == 'InputStart2':
                            target_config.set(section, key, f'MOUSE2_BUTTONX1,{p2_gun_start}')
                        elif key == 'InputCoin2':
                            target_config.set(section, key, f'MOUSE2_BUTTONX2,{p2_gun_select}')
                        elif key == 'InputAnalogJoyEvent2':
                            target_config.set(section, key, 'MOUSE2_MIDDLE_BUTTON')

        # save the ini file
        target_file.parent.mkdir(parents=True, exist_ok=True)
        with target_file.open('w') as configfile:
            target_config.write(configfile)
