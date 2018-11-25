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

class EsSystemConf:

    default_parentpath = "/recalbox/share/roms"
    default_command    = "python /usr/lib/python2.7/site-packages/configgen/emulatorlauncher.py %CONTROLLERSCONFIG% -system %SYSTEM% -rom %ROM% -emulator %EMULATOR% -core %CORE% -ratio %RATIO%"

    # Generate the es_systems.cfg file by searching the information in the es_system.yml file
    @staticmethod
    def generate(rulesYaml, configFile, esSystemFile, romsdirsource, romsdirtarget):
        rules = yaml.load(file(rulesYaml, "r"))
        config = EsSystemConf.loadConfig(configFile)
        es_system = ""

        es_system += "<?xml version=\"1.0\"?>\n"
        es_system += "<systemList>\n"
        # sort to be determinist
        sortedRules = sorted(rules)

        print "generating the " + esSystemFile + " file..."
        for system in sortedRules:
            data = {}
            if rules[system]:
                data = rules[system]
            es_system += EsSystemConf.generateSystem(system, data, config)
        es_system += "</systemList>\n"
        EsSystemConf.createEsSystem(es_system, esSystemFile)

        print "removing the " + romsdirtarget + " folder..."
        if os.path.isdir(romsdirtarget):
            shutil.rmtree(romsdirtarget)
        print "generating the " + romsdirtarget + " folder..."
        for system in sortedRules:
            if rules[system]:
                if EsSystemConf.needFolder(system, rules[system], config):
                    EsSystemConf.createFolders(system, rules[system], romsdirsource, romsdirtarget)
                    EsSystemConf.infoSystem(system, rules[system], romsdirtarget)
                else:
                    print "skipping directory for system " + system

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
    def generateSystem(system, data, config):
        listEmulatorsTxt = EsSystemConf.listEmulators(data, config)
        if listEmulatorsTxt == "" and not("force" in data and data["force"] == True) :
          return ""

        pathValue      = EsSystemConf.systemPath(system, data)
        platformValue  = EsSystemConf.systemPlatform(system, data)
        listExtensions = EsSystemConf.listExtension(data, True)

        systemTxt =  "  <system>\n"
        systemTxt += "        <fullname>%s</fullname>\n" % (data["name"])
        systemTxt += "        <name>%s</name>\n"           % (system)
        if pathValue != "":
            systemTxt += "        <path>%s</path>\n"           % (pathValue)
        if listExtensions != "":
            systemTxt += "        <extension>%s</extension>\n" % (listExtensions)
        systemTxt += "        <command>%s</command>\n"     % (EsSystemConf.default_command)
        if platformValue != "":
            systemTxt += "        <platform>%s</platform>\n"   % (platformValue)
        systemTxt += "        <theme>%s</theme>\n"         % (EsSystemConf.themeName(system, data))
        if not("includeEmulators" in data and data["includeEmulators"] is False):
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
        systemsInfo.write(infoTxt.encode('utf-8'))
        systemsInfo.close()

    # Writes the information in the es_systems.cfg file
    @staticmethod
    def createEsSystem(essystem, esSystemFile):
        es_systems = open(esSystemFile, "w")
        es_systems.write(essystem)
        es_systems.close()

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
    def listEmulators(data, config):
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
                    coresTxt += "                    <core>%s</core>\n" % (core)

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("yml",        help="es_systems.yml definition file")
    parser.add_argument("config",     help=".config buildroot file")
    parser.add_argument("es_systems", help="es_systems.cfg emulationstation file")
    parser.add_argument("romsdirsource",    help="emulationstation roms directory")
    parser.add_argument("romsdirtarget",    help="emulationstation roms directory")
    args = parser.parse_args()
    EsSystemConf.generate(args.yml, args.config, args.es_systems, args.romsdirsource, args.romsdirtarget)
