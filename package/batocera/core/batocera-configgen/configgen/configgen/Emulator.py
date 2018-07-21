import sys
import os
import recalboxFiles
from settings.unixSettings import UnixSettings
import xml.etree.ElementTree as ET
import shlex

class Emulator():

    def __init__(self, name, emulator, core='', videomode='CEA 4 HDMI', shaders='', ratio='auto', smooth='1', rewind='0', configfile=None, showFPS=None):
        self.name = name
        self.config = dict()
        self.config['videomode']  = videomode
        self.config['core']       = core
        self.config['emulator']   = emulator
        self.config['shaders']    = shaders
        self.config['ratio']      = ratio
        self.config['smooth']     = smooth
        self.config['rewind']     = rewind
        self.config['configfile'] = configfile
        self.config['netplay']    = None
        self.config['showFPS']    = showFPS
        self.config['args']       = None
        
    def configure(self, emulator='default', core='default', ratio='auto', netplay=None):
        recalSettings = UnixSettings(recalboxFiles.recalboxConf)
        globalSettings = recalSettings.loadAll('global')
        self.config['specials'] = recalSettings.load('system.emulators.specialkeys', 'default')
        self.config['netplaymode'] = netplay
        self.updateConfiguration(globalSettings)
        self.updateConfiguration(recalSettings.loadAll(self.name))
        self.updateForcedConfig(emulator, core, ratio)

    def updateConfiguration(self, settings):
        systemSettings = self.config
        # Special case of auto ratio
        if 'ratio' in settings and settings['ratio'] == 'auto':
            del settings['ratio']
        if 'emulator' in settings and settings['emulator'] == 'default':
            del settings['emulator']
        if 'core' in settings and settings['core'] == 'default':
            del settings['core']
        systemSettings.update(settings)
        # ShaderSets
        if ('shaderset' in settings and settings['shaderset'] != ''):
            self.updateShaders(settings['shaderset'])
        # Draw FPS
        if self.config['showFPS'] is None or self.config['showFPS'] not in ['false', 'true']:
            self.updateDrawFPS()
        # Optionnal emulator args ONLY if security is disabled
        recalSettings = UnixSettings(recalboxFiles.recalboxConf)
        security = recalSettings.load("system.security.enabled")
        if (security != "1" and'args' in settings and settings['args'] != ''):
            self.config['args'] = shlex.split(settings['args'])
        else:
            self.config['args'] = None

    def updateShaders(self, shaderSet):
        if shaderSet != None and shaderSet != 'none':
            shaderfile = recalboxFiles.shaderPresetRoot + '/' + shaderSet + '.cfg'
            systemShader = UnixSettings(shaderfile).load(self.name)
            if systemShader != None:
                self.config['shaders'] = systemShader

    def updateForcedConfig(self, emulator, core, ratio):
        if emulator != None and emulator != 'default':
            self.config['emulator'] = emulator
        if core != None and core != 'default':
            self.config['core'] = core
        if ratio != None and ratio != 'auto':
            self.config['ratio'] = ratio

    def updateDrawFPS(self):
        try:
            esConfig = ET.parse(recalboxFiles.esSettings)
            value = esConfig.find("./bool[@name='DrawFramerate']").attrib["value"]
        except:
            value = 'false'
        if value not in ['false', 'true']:
            value = 'false'
        self.config['showFPS'] = value
