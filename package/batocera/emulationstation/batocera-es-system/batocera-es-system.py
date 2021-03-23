#
# - Generates the es_systems.cfg file
# - Generates roms folder and emulators folders
# - Generate the _info.txt file with the emulator information
# - Information from the emulators are being extracted from the file es_system.yml
#
import yaml
import re
import argparse
import os
import shutil
from collections import OrderedDict
from operator import itemgetter

def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

class EsSystemConf:

    default_parentpath = "/userdata/roms"
    default_command    = "python /usr/lib/python3.9/site-packages/configgen/emulatorlauncher.py %CONTROLLERSCONFIG% -system %SYSTEM% -rom %ROM%"

    # Generate the es_systems.cfg file by searching the information in the es_system.yml file
    @staticmethod
    def generate(rulesYaml, featuresYaml, configFile, esSystemFile, esFeaturesFile, systemsConfigFile, archSystemsConfigFile, romsdirsource, romsdirtarget, arch):
        rules = yaml.safe_load(open(rulesYaml, "r"))
        config = EsSystemConf.loadConfig(configFile)
        es_system = ""

        archSystemsConfig = yaml.safe_load(open(archSystemsConfigFile, "r"))
        systemsConfig     = yaml.safe_load(open(systemsConfigFile, "r"))

        es_system += "<?xml version=\"1.0\"?>\n"
        es_system += "<systemList>\n"
        # sort to be determinist
        sortedRules = sorted(rules)

        print("generating the " + esSystemFile + " file...")
        for system in sortedRules:
            # compute default emulator/cores
            defaultCore = None
            defaultEmulator = None

            if EsSystemConf.keys_exists(archSystemsConfig, system, "emulator"):
                defaultEmulator = archSystemsConfig[system]["emulator"]
            elif EsSystemConf.keys_exists(systemsConfig, system, "emulator"):
                defaultEmulator = systemsConfig[system]["emulator"]
            if EsSystemConf.keys_exists(archSystemsConfig, system, "core"):
                defaultCore = archSystemsConfig[system]["core"]
            elif EsSystemConf.keys_exists(systemsConfig, system, "core"):
                defaultCore = systemsConfig[system]["core"]

            data = {}
            if rules[system]:
                data = rules[system]
            es_system += EsSystemConf.generateSystem(system, data, config, defaultEmulator, defaultCore)
        es_system += "</systemList>\n"
        EsSystemConf.createEsSystem(es_system, esSystemFile)
        EsSystemConf.createEsFeatures(featuresYaml, rules, esFeaturesFile, arch)

        print("removing the " + romsdirtarget + " folder...")
        if os.path.isdir(romsdirtarget):
            shutil.rmtree(romsdirtarget)
        print("generating the " + romsdirtarget + " folder...")
        for system in sortedRules:
            if rules[system]:
                if EsSystemConf.needFolder(system, rules[system], config):
                    EsSystemConf.createFolders(system, rules[system], romsdirsource, romsdirtarget)
                    EsSystemConf.infoSystem(system, rules[system], romsdirtarget)
                else:
                    print("skipping directory for system " + system)

    # check if the folder is required
    @staticmethod
    def needFolder(system, data, config):
        # no emulator
        if "emulators" not in data:
            return False

        for emulator in sorted(data["emulators"]):
            emulatorData = data["emulators"][emulator]
            for core in sorted(emulatorData):
                if EsSystemConf.isValidRequirements(config, emulatorData[core]["requireAnyOf"]):
                    return True
        return False

    # Loads the .config file
    @staticmethod
    def loadConfig(configFile):
        config = {}
        with open(configFile) as fp:
            line = fp.readline()
            while line:
                m = re.search("^([^ ]+)=y$", line)
                if m:
                    config[m.group(1)] = 1
                line = fp.readline()
        return config

    # Generate emulator system
    @staticmethod
    def generateSystem(system, data, config, defaultEmulator, defaultCore):
        listEmulatorsTxt = EsSystemConf.listEmulators(data, config, defaultEmulator, defaultCore)
        if listEmulatorsTxt == "" and not("force" in data and data["force"] == True) :
          return ""

        pathValue      = EsSystemConf.systemPath(system, data)
        platformValue  = EsSystemConf.systemPlatform(system, data)
        listExtensions = EsSystemConf.listExtension(data, False)
        groupValue     = EsSystemConf.systemGroup(system, data)
        command        = EsSystemConf.commandName(data)

        systemTxt =  "  <system>\n"
        systemTxt += "        <fullname>%s</fullname>\n" % (data["name"])
        systemTxt += "        <name>%s</name>\n"           % (system)
        systemTxt += "        <manufacturer>%s</manufacturer>\n" % (data["manufacturer"])
        systemTxt += "        <release>%s</release>\n" % (data["release"])
        systemTxt += "        <hardware>%s</hardware>\n" % (data["hardware"])
        if listExtensions != "":
            if pathValue != "":
                systemTxt += "        <path>%s</path>\n"           % (pathValue)
            systemTxt += "        <extension>%s</extension>\n" % (listExtensions)
            systemTxt += "        <command>%s</command>\n"     % (command)
        if platformValue != "":
            systemTxt += "        <platform>%s</platform>\n"   % (platformValue)
        systemTxt += "        <theme>%s</theme>\n"         % (EsSystemConf.themeName(system, data))
        if groupValue != "":
            systemTxt += "        <group>%s</group>\n" % (groupValue)        
        systemTxt += listEmulatorsTxt
        systemTxt += "  </system>\n"
        return systemTxt

    # Returns the path to the rom folder for the emulator
    @staticmethod
    def systemPath(system, data):
        if "path" in data:
            if data["path"] is None:
                return ""
            else:
                if data["path"][0] == "/": # absolute path
                    return data["path"]
                else:
                    return EsSystemConf.default_parentpath + "/" + data["path"]
        return EsSystemConf.default_parentpath + "/" + system

    @staticmethod
    def systemSubRomsDir(system, data):
        if "path" in data:
            if data["path"] is None:
                return None # no path to create
            else:
                if data["path"][0] == "/": # absolute path
                    return None # don't create absolute paths
                else:
                    return data["path"]
        return system
        
    # Returns the path to the rom folder for the emulator
    @staticmethod
    def systemPlatform(system, data):
        if "platform" in data:
            if data["platform"] is None:
                return ""
            return data["platform"]
        return system

    # Some emulators have different names between roms and themes
    @staticmethod
    def themeName(system, data):
        if "theme" in data:
          return data["theme"]
        return system

    # In case you need to specify a different command line 
    @staticmethod
    def commandName(data):
        if "command" in data:
          return data["command"]
        return EsSystemConf.default_command

    # Create the folders of the consoles in the roms folder
    @staticmethod
    def createFolders(system, data, romsdirsource, romsdirtarget):
        subdir = EsSystemConf.systemSubRomsDir(system, data)

        # nothing to create
        if subdir is None:
            return

        if not os.path.isdir(romsdirtarget + "/" + subdir):
            os.makedirs(romsdirtarget + "/" + subdir)
            # copy from the template one, or just keep it empty
            if os.path.isdir(romsdirsource + "/" + subdir):
                os.rmdir(romsdirtarget + "/" + subdir) # remove the last level
                shutil.copytree(romsdirsource + "/" + subdir, romsdirtarget + "/" + subdir)

    # Creates an _info.txt file inside the emulators folders in roms with the information of the supported extensions.
    @staticmethod
    def infoSystem(system, data, romsdir):
        subdir = EsSystemConf.systemSubRomsDir(system, data)

        # nothing to create
        if subdir is None:
            return

        infoTxt = "## SYSTEM %s ##\n" % (data["name"].upper())
        infoTxt += "-------------------------------------------------------------------------------\n"
        infoTxt += "ROM files extensions accepted: \"%s\"\n" % (EsSystemConf.listExtension(data, False))
        if "comment_en" in data:
            infoTxt += "\n" + data["comment_en"]
        infoTxt += "-------------------------------------------------------------------------------\n"
        infoTxt += "Extensions des fichiers ROMs permises: \"%s\"\n" % (EsSystemConf.listExtension(data, False))
        if "comment_fr" in data:
            infoTxt += "\n" + data["comment_fr"]

        arqtxt = romsdir + "/" + subdir + "/" + "_info.txt"

        systemsInfo = open(arqtxt, 'w')
        systemsInfo.write(infoTxt)
        systemsInfo.close()

    # Writes the information in the es_systems.cfg file
    @staticmethod
    def createEsSystem(essystem, esSystemFile):
        es_systems = open(esSystemFile, "w")
        es_systems.write(essystem)
        es_systems.close()

    # Write the information in the es_features.cfg file
    @staticmethod
    def createEsFeatures(featuresYaml, systems, esFeaturesFile, arch):
        features = ordered_load(open(featuresYaml, "r"))
        es_features = open(esFeaturesFile, "w")
        featuresTxt = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n"
        featuresTxt += "<features>\n"
        for emulator in features:
            emulator_featuresTxt = "videomode" # on batocera, the videomode is supported for any board allowing to change resolution via configgen. It is not related to the emulator
            if "features" in features[emulator]:
                for feature in features[emulator]["features"]:
                    if emulator_featuresTxt != "":
                        emulator_featuresTxt += ", "
                    emulator_featuresTxt += feature
            featuresTxt += "  <emulator name=\"{}\" features=\"{}\"".format(emulator, emulator_featuresTxt)

            if "cores" in features[emulator] or "systems" in features[emulator] or "cfeatures" in features[emulator]:
                featuresTxt += ">\n"
                if "cores" in features[emulator]:
                    featuresTxt += "    <cores>\n"
                    for core in features[emulator]["cores"]:
                        core_featuresTxt = ""
                        if "features" in features[emulator]["cores"][core]:
                            for feature in features[emulator]["cores"][core]["features"]:
                                if core_featuresTxt != "":
                                    core_featuresTxt += ", "
                                core_featuresTxt += feature
                        if "cfeatures" in features[emulator]["cores"][core] or "systems" in features[emulator]["cores"][core]:
                            featuresTxt += "      <core name=\"{}\" features=\"{}\">\n".format(core, core_featuresTxt)
                            # core features
                            if "cfeatures" in features[emulator]["cores"][core]:
                               for cfeature in features[emulator]["cores"][core]["cfeatures"]:
                                   if "archs_include" not in features[emulator]["cores"][core]["cfeatures"][cfeature] or arch in features[emulator]["cores"][core]["cfeatures"][cfeature]["archs_include"]:
                                       description = ""
                                       if "description" in features[emulator]["cores"][core]["cfeatures"][cfeature]:
                                           description = features[emulator]["cores"][core]["cfeatures"][cfeature]["description"]
                                       featuresTxt += "        <feature name=\"{}\" value=\"{}\" description=\"{}\">\n".format(features[emulator]["cores"][core]["cfeatures"][cfeature]["prompt"], cfeature, description)
                                       for choice in features[emulator]["cores"][core]["cfeatures"][cfeature]["choices"]:
                                           featuresTxt += "          <choice name=\"{}\" value=\"{}\" />\n".format(choice, features[emulator]["cores"][core]["cfeatures"][cfeature]["choices"][choice])
                                       featuresTxt += "        </feature>\n"
                                   else:
                                       print("skipping core " + emulator + "/" + core + " cfeature " + cfeature)
                            # #############

                            # systems in cores/core
                            if "systems" in features[emulator]["cores"][core]:
                               featuresTxt += "        <systems>\n"
                               for system in features[emulator]["cores"][core]["systems"]:
                                   system_featuresTxt = ""
                                   if "features" in features[emulator]["cores"][core]["systems"][system]:
                                       for feature in features[emulator]["cores"][core]["systems"][system]["features"]:
                                           if system_featuresTxt != "":
                                               system_featuresTxt += ", "
                                           system_featuresTxt += feature
                                   featuresTxt += "          <system name=\"{}\" features=\"{}\" >\n".format(system, system_featuresTxt)
                                   if "cfeatures" in features[emulator]["cores"][core]["systems"][system]:
                                       for cfeature in features[emulator]["cores"][core]["systems"][system]["cfeatures"]:
                                           if "archs_include" not in features[emulator]["cores"][core]["systems"][system]["cfeatures"][cfeature] or arch in features[emulator]["cores"][core]["systems"][system]["cfeatures"][cfeature]["archs_include"]:
                                               description = ""
                                               if "description" in features[emulator]["cores"][core]["systems"][system]["cfeatures"][cfeature]:
                                                   description = features[emulator]["cores"][core]["systems"][system]["cfeatures"][cfeature]["description"]
                                               featuresTxt += "            <feature name=\"{}\" value=\"{}\" description=\"{}\">\n".format(features[emulator]["cores"][core]["systems"][system]["cfeatures"][cfeature]["prompt"], cfeature, description)
                                               for choice in features[emulator]["cores"][core]["systems"][system]["cfeatures"][cfeature]["choices"]:
                                                   featuresTxt += "              <choice name=\"{}\" value=\"{}\" />\n".format(choice, features[emulator]["cores"][core]["systems"][system]["cfeatures"][cfeature]["choices"][choice])
                                               featuresTxt += "            </feature>\n"
                                           else:
                                               print("skipping system " + emulator + "/" + system + " cfeature " + cfeature)
                                   featuresTxt += "          </system>\n"
                               featuresTxt += "        </systems>\n"
                               ###
                            featuresTxt += "      </core>\n"
                        else:
                            featuresTxt += "      <core name=\"{}\" features=\"{}\" />\n".format(core, core_featuresTxt)
                    featuresTxt += "    </cores>\n"
                if "systems" in features[emulator]:
                    featuresTxt += "    <systems>\n"
                    for system in features[emulator]["systems"]:
                        system_featuresTxt = ""
                        if "features" in features[emulator]["systems"][system]:
                            for feature in features[emulator]["systems"][system]["features"]:
                                if system_featuresTxt != "":
                                    system_featuresTxt += ", "
                                system_featuresTxt += feature
                        featuresTxt += "      <system name=\"{}\" features=\"{}\" >\n".format(system, system_featuresTxt)
                        if "cfeatures" in features[emulator]["systems"][system]:
                            for cfeature in features[emulator]["systems"][system]["cfeatures"]:
                                if "archs_include" not in features[emulator]["systems"][system]["cfeatures"][cfeature] or arch in features[emulator]["systems"][system]["cfeatures"][cfeature]["archs_include"]:
                                    description = ""
                                    if "description" in features[emulator]["systems"][system]["cfeatures"][cfeature]:
                                        description = features[emulator]["systems"][system]["cfeatures"][cfeature]["description"]
                                    featuresTxt += "        <feature name=\"{}\" value=\"{}\" description=\"{}\">\n".format(features[emulator]["systems"][system]["cfeatures"][cfeature]["prompt"], cfeature, description)
                                    for choice in features[emulator]["systems"][system]["cfeatures"][cfeature]["choices"]:
                                        featuresTxt += "        <choice name=\"{}\" value=\"{}\" />\n".format(choice, features[emulator]["systems"][system]["cfeatures"][cfeature]["choices"][choice])
                                    featuresTxt += "        </feature>\n"
                                else:
                                    print("skipping system " + emulator + "/" + system + " cfeature " + cfeature)
                        featuresTxt += "      </system>\n"
                    featuresTxt += "    </systems>\n"
                if "cfeatures" in features[emulator]:
                    for cfeature in features[emulator]["cfeatures"]:
                        if "archs_include" not in features[emulator]["cfeatures"][cfeature] or arch in features[emulator]["cfeatures"][cfeature]["archs_include"]:
                            description = ""
                            if "description" in features[emulator]["cfeatures"][cfeature]:
                                description = features[emulator]["cfeatures"][cfeature]["description"]
                            featuresTxt += "    <feature name=\"{}\" value=\"{}\" description=\"{}\">\n".format(features[emulator]["cfeatures"][cfeature]["prompt"], cfeature, description)
                            for choice in features[emulator]["cfeatures"][cfeature]["choices"]:
                                featuresTxt += "      <choice name=\"{}\" value=\"{}\" />\n".format(choice, features[emulator]["cfeatures"][cfeature]["choices"][choice])
                            featuresTxt += "    </feature>\n"
                        else:
                            print("skipping emulator " + emulator + " cfeature " + cfeature)

                featuresTxt += "  </emulator>\n"
            else:
                featuresTxt += " />\n"
        featuresTxt += "</features>\n"
        es_features.write(featuresTxt)
        es_features.close()

    # Returns the extensions supported by the emulator
    @staticmethod
    def listExtension(data, uppercase):
        extension = ""
        if "extensions" in data:
            extensions = data["extensions"]
            firstExt = True
            for item in extensions:
                if not firstExt:
                    extension += " "
                firstExt = False
                extension += "." + item.lower()
                if uppercase == True:
                    extension += " ." + item.upper()
        return extension

    # Returns group to emulator rom folder
    @staticmethod
    def systemGroup(system, data):
        if "group" in data:
            if data["group"] is None:
                return ""
            return data["group"]
        return ""

    # Returns the validity of prerequisites
    @staticmethod
    def isValidRequirements(config, requirements):
        if len(requirements) == 0:
            return True

        for requirement in requirements:
            if isinstance(requirement, list):
                subreqValid = True
                for reqitem in requirement:
                    if reqitem not in config:
                        subreq = False
                if subreq:
                    return True
            else:
                if requirement in config:
                    return True
        return False

    # Returns the enabled cores in the .config file for the emulator
    @staticmethod
    def listEmulators(data, config, defaultEmulator, defaultCore):
        listEmulatorsTxt = ""
        emulators = {}
        if "emulators" in data:
            emulators = data["emulators"]

        emulatorsTxt = ""
        for emulator in sorted(emulators):
            emulatorData = data["emulators"][emulator]

            emulatorTxt = "            <emulator name=\"%s\">\n" % (emulator)
            emulatorTxt += "                <cores>\n"

            # CORES
            coresTxt = ""
            for core in sorted(emulatorData):
                if EsSystemConf.isValidRequirements(config, emulatorData[core]["requireAnyOf"]):
                    incompatible_extensionsTxt = ""
                    if "incompatible_extensions" in emulatorData[core]:
                        for ext in emulatorData[core]["incompatible_extensions"]:
                            if incompatible_extensionsTxt != "":
                                incompatible_extensionsTxt += " "
                            incompatible_extensionsTxt += "." + ext.lower()
                        incompatible_extensionsTxt = " incompatible_extensions=\"" + incompatible_extensionsTxt + "\""

                    if emulator == defaultEmulator and core == defaultCore:
                        coresTxt += "                    <core default=\"true\"%s>%s</core>\n" % (incompatible_extensionsTxt, core)
                    else:
                        coresTxt += "                    <core%s>%s</core>\n" % (incompatible_extensionsTxt, core)

            if coresTxt == "":
                emulatorTxt = ""
            else:
                emulatorTxt  += coresTxt
                emulatorTxt  += "                </cores>\n"
                emulatorTxt  += "            </emulator>\n"
                emulatorsTxt += emulatorTxt

        if emulatorsTxt == "":
            listEmulatorsTxt = ""
        else:
            listEmulatorsTxt += "        <emulators>\n"
            listEmulatorsTxt += emulatorsTxt
            listEmulatorsTxt += "        </emulators>\n"

        return listEmulatorsTxt

    @staticmethod
    def keys_exists(element, *keys):
        '''
        Check if *keys (nested) exists in `element` (dict).
        '''
        if not isinstance(element, dict):
            raise AttributeError('keys_exists() expects dict as first argument.')
        if len(keys) == 0:
            raise AttributeError('keys_exists() expects at least two arguments, one given.')

        _element = element
        for key in keys:
            try:
                _element = _element[key]
            except KeyError:
                return False
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("yml",           help="es_systems.yml definition file")
    parser.add_argument("features",      help="es_features.yml file")
    parser.add_argument("config",        help=".config buildroot file")
    parser.add_argument("es_systems",    help="es_systems.cfg emulationstation file")
    parser.add_argument("es_features",   help="es_features.cfg emulationstation file")
    parser.add_argument("gen_defaults_global", help="global configgen defaults")
    parser.add_argument("gen_defaults_arch",   help="defaults configgen defaults")
    parser.add_argument("romsdirsource", help="emulationstation roms directory")
    parser.add_argument("romsdirtarget", help="emulationstation roms directory")
    parser.add_argument("arch", help="arch")
    args = parser.parse_args()
    EsSystemConf.generate(args.yml, args.features, args.config, args.es_systems, args.es_features, args.gen_defaults_global, args.gen_defaults_arch, args.romsdirsource, args.romsdirtarget, args.arch)
