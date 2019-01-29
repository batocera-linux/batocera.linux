import sys
import os
import recalboxFiles
from settings.unixSettings import UnixSettings
import xml.etree.ElementTree as ET
import shlex
from utils.logger import eslog

class Emulator():

    def __init__(self, name, config):
        self.name = name
        self.config = config

    def configure(self, emulator='default', core='default', ratio='auto', netplay=None):
        recalSettings = UnixSettings(recalboxFiles.recalboxConf)
        globalSettings = recalSettings.loadAll('global')
        self.config['specials'] = recalSettings.load('system.emulators.specialkeys', 'default')
        self.updateConfiguration(globalSettings)
        self.updateConfiguration(recalSettings.loadAll(self.name))
        self.updateForcedConfig(emulator, core, ratio)

    def isOptSet(self, key):
        return key in self.config

    def getOptBoolean(self, key):
        if self.config[key] == '1'    and type(self.config[key]) == type('1'):
            return True
        if self.config[key] == 'true' and type(self.config[key]) == type('true'):
            return True
        if self.config[key] == True   and type(self.config[key]) == type(True):
            return True
        return False

    def updateConfiguration(self, settings):
        systemSettings = self.config

        # ignore all values "default", "auto", "" to take the system value instead
        # ideally, such value must not be in the configuration file
        # but historically some user have them
        toremove = [k for k in settings if settings[k] == "" or settings[k] == "default" or settings[k] == "auto"]
        for k in toremove: del settings[k]

        systemSettings.update(settings)
        # ShaderSets
        if 'shaderset' in settings:
            self.updateShaders(settings['shaderset'])
        # Draw FPS
        self.updateDrawFPS()

    def updateShaders(self, shaderSet):
        if shaderSet != None and shaderSet != 'none':
            shaderfile = recalboxFiles.shaderPresetRoot + '/' + shaderSet + '.cfg'
            systemShader = UnixSettings(shaderfile).load(self.name)
            if systemShader != None:
                self.config['shaders'] = systemShader

    def updateForcedConfig(self, emulator, core, ratio):
        if emulator != None and emulator != 'auto':
            self.config['emulator'] = emulator
        if core != None and core != 'auto':
            self.config['core'] = core
        if ratio != None and ratio != 'auto':
            self.config['ratio'] = ratio

    # fps value is from es
    def updateDrawFPS(self):
        try:
            esConfig = ET.parse(recalboxFiles.esSettings)
            value = esConfig.find("./bool[@name='DrawFramerate']").attrib["value"]
        except:
            value = 'false'
        if value not in ['false', 'true']:
            value = 'false'
        self.config['showFPS'] = value
