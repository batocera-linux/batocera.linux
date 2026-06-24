from __future__ import annotations

import configparser
import logging
import shutil
from typing import TYPE_CHECKING, Any, cast

import ruamel.yaml
import ruamel.yaml.util

from ... import Command
from ...batoceraPaths import CACHE, CONFIGS, SAVES, mkdir_if_not_exists
from ...controller import generate_sdl_game_controller_config
from ..Generator import Generator
from ...utils import vulkan

if TYPE_CHECKING:
    from ...types import HotkeysContext

vitaConfig = CONFIGS / 'vita3k'
vitaSaves = SAVES / 'psvita'
vitaConfigFile = vitaConfig / 'config.yml'
vitaGuiConfigs = vitaConfig / 'gui-configs'
vitaIniFile = vitaGuiConfigs / 'CurrentSettings.ini'

_logger = logging.getLogger(__name__)


# Helper function to check if desktop OpenGL 4.4+ is supported
def has_opengl_4_4_support() -> bool:
    import platform
    machine = platform.machine().lower()
        
    # ARM systems only natively support OpenGL ES, not desktop OpenGL 4.4
    if "arm" in machine or "aarch64" in machine:
        _logger.debug("ARM system detected. Desktop OpenGL 4.4 is not supported (only OpenGL ES is available).")
        return False

    try:
        import subprocess
        import re
        # Query OpenGL version using glxinfo
        res = subprocess.run(["glxinfo", "-B"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if "OpenGL core profile version string" in line or "OpenGL version string" in line:
                    match = re.search(r"OpenGL (?:core profile )?version string:\s*([0-9]+)\.([0-9]+)", line, re.IGNORECASE)
                    if match:
                        major = int(match.group(1))
                        minor = int(match.group(2))
                        return major > 4 or (major == 4 and minor >= 4)
    except Exception as e:
        _logger.debug("OpenGL 4.4 check failed or glxinfo not available: %s", e)
    return False


class Vita3kGenerator(Generator):

    def getHotkeysContext(self) -> HotkeysContext:
        return {
            "name": "vita3k",
            "keys": { "exit": ["KEY_LEFTCTRL", "KEY_F12"] }
        }

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        # Create save folder
        mkdir_if_not_exists(vitaSaves)

        # Move saves if necessary
        if (vitaConfig / 'ux0').is_dir():
            # Move all folders from vitaConfig to vitaSaves except "data", "lang", and "shaders-builtin"
            for item in vitaConfig.iterdir():
                if item.name not in ['data', 'lang', 'shaders-builtin'] and item.is_dir():
                    shutil.move(item, vitaSaves)

        # Create the config folders if they don't exist
        mkdir_if_not_exists(vitaConfig)
        mkdir_if_not_exists(vitaGuiConfigs)

        # Handle CurrentSettings.ini
        iniConfig = configparser.ConfigParser()
        iniConfig.optionxform = str  # Preserve the exact casing of keys

        if vitaIniFile.is_file():
            iniConfig.read(vitaIniFile)

        if not iniConfig.has_section('MainWindow'):
            iniConfig.add_section('MainWindow')

        iniConfig.set('MainWindow', 'warnAdminPrivileges', 'false')

        with vitaIniFile.open('w') as configfile:
            # space_around_delimiters=False ensures it writes as key=value without spaces
            iniConfig.write(configfile, space_around_delimiters=False)

        vita3kymlconfig: dict[str, Any] | None = None
        indent: int | None = None
        block_seq_indent: int | None = None

        if vitaConfigFile.is_file():
            with vitaConfigFile.open('r') as stream:
                vita3kymlconfig, indent, block_seq_indent = cast('tuple[dict[str, Any] | None, int | None, int | None]', ruamel.yaml.util.load_yaml_guess_indent(stream))

        if vita3kymlconfig is None:
            vita3kymlconfig = {}

        if indent is None:
            indent = 2

        if block_seq_indent is None:
            block_seq_indent = 0

        # Ensure the correct path is set
        vita3kymlconfig["pref-path"] = f"{vitaSaves!s}"

        # Set some defauls
        vita3kymlconfig["initial-setup"] = False
        vita3kymlconfig["boot-apps-full-screen"] = True
        vita3kymlconfig["validation-layer"] = False
        vita3kymlconfig["discord-rich-presence"] = False
        vita3kymlconfig["show-welcome"] = False
        vita3kymlconfig["check-for-updates-mode"] = 0
        vita3kymlconfig["log-level"] = 6 # None
        
        # Set the renderer
        gfx_backend = system.config.get("vita3k_gfxbackend")
        _logger.debug("User selected graphics backend: %s", gfx_backend)

        # Determine whether we should attempt to configure Vulkan
        use_vulkan = False
        if gfx_backend == "Vulkan":
            use_vulkan = True
        else:
            _logger.debug("OpenGL backend selected/default. Verifying if OpenGL 4.4 is supported...")
            if has_opengl_4_4_support():
                _logger.debug("OpenGL 4.4 is supported on this system. Sticking with OpenGL.")
                vita3kymlconfig["backend-renderer"] = "OpenGL"
            else:
                _logger.debug("OpenGL 4.4 is NOT supported. Attempting to fall back to Vulkan...")
                use_vulkan = True

        # Run Vulkan checks if Vulkan was selected or if OpenGL 4.4 checks failed
        if use_vulkan:
            if vulkan.is_available():
                _logger.debug("Vulkan driver is available on the system.")
                vita3kymlconfig["backend-renderer"] = "Vulkan"

                if vulkan.has_discrete_gpu():
                    _logger.debug("A discrete GPU is available on the system. We will use that for performance")
                    discrete_index = vulkan.get_discrete_gpu_index()
                    if discrete_index:
                        _logger.debug("Using Discrete GPU Index: %s for Vita3K", discrete_index)
                        vita3kymlconfig["gpu-idx"] = discrete_index
                    else:
                        _logger.debug("Couldn't get discrete GPU index")
                else:
                    _logger.debug("Discrete GPU is not available on the system. Using default.")
                    vita3kymlconfig["gpu-idx"] = 0
            else:
                _logger.debug("Vulkan was requested or triggered as fallback, but the Vulkan driver is not available. Falling back to OpenGL.")
                vita3kymlconfig["backend-renderer"] = "OpenGL"

        # Set the resolution multiplier
        res_val = system.config.get("vita3k_resolution", "1")
        res_mult = float(res_val)
        vita3kymlconfig["resolution-multiplier"] = int(res_mult) if res_mult.is_integer() else res_mult

        # Set VSync
        vita3kymlconfig["v-sync"] = system.config.get_bool("vita3k_vsync", True)
        # Set the anisotropic filtering
        vita3kymlconfig["anisotropic-filtering"] = system.config.get_int("vita3k_anisotropic", 1)
        # Set the filtering option
        vita3kymlconfig["screen-filter"] = system.config.get("vita3k_filter", "Bilinear")
        # Surface Sync
        vita3kymlconfig["disable-surface-sync"] = system.config.get_bool("vita3k_surface", True)
        # Async Pipeline
        vita3kymlconfig["async-pipeline-compilation"] = system.config.get_bool("vita3k_sync", True)      
        # Fullscreen HD Pixel Perfect
        vita3kymlconfig["fullscreen_hd_res_pixel_perfect"] = system.config.get_bool("vita3k_hd_pixel", False)
        # Rendering Accuracy
        vita3kymlconfig["high-accuracy"] = system.config.get_bool("vita3k_accuracy", False)
        # Texture Cache
        vita3kymlconfig["texture-cache"] = system.config.get_bool("vita3k_texture", True)
        # Shader Cache
        vita3kymlconfig["shader-cache"] = system.config.get_bool("vita3k_shader", True)
        # Memory Mapping
        vita3kymlconfig["memory-mapping"] = system.config.get("vita3k_mapping", "double-buffer")
         
        # System Language
        vita3kymlconfig["sys-lang"] = system.config.get_int("vita3k_system_language", 1)

        # Vita3k is fussy over its yml file
        # We try to match it as close as possible, but the 'vectors' cause yml formatting issues
        yaml = ruamel.yaml.YAML()
        yaml.explicit_start = True
        yaml.explicit_end = True
        yaml.indent(mapping=indent, sequence=indent, offset=block_seq_indent)

        with vitaConfigFile.open('w') as fp:
            yaml.dump(vita3kymlconfig, fp)

        # Simplify the rom name (strip the directory & extension)
        begin, end = rom.stem.find('['), rom.stem.rfind(']')
        smplromname = rom.stem[begin+1: end]
        # because of the yml formatting, we don't allow Vita3k to modify it
        # using the -w & -f options prevents Vita3k from re-writing & prompting the user in GUI
        # we want to avoid that so roms load straight away
        if (vitaSaves / 'ux0' / 'app' / smplromname).is_dir():
            commandArray = ["/usr/bin/vita3k/Vita3K", "-F", "-w", "-f", "-c", vitaConfigFile, "-r", smplromname]
        else:
            # Game not installed yet, let's open the menu
            commandArray = ["/usr/bin/vita3k/Vita3K", "-F", "-w", "-f", "-c", vitaConfigFile, rom]

        # use x11 for now to avoid crashes on certain games
        return Command.Command(
            array=commandArray,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_game_controller_config(playersControllers),
                "SDL_JOYSTICK_HIDAPI": "0",
                "XDG_CONFIG_HOME": CONFIGS,
                "XDG_DATA_HOME": SAVES,
                "XDG_CACHE_HOME": CACHE,
                "QT_QPA_PLATFORM": "xcb",
                "SDL_VIDEODRIVER": "x11"
            }
        )

    # Show mouse for touchscreen actions
    def getMouseMode(self, config, rom):
        return config.get("vita3k_show_pointer") != '0'

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
