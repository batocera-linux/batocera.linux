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
import glob
import json
from os.path import basename

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
    default_command    = "emulatorlauncher %CONTROLLERSCONFIG% -system %SYSTEM% -rom %ROM% -gameinfoxml %GAMEINFOXML% -systemname %SYSTEMNAME%"

    # Generate the es_systems.cfg file by searching the information in the es_system.yml file
    @staticmethod
    def generate(rulesYaml, featuresYaml, configFile, esSystemFile, esFeaturesFile, esTranslationFile, esKeysTranslationFile, esKeysParentFolder, esBlacklistedWordsFile, systemsConfigFile, archSystemsConfigFile, romsdirsource, romsdirtarget, arch):
        rules = yaml.safe_load(open(rulesYaml, "r"))
        config = EsSystemConf.loadConfig(configFile)
        es_system = ""

        archSystemsConfig = yaml.safe_load(open(archSystemsConfigFile, "r"))
        if archSystemsConfig is None:
            archSystemsConfig = {}
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

        toTranslateOnArch = {}
        EsSystemConf.createEsFeatures(featuresYaml, rules, esFeaturesFile, arch, toTranslateOnArch)
        toTranslate = EsSystemConf.findTranslations(featuresYaml)

        # remove blacklisted words
        backlistWords = {}
        with open(esBlacklistedWordsFile) as fp:
            line = fp.readline().rstrip('\n')
            while line:
                if line in toTranslate:
                    del toTranslate[line]
                line = fp.readline().rstrip('\n')
        ###

        EsSystemConf.createEsTranslations(esTranslationFile, toTranslate)
        EsSystemConf.createEsKeysTranslations(esKeysTranslationFile, esKeysParentFolder)

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
        systemTxt += "        <fullname>%s</fullname>\n" % (EsSystemConf.protectXml(data["name"]))
        systemTxt += "        <name>%s</name>\n"           % (system)
        systemTxt += "        <manufacturer>%s</manufacturer>\n" % (EsSystemConf.protectXml(data["manufacturer"]))
        systemTxt += "        <release>%s</release>\n" % (EsSystemConf.protectXml(data["release"]))
        systemTxt += "        <hardware>%s</hardware>\n" % (EsSystemConf.protectXml(data["hardware"]))
        if listExtensions != "":
            if pathValue != "":
                systemTxt += "        <path>%s</path>\n"           % (pathValue)
            systemTxt += "        <extension>%s</extension>\n" % (listExtensions)
            systemTxt += "        <command>%s</command>\n"     % (command)
        if platformValue != "":
            systemTxt += "        <platform>%s</platform>\n"   % (EsSystemConf.protectXml(platformValue))
        systemTxt += "        <theme>%s</theme>\n"         % (EsSystemConf.themeName(system, data))
        if groupValue != "":
            systemTxt += "        <group>%s</group>\n" % (EsSystemConf.protectXml(groupValue))
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

    # generate the fake translations from *.keys files
    @staticmethod
    def createEsKeysTranslations(esKeysTranslationFile, esKeysParentFolder):
        print("generating {}...".format(esKeysTranslationFile))
        files = glob.glob(esKeysParentFolder+'/**/*.keys', recursive=True)
        vals = {}
        for file in files:
            print("... {}".format(file))
            content = json.load(open(file))
            for device in content:
                for action in content[device]:
                    if "description" in action:
                        if action["description"] not in vals:
                            vals[action["description"]] = { basename(file): {} }
                        else:
                            vals[action["description"]][basename(file)] = {}
        
        fd = open(esKeysTranslationFile, 'w')
        fd.write("// file generated automatically by batocera-es-system.py, don't modify it\n\n")
        n = 0
        for tr in vals:
            vcomment = ""
            vn = 0
            for v in vals[tr]:
                if vn < 5:
                    if vcomment != "":
                        vcomment = vcomment + ", "
                    vcomment = vcomment + v
                else:
                    if vn == 5:
                        vcomment = vcomment + ", ..."
                vn = vn+1
            fd.write("/* TRANSLATION: " + vcomment + " */\n");
            fd.write("#define fake_gettext_external_" + str(n) + " pgettext(\"keys_files\", \"" + tr.replace("\"", "\\\"") + "\")\n")
            n = n+1
        fd.close()

    # generate the fake translations from external options
    @staticmethod
    def createEsTranslations(esTranslationFile, toTranslate):
        if toTranslate is None or not toTranslate:
            return
        fd = open(esTranslationFile, 'w')
        n = 1
        fd.write("// file generated automatically by batocera-es-system.py, don't modify it\n\n")
        for tr in toTranslate:
              # skip if tr is None
            if tr is None:
                continue
            # skip empty string
            if tr == "":
                continue
            # skip numbers (8, 10, 500+)
            m = re.search("^[0-9]+[+]?$", tr)
            if m:
               continue
            # skip floats (2.5)
            m = re.search("^[0-9]+\.[0-9]+[+]?$", tr)
            if m:
               continue
            # skip ratio (4:3)
            m = re.search("^[0-9]+:[0-9]+$", tr)
            if m:
               continue
            # skip ratio (4/3)
            m = re.search("^[0-9]+/[0-9]+$", tr)
            if m:
               continue
            # skip numbers (100%, 3x, +50%)
            m = re.search("^[+-]?[0-9]+[%x]?$", tr)
            if m:
                continue
            # skip resolutions (640x480)
            m = re.search("^[0-9]+x[0-9]+$", tr)
            if m:
                continue
            # skip resolutions (2x 640x480, 4x (640x480), x4 640x480, 3x 1080p (1920x1584), 2x 720p, 7x 2880p 5K
            m = re.search("^[xX]?[0-9]*[xX]?[ ]*\(?[0-9]+[x]?[0-9]+[pK]?\)?[ ]*\(?[0-9]+[x]?[0-9]+[pK]?\)?$", tr)
            if m:
                continue

            vcomment = ""
            vn = 0
            for v in sorted(toTranslate[tr], key=lambda x: x["emulator"] + ("/" + x["core"] if "core" in x else "")):
                if vn < 5:
                    if vcomment != "":
                        vcomment = vcomment + ", "
                    if "core" not in v or v["emulator"] == v["core"]:
                        vcomment = vcomment + v["emulator"]
                    else:
                        vcomment = vcomment + v["emulator"] + "/" + v["core"]
                else:
                    if vn == 5:
                        vcomment = vcomment + ", ..."
                vn = vn+1
            fd.write("/* TRANSLATION: " + vcomment + " */\n");
            fd.write("#define fake_gettext_external_" + str(n) + " pgettext(\"game_options\", \"" + tr.replace("\"", "\\\"") + "\")\n")
            n = n+1
        fd.close()

    @staticmethod
    def protectXml(strval):
        strval = str(strval)
        strval = strval.replace("&", "&amp;")
        strval = strval.replace("<", "&lt;")
        strval = strval.replace(">", "&gt;")
        strval = strval.replace("\"", "&quot;")
        strval = strval.replace("\n", "&#x0a;")
        return strval

    @staticmethod
    def addCommentToDictKey(dictvar, dictval, comment):
        if dictval not in dictvar:
            dictvar[dictval] = []
        dictvar[dictval].append(comment)

    @staticmethod
    def getXmlFeature(nfspaces, key, infos, toTranslate, emulator, core):
        fspaces = " " * nfspaces
        featuresTxt = ""
        description = ""
        if "description" in infos:
            description = infos["description"]
        submenustr = ""
        if "submenu" in infos:
            submenustr = " submenu=\"{}\"".format(EsSystemConf.protectXml(infos["submenu"]))
        groupstr = ""
        if "group" in infos:
            groupstr = " group=\"{}\"".format(EsSystemConf.protectXml(infos["group"]))
        orderstr = ""
        if "order" in infos:
            orderstr = " order=\"{}\"".format(EsSystemConf.protectXml(infos["order"]))
        presetstr = ""
        if "preset" in infos:
            presetstr = " preset=\"{}\"".format(EsSystemConf.protectXml(infos["preset"]))
        if "preset_parameters" in infos:
            presetstr +=  " preset-parameters=\"{}\"".format(EsSystemConf.protectXml(infos["preset_parameters"]))
        featuresTxt += fspaces + "<feature name=\"{}\"{}{}{} value=\"{}\" description=\"{}\"{}>\n".format(EsSystemConf.protectXml(infos["prompt"]), submenustr, groupstr, orderstr, EsSystemConf.protectXml(key), EsSystemConf.protectXml(description), presetstr)
        EsSystemConf.addCommentToDictKey(toTranslate, infos["prompt"], { "emulator": emulator, "core": core })
        EsSystemConf.addCommentToDictKey(toTranslate, description, { "emulator": emulator, "core": core })
        if "preset" not in infos:
            for choice in infos["choices"]:
                featuresTxt += fspaces + "  <choice name=\"{}\" value=\"{}\" />\n".format(EsSystemConf.protectXml(choice), EsSystemConf.protectXml(infos["choices"][choice]))
                EsSystemConf.addCommentToDictKey(toTranslate, choice, { "emulator": emulator, "core": core })
        featuresTxt += fspaces + "</feature>\n"
        return featuresTxt

    @staticmethod
    def array2vallist(arr, res = ""):
        for x in arr:
            if res != "":
                res += ", "
            res += x
        return res

    @staticmethod
    def archValid(arch, obj):
        if "archs_exclude" in obj and arch in obj["archs_exclude"]:
            return false
        return "archs_include" not in obj or arch in obj["archs_include"]

    # Write the information in the es_features.cfg file
    @staticmethod
    def createEsFeatures(featuresYaml, systems, esFeaturesFile, arch, toTranslate):
        features = ordered_load(open(featuresYaml, "r"))
        es_features = open(esFeaturesFile, "w")
        featuresTxt = "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n"
        featuresTxt += "<features>\n"
        for emulator in features:
            emulator_featuresTxt = ""
            if "features" in features[emulator]:
                emulator_featuresTxt = EsSystemConf.array2vallist(features[emulator]["features"], emulator_featuresTxt)
            if emulator == "global":
                featuresTxt += "  <globalFeatures"
            elif emulator == "shared":
                featuresTxt += "  <sharedFeatures"
            else:
                featuresTxt += "  <emulator name=\"{}\" features=\"{}\"".format(EsSystemConf.protectXml(emulator), EsSystemConf.protectXml(emulator_featuresTxt))

            if "cores" in features[emulator] or "systems" in features[emulator] or "cfeatures" in features[emulator] or "shared" in features[emulator]:
                featuresTxt += ">\n"
                if "cores" in features[emulator]:
                    featuresTxt += "    <cores>\n"
                    for core in features[emulator]["cores"]:
                        core_featuresTxt = ""
                        if "features" in features[emulator]["cores"][core]:
                            core_featuresTxt = EsSystemConf.array2vallist(features[emulator]["cores"][core]["features"], core_featuresTxt)
                        if "cfeatures" in features[emulator]["cores"][core] or "shared" in features[emulator]["cores"][core] or "systems" in features[emulator]["cores"][core]:
                            featuresTxt += "      <core name=\"{}\" features=\"{}\">\n".format(EsSystemConf.protectXml(core), EsSystemConf.protectXml(core_featuresTxt))
                            if "shared" in features[emulator]["cores"][core]:
                                for shared in features[emulator]["cores"][core]["shared"]:
                                    if EsSystemConf.archValid(arch, features["shared"]["cfeatures"][shared]):
                                        featuresTxt += "        <sharedFeature value=\"{}\" />\n".format(EsSystemConf.protectXml(shared))
                            # core features
                            if "cfeatures" in features[emulator]["cores"][core]:
                               for cfeature in features[emulator]["cores"][core]["cfeatures"]:
                                   if EsSystemConf.archValid(arch, features[emulator]["cores"][core]["cfeatures"][cfeature]):
                                       featuresTxt += EsSystemConf.getXmlFeature(8, cfeature, features[emulator]["cores"][core]["cfeatures"][cfeature], toTranslate, emulator, core)
                                   else:
                                       print("skipping core " + emulator + "/" + core + " cfeature " + cfeature)
                            # #############

                            # systems in cores/core
                            if "systems" in features[emulator]["cores"][core]:
                               featuresTxt += "        <systems>\n"
                               for system in features[emulator]["cores"][core]["systems"]:
                                   system_featuresTxt = ""
                                   if "features" in features[emulator]["cores"][core]["systems"][system]:
                                       system_featuresTxt = EsSystemConf.array2vallist(features[emulator]["cores"][core]["systems"][system]["features"], system_featuresTxt)
                                   featuresTxt += "          <system name=\"{}\" features=\"{}\" >\n".format(EsSystemConf.protectXml(system), EsSystemConf.protectXml(system_featuresTxt))
                                   if "shared" in features[emulator]["cores"][core]["systems"][system]:
                                       for shared in features[emulator]["cores"][core]["systems"][system]["shared"]:
                                           if EsSystemConf.archValid(arch, features["shared"]["cfeatures"][shared]):
                                               featuresTxt += "    <sharedFeature value=\"{}\" />\n".format(EsSystemConf.protectXml(shared))
                                           else:
                                               print("skipping system " + emulator + "/" + system + " shared " + shared)
                                   if "cfeatures" in features[emulator]["cores"][core]["systems"][system]:
                                       for cfeature in features[emulator]["cores"][core]["systems"][system]["cfeatures"]:
                                           if EsSystemConf.archValid(arch, features[emulator]["cores"][core]["systems"][system]["cfeatures"][cfeature]):
                                               featuresTxt += EsSystemConf.getXmlFeature(12, cfeature, features[emulator]["cores"][core]["systems"][system]["cfeatures"][cfeature], toTranslate, emulator, core)
                                           else:
                                               print("skipping system " + emulator + "/" + system + " cfeature " + cfeature)
                                   featuresTxt += "          </system>\n"
                               featuresTxt += "        </systems>\n"
                               ###
                            featuresTxt += "      </core>\n"
                        else:
                            featuresTxt += "      <core name=\"{}\" features=\"{}\" />\n".format(EsSystemConf.protectXml(core), EsSystemConf.protectXml(core_featuresTxt))
                    featuresTxt += "    </cores>\n"
                if "systems" in features[emulator]:
                    featuresTxt += "    <systems>\n"
                    for system in features[emulator]["systems"]:
                        system_featuresTxt = ""
                        if "features" in features[emulator]["systems"][system]:
                            system_featuresTxt = EsSystemConf.array2vallist(features[emulator]["systems"][system]["features"], system_featuresTxt)
                        featuresTxt += "      <system name=\"{}\" features=\"{}\" >\n".format(EsSystemConf.protectXml(system), EsSystemConf.protectXml(system_featuresTxt))
                        if "shared" in features[emulator]["systems"][system]:
                            for shared in features[emulator]["systems"][system]["shared"]:
                                if EsSystemConf.archValid(arch, features["shared"]["cfeatures"][shared]):
                                    featuresTxt += "    <sharedFeature value=\"{}\" />\n".format(EsSystemConf.protectXml(shared))
                                else:
                                    print("skipping system " + emulator + "/" + system + " shared " + shared)
                        if "cfeatures" in features[emulator]["systems"][system]:
                            for cfeature in features[emulator]["systems"][system]["cfeatures"]:
                                if EsSystemConf.archValid(arch, features[emulator]["systems"][system]["cfeatures"][cfeature]):
                                    featuresTxt += EsSystemConf.getXmlFeature(8, cfeature, features[emulator]["systems"][system]["cfeatures"][cfeature], toTranslate, emulator, core)
                                else:
                                    print("skipping system " + emulator + "/" + system + " cfeature " + cfeature)
                        featuresTxt += "      </system>\n"
                    featuresTxt += "    </systems>\n"
                if "shared" in features[emulator]:
                    for shared in features[emulator]["shared"]:
                        if EsSystemConf.archValid(arch, features["shared"]["cfeatures"][shared]):
                            featuresTxt += "    <sharedFeature value=\"{}\" />\n".format(EsSystemConf.protectXml(shared))
                        else:
                            print("skipping emulator " + emulator + " shared " + shared)

                if "cfeatures" in features[emulator]:
                    for cfeature in features[emulator]["cfeatures"]:
                        if EsSystemConf.archValid(arch, features[emulator]["cfeatures"][cfeature]):
                            featuresTxt += EsSystemConf.getXmlFeature(4, cfeature, features[emulator]["cfeatures"][cfeature], toTranslate, emulator, None)
                        else:
                            print("skipping emulator " + emulator + " cfeature " + cfeature)

                if emulator == "global":
                    featuresTxt += "  </globalFeatures>\n"
                elif emulator == "shared":
                    featuresTxt += "  </sharedFeatures>\n"
                else:
                    featuresTxt += "  </emulator>\n"
            else:
                featuresTxt += " />\n"
        featuresTxt += "</features>\n"
        es_features.write(featuresTxt)
        es_features.close()

    # find all translation independantly of the arch
    @staticmethod
    def findTranslations(featuresYaml):
        toTranslate = {}
        features = ordered_load(open(featuresYaml, "r"))
        for emulator in features:
            if "cores" in features[emulator] or "systems" in features[emulator] or "cfeatures" in features[emulator] or "shared" in features[emulator]:
                if "cores" in features[emulator]:
                    for core in features[emulator]["cores"]:
                        if "cfeatures" in features[emulator]["cores"][core] or "systems" in features[emulator]["cores"][core]:
                            # core features
                            if "cfeatures" in features[emulator]["cores"][core]:
                               for cfeature in features[emulator]["cores"][core]["cfeatures"]:
                                   for tag in ["description", "submenu", "group", "prompt"]:
                                       if tag in features[emulator]["cores"][core]["cfeatures"][cfeature]:
                                           tagval = features[emulator]["cores"][core]["cfeatures"][cfeature][tag]
                                           EsSystemConf.addCommentToDictKey(toTranslate, tagval, { "emulator": emulator, "core": core })
                                   if "choices" in features[emulator]["cores"][core]["cfeatures"][cfeature]:
                                       for choice in features[emulator]["cores"][core]["cfeatures"][cfeature]["choices"]:
                                           EsSystemConf.addCommentToDictKey(toTranslate, choice, { "emulator": emulator, "core": core })
                            # #############

                            # systems in cores/core
                            if "systems" in features[emulator]["cores"][core]:
                               for system in features[emulator]["cores"][core]["systems"]:
                                   if "cfeatures" in features[emulator]["cores"][core]["systems"][system]:
                                       for cfeature in features[emulator]["cores"][core]["systems"][system]["cfeatures"]:
                                           for tag in ["description", "submenu", "group", "prompt"]:
                                               if tag in features[emulator]["cores"][core]["systems"][system]["cfeatures"][cfeature]:
                                                   tagval = features[emulator]["cores"][core]["systems"][system]["cfeatures"][cfeature][tag]
                                                   EsSystemConf.addCommentToDictKey(toTranslate, tagval, { "emulator": emulator, "core": core })
                                           if "choices" in features[emulator]["cores"][core]["systems"][system]["cfeatures"][cfeature]:
                                               for choice in features[emulator]["cores"][core]["systems"][system]["cfeatures"][cfeature]["choices"]:
                                                   EsSystemConf.addCommentToDictKey(toTranslate, choice, { "emulator": emulator, "core": core })
                if "systems" in features[emulator]:
                    for system in features[emulator]["systems"]:
                        if "cfeatures" in features[emulator]["systems"][system]:
                            for cfeature in features[emulator]["systems"][system]["cfeatures"]:
                                for tag in ["description", "submenu", "group", "prompt"]:
                                    if tag in features[emulator]["systems"][system]["cfeatures"][cfeature]:
                                        tagval = features[emulator]["systems"][system]["cfeatures"][cfeature][tag]
                                        EsSystemConf.addCommentToDictKey(toTranslate, tagval, { "emulator": emulator, "core": core })
                                if "choices" in features[emulator]["systems"][system]["cfeatures"][cfeature]:
                                    for choice in features[emulator]["systems"][system]["cfeatures"][cfeature]["choices"]:
                                        EsSystemConf.addCommentToDictKey(toTranslate, choice, { "emulator": emulator, "core": core })
                if "cfeatures" in features[emulator]:
                    for cfeature in features[emulator]["cfeatures"]:
                        for tag in ["description", "submenu", "group", "prompt"]:
                            if tag in features[emulator]["cfeatures"][cfeature]:
                                tagval = features[emulator]["cfeatures"][cfeature][tag]
                                EsSystemConf.addCommentToDictKey(toTranslate, tagval, { "emulator": emulator })
                        if "choices" in features[emulator]["cfeatures"][cfeature]:
                            for choice in features[emulator]["cfeatures"][cfeature]["choices"]:
                                EsSystemConf.addCommentToDictKey(toTranslate, choice, { "emulator": emulator })
        return toTranslate

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
                extension += "." + str(item).lower()
                if uppercase == True:
                    extension += " ." + str(item).upper()
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
                            incompatible_extensionsTxt += "." + str(ext).lower()
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
    parser.add_argument("es_translations",  help="es_translations.h file")
    parser.add_argument("es_keys_translations", help="es_keys_translations.h file")
    parser.add_argument("es_keys_parent_folder", help="es_keys files parent folder (where to search for .keys files)")
    parser.add_argument("blacklisted_words",  help="blacklisted_words.txt file")
    parser.add_argument("config",        help=".config buildroot file")
    parser.add_argument("es_systems",    help="es_systems.cfg emulationstation file")
    parser.add_argument("es_features",   help="es_features.cfg emulationstation file")
    parser.add_argument("gen_defaults_global", help="global configgen defaults")
    parser.add_argument("gen_defaults_arch",   help="defaults configgen defaults")
    parser.add_argument("romsdirsource", help="emulationstation roms directory")
    parser.add_argument("romsdirtarget", help="emulationstation roms directory")
    parser.add_argument("arch", help="arch")
    args = parser.parse_args()
    EsSystemConf.generate(args.yml, args.features, args.config, args.es_systems, args.es_features, args.es_translations, args.es_keys_translations, args.es_keys_parent_folder, args.blacklisted_words, args.gen_defaults_global, args.gen_defaults_arch, args.romsdirsource, args.romsdirtarget, args.arch)
