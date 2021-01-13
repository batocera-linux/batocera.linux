#!/usr/bin/env python

import glob
import os
import re
import shutil

import Command
from generators.Generator import Generator
import controllersConfig
import utils.videoMode as videoMode

_ROMS_DIR = '/userdata/roms/openmw'


def _rom_dir(game):
    return _ROMS_DIR + '/' + game


def _config_dir(game):
    return '/userdata/system/configs/openmw/' + game


def _save_dir(game):
    return '/userdata/saves/openmw/' + game

def _getDefaultSettings(system):
    resolution = videoMode.getCurrentResolution()
    w, h = resolution['width'], resolution['height']
    if system.getOptBoolean('resolutionIsReversed'):
        w, h = h, w

    gui_scaling_factor = 1.0
    if h < 480:
        # Reduce GUI scale on small screens to make the menus fit.
        gui_scaling_factor = h / 480.0
    return """# Overrides for default settings
# See /etc/openmw/settings-default.cfg for the full list of settings.

[Camera]
viewing distance = 2048.0

# Key controlling sneak toggles setting instead of being held down.
toggle sneak = true

# Camera sensitivity when not in GUI mode. (>0.0, e.g. 0.1 to 5.0).
camera sensitivity = 0.4

[Video]
resolution x = {}
resolution y = {}
fullscreen = true

[Physics]
async num threads = 1

[GUI]
scaling factor = {}
""".format(w, h, gui_scaling_factor)


def _maybeInitConfig(system, game):
    config_dir = _config_dir(game) + '/openmw'
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    openmw_cfg_path = config_dir + '/openmw.cfg'
    if not os.path.exists(openmw_cfg_path):
        template_path = os.path.dirname(os.path.abspath(
            __file__)) + '/' + game + '-openmw.cfg'
        if os.path.exists(template_path):
            shutil.copy(template_path, openmw_cfg_path)

    # User-adjustable settings
    settings_path = config_dir + '/settings.cfg'
    if not os.path.exists(settings_path):
        with open(settings_path, 'w') as f:
            f.write(_getDefaultSettings(system))

class OpenMWGenerator(Generator):

    def generate(self, system, rom, playersControllers, gameResolution):
        game = os.path.splitext(os.path.basename(rom))[0]
        commandArray = ['/usr/bin/openmw']
        if system.getOptBoolean('showFPS'):
            commandArray.append('--fps')

        _maybeInitConfig(system, game)

        return Command.Command(
            array=commandArray,
            env={
                'OPENMW_GLES_VERSION': '2',
                'XDG_CONFIG_HOME': _config_dir(game),
                'XDG_DATA_HOME': _save_dir(game),
                'LD_LIBRARY_PATH': '/usr/lib/openmw/gl4es',
                'SDL_GAMECONTROLLERCONFIG': controllersConfig.generateSdlGameControllerConfig(playersControllers)
            })
