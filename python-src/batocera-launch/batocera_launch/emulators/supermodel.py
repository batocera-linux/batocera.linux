from __future__ import annotations

import logging
import platform
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
}

_HAT_DIRECTIONS: Final = {'1': 'UP', '2': 'RIGHT', '4': 'DOWN', '8': 'LEFT'}


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

    prefix = f'JOY{pad.player_number}'

    if input.type == 'button':
        return f'{prefix}_BUTTON{int(input.id) + 1}'

    if input.type == 'axis':
        axis_name = _AXIS_NAMES.get(int(input.id), f'AXIS{input.id}')

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

        # SCSP Sound Engine selection
        if self.config.get_str('m3_scsp') == 'legacy':
            args.append('-legacy-scsp')
        else:
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

        # Force feedback
        if self.config.get_bool('forceFeedback'):
            args.append('-force-feedback')

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
            p1_up = _get_pad_input(pad1, 'up') or 'JOY1_POV1_UP'
            p1_down = _get_pad_input(pad1, 'down') or 'JOY1_POV1_DOWN'
            p1_left = _get_pad_input(pad1, 'left') or 'JOY1_POV1_LEFT'
            p1_right = _get_pad_input(pad1, 'right') or 'JOY1_POV1_RIGHT'

            p1_south = _get_pad_input(pad1, 'b') or 'JOY1_BUTTON1'
            p1_east = _get_pad_input(pad1, 'a') or 'JOY1_BUTTON2'
            p1_west = _get_pad_input(pad1, 'y') or 'JOY1_BUTTON3'
            p1_north = _get_pad_input(pad1, 'x') or 'JOY1_BUTTON4'

            p1_l1 = _get_pad_input(pad1, ['pageup', 'l1', 'left_shoulder']) or 'JOY1_BUTTON5'
            p1_r1 = _get_pad_input(pad1, ['pagedown', 'r1', 'right_shoulder']) or 'JOY1_BUTTON6'
            p1_l2 = _get_pad_input(pad1, ['l2', 'left_trigger'], force_pos=True) or 'JOY1_ZAXIS_POS'
            p1_r2 = _get_pad_input(pad1, ['r2', 'right_trigger'], force_pos=True) or 'JOY1_RZAXIS_POS'

            p1_lstick_x = _get_pad_input(pad1, ['joystick1left', 'joystick1right'], full_axis=True) or 'JOY1_XAXIS'
            p1_lstick_y = _get_pad_input(pad1, ['joystick1up', 'joystick1down'], full_axis=True) or 'JOY1_YAXIS'
            p1_rstick_x = _get_pad_input(pad1, ['joystick2left', 'joystick2right'], full_axis=True) or 'JOY1_RXAXIS'
            p1_rstick_y = _get_pad_input(pad1, ['joystick2up', 'joystick2down'], full_axis=True) or 'JOY1_RYAXIS'

            p1_rstick_left = _get_pad_input(pad1, 'joystick2left') or 'JOY1_RXAXIS_NEG'
            p1_rstick_down = _get_pad_input(pad1, 'joystick2down') or 'JOY1_RYAXIS_POS'
            p1_rstick_up = _get_pad_input(pad1, 'joystick2up') or 'JOY1_RYAXIS_NEG'
            p1_rstick_right = _get_pad_input(pad1, 'joystick2right') or 'JOY1_RXAXIS_POS'

            target_config.set('Global', 'InputStart1', _build_binding('KEY_1', p1_start or 'JOY1_BUTTON8'))
            target_config.set('Global', 'InputCoin1', _build_binding('KEY_3', p1_select or 'JOY1_BUTTON7'))

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

            target_config.set('Global', 'InputSteering', p1_lstick_x)
            target_config.set('Global', 'InputAccelerator', _build_binding('KEY_UP,JOY1_RZAXIS_POS', p1_r2))
            target_config.set('Global', 'InputBrake', _build_binding('KEY_DOWN,JOY1_ZAXIS_POS', p1_l2))

            target_config.set('Global', 'InputGearShiftUp', _build_binding('KEY_Y', p1_r1))
            target_config.set('Global', 'InputGearShiftDown', _build_binding('KEY_H', p1_l1))

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
            p2_up = _get_pad_input(pad2, 'up') or 'JOY2_POV1_UP'
            p2_down = _get_pad_input(pad2, 'down') or 'JOY2_POV1_DOWN'
            p2_left = _get_pad_input(pad2, 'left') or 'JOY2_POV1_LEFT'
            p2_right = _get_pad_input(pad2, 'right') or 'JOY2_POV1_RIGHT'

            p2_south = _get_pad_input(pad2, 'b') or 'JOY2_BUTTON1'
            p2_east = _get_pad_input(pad2, 'a') or 'JOY2_BUTTON2'
            p2_west = _get_pad_input(pad2, 'y') or 'JOY2_BUTTON3'
            p2_north = _get_pad_input(pad2, 'x') or 'JOY2_BUTTON4'

            target_config.set('Global', 'InputStart2', _build_binding('KEY_2', p2_start or 'JOY2_BUTTON8'))
            target_config.set('Global', 'InputCoin2', _build_binding('KEY_4', p2_select or 'JOY2_BUTTON7'))

            target_config.set('Global', 'InputJoyUp2', p2_up)
            target_config.set('Global', 'InputJoyDown2', p2_down)
            target_config.set('Global', 'InputJoyLeft2', p2_left)
            target_config.set('Global', 'InputJoyRight2', p2_right)

            target_config.set('Global', 'InputPunch2', p2_west)
            target_config.set('Global', 'InputKick2', p2_north)
            target_config.set('Global', 'InputGuard2', p2_south)
            target_config.set('Global', 'InputEscape2', p2_east)

            target_config.set('Global', 'InputShortPass2', p2_south)
            target_config.set('Global', 'InputLongPass2', p2_west)
            target_config.set('Global', 'InputShoot2', p2_east)

        # Evdev for guns or sdlgamepad for controllers
        use_guns = self.config.use_guns and bool(self.guns)
        for section in target_config.sections():
            if section.strip() not in ('Global', self.rom.stem):
                continue

            # for an input system
            if section.strip() != 'Global':
                target_config.set(section, 'InputSystem', 'to be defined')

            for key, _ in target_config.items(section):
                if key == 'InputSystem':
                    target_config.set(section, key, 'evdev' if use_guns else 'sdlgamepad')
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
