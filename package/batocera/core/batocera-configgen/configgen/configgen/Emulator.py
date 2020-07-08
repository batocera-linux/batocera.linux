import sys
import os
import batoceraFiles
from settings.unixSettings import UnixSettings
import xml.etree.ElementTree as ET
import shlex
from utils.logger import eslog
import yaml
import collections

class Emulator():

    def __init__(self, name, rom):
        self.name = name

        # read the configuration from the system name
        self.config = Emulator.get_system_config(self.name, "/usr/share/batocera/configgen/configgen-defaults.yml", "/usr/share/batocera/configgen/configgen-defaults-arch.yml")
        if "emulator" not in self.config or self.config["emulator"] == "":
            eslog.log("no emulator defined. exiting.")
            raise Exception("No emulator found")

        # load configuration from batocera.conf
        recalSettings = UnixSettings(batoceraFiles.batoceraConf)
        globalSettings = recalSettings.loadAll('global')
        systemSettings = recalSettings.loadAll(self.name)
        gameSettings = recalSettings.loadAll(self.name + "[\"" + os.path.basename(rom) + "\"]")

        # update config
        Emulator.updateConfiguration(self.config, globalSettings)
        Emulator.updateConfiguration(self.config, systemSettings)
        Emulator.updateConfiguration(self.config, gameSettings)
        self.updateFromESSettings()
        eslog.log("uimode: {}".format(self.config['uimode']))

        # update renderconfig
        self.renderconfig = {}
        if "shaderset" in self.config and self.config["shaderset"] != "none":
            self.renderconfig = Emulator.get_generic_config(self.name, "/usr/share/batocera/shaders/configs/" + self.config["shaderset"] + "/rendering-defaults.yml", "/usr/share/batocera/shaders/configs/" + self.config["shaderset"] + "/rendering-defaults-arch.yml")
        if "shaderset" not in self.config: # auto
            self.renderconfig = Emulator.get_generic_config(self.name, "/usr/share/batocera/shaders/configs/rendering-defaults.yml", "/usr/share/batocera/shaders/configs/rendering-defaults-arch.yml")

        # for compatibility with earlier Batocera versions, let's keep -renderer
        # but it should be reviewed when we refactor configgen (to Python3?)
        # so that we can fetch them from system.shader without -renderer
        systemSettings = recalSettings.loadAll(self.name + "-renderer")
        gameSettings = recalSettings.loadAll(self.name + "[\"" + os.path.basename(rom) + "\"]" + "-renderer")

        # es only allow to update systemSettings and gameSettings in fact for the moment
        Emulator.updateConfiguration(self.renderconfig, systemSettings)
        Emulator.updateConfiguration(self.renderconfig, gameSettings)

    # to be updated for python3: https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
    @staticmethod
    def dict_merge(dct, merge_dct):
        """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
        updating only top-level keys, dict_merge recurses down into dicts nested
        to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
        ``dct``.
        :param dct: dict onto which the merge is executed
        :param merge_dct: dct merged into dct
        :return: None
        """
        for k, v in merge_dct.iteritems():
            if (k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], collections.Mapping)):
                Emulator.dict_merge(dct[k], merge_dct[k])
            else:
                dct[k] = merge_dct[k]

    @staticmethod
    def get_generic_config(system, defaultyml, defaultarchyml):
        systems_default = yaml.load(file(defaultyml, "r"), Loader=yaml.FullLoader)

        systems_default_arch = {}
        if os.path.exists(defaultarchyml):
            systems_default_arch = yaml.load(file(defaultarchyml, "r"), Loader=yaml.FullLoader)
        dict_all = {}

        if "default" in systems_default:
            dict_all = systems_default["default"]

        if "default" in systems_default_arch:
            Emulator.dict_merge(dict_all, systems_default_arch["default"])

        if system in systems_default:
            Emulator.dict_merge(dict_all, systems_default[system])

        if system in systems_default_arch:
            Emulator.dict_merge(dict_all, systems_default_arch[system])

        return dict_all

    @staticmethod
    def get_system_config(system, defaultyml, defaultarchyml):
        dict_all = Emulator.get_generic_config(system, defaultyml, defaultarchyml)

        # options are in the yaml, not in the system structure
        # it is flat in the batocera.conf which is easier for the end user, but i prefer not flat in the yml files
        dict_result = {"emulator": dict_all["emulator"], "core": dict_all["core"]}
        if "options" in dict_all:
            Emulator.dict_merge(dict_result, dict_all["options"])
        return dict_result

    def isOptSet(self, key):
        if key in self.config:
            return True
        else:
            return False

    def getOptBoolean(self, key):
        if unicode(self.config[key]) == u'1':
            return True
        if unicode(self.config[key]) == u'true':
            return True
        if self.config[key] == True:
            return True
        return False

    @staticmethod
    def updateConfiguration(config, settings):
        # ignore all values "default", "auto", "" to take the system value instead
        # ideally, such value must not be in the configuration file
        # but historically some user have them
        toremove = [k for k in settings if settings[k] == "" or settings[k] == "default" or settings[k] == "auto"]
        for k in toremove: del settings[k]

        config.update(settings)

    # fps value is from es
    def updateFromESSettings(self):
        try:
            esConfig = ET.parse(batoceraFiles.esSettings)

            # showFPS
            try:
                drawframerate_value = esConfig.find("./bool[@name='DrawFramerate']").attrib["value"]
            except:
                drawframerate_value = 'false'
            if drawframerate_value not in ['false', 'true']:
                drawframerate_value = 'false'
            self.config['showFPS'] = drawframerate_value

            # uimode
            try:
                uimode_value = esConfig.find("./string[@name='UIMode']").attrib["value"]
            except:
                uimode_value = 'Full'
            if uimode_value not in ['Full', 'Kiosk', 'Kid']:
                uimode_value = 'Full'
            self.config['uimode'] = uimode_value

        except:
            self.config['showFPS'] = False
            self.config['uimode'] = "Full"

