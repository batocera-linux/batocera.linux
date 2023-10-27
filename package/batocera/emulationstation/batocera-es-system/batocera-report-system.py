#
# - Generates the es_systems.cfg file
# - Generates roms folder and emulators folders
# - Generate the _info.txt file with the emulator information
# - Information from the emulators are being extracted from the file es_system.yml
#
import yaml
import re
import argparse
import json
import os

class SortedListEncoder(json.JSONEncoder):
    def encode(self, obj):
        def sort_lists(item):
            if isinstance(item, list):
                return sorted(sort_lists(i) for i in item)
            elif isinstance(item, dict):
                return {k: sort_lists(v) for k, v in item.items()}
            else:
                return item
        return super(SortedListEncoder, self).encode(sort_lists(obj))

class EsSystemConf:

    @staticmethod
    def hasRedFlag(nb_variants, nb_explanations, nb_all_explanations):
        if nb_variants == 0 and nb_all_explanations == 0:
            return True
        if nb_variants == 0 and nb_all_explanations >= 1:
            return False
        if nb_variants == 1:
            return False
        if nb_variants == nb_explanations:
            return False
        return True

    @staticmethod
    def find_boards_from_config(config):
        if "BR2_TARGET_BATOCERA_IMAGES" not in config:
            return []
        dirs = config["BR2_TARGET_BATOCERA_IMAGES"][1:-1].split(" ")
        boards = []
        for dir in dirs:
            boards.append(os.path.basename(dir))
        return boards

    @staticmethod
    def generate(rulesYaml, explanationsYaml, configsDir, defaultsDir):
        rules = yaml.safe_load(open(rulesYaml, "r"))
        explanations = yaml.safe_load(open(explanationsYaml, "r"))
        result_archs = {}

        systemsConfig = yaml.safe_load(open(defaultsDir + "/configgen-defaults.yml", "r"))

        for configFile in os.listdir(configsDir):
            arch = configFile.replace("config_", "")
            config = EsSystemConf.loadConfig(configsDir + "/" + configFile)
            archSystemsConfig = yaml.safe_load(open(defaultsDir + "/configgen-defaults-" + arch + ".yml", "r"))
            # case when there is no arch file
            if archSystemsConfig is None:
                archSystemsConfig = {}
            result_systems = {}
            boards = EsSystemConf.find_boards_from_config(config)
            for system in rules:
                # default emulator
                defaultEmulator = None
                if EsSystemConf.keys_exists(archSystemsConfig, system, "emulator"):
                    defaultEmulator = archSystemsConfig[system]["emulator"]
                elif EsSystemConf.keys_exists(systemsConfig, system, "emulator"):
                    defaultEmulator = systemsConfig[system]["emulator"]

                # default core
                defaultCore = None
                if EsSystemConf.keys_exists(archSystemsConfig, system, "core"):
                    defaultCore = archSystemsConfig[system]["core"]
                elif EsSystemConf.keys_exists(systemsConfig, system, "core"):
                    defaultCore = systemsConfig[system]["core"]

                emulators = EsSystemConf.listEmulators(arch, system, rules[system], explanations, config, defaultEmulator, defaultCore)
                if any(emulators["emulators"]):
                    emulators["red_flag"] = EsSystemConf.hasRedFlag(emulators["nb_variants"], emulators["nb_explanations"], emulators["nb_all_explanations"])
                    result_systems[system] = emulators
            for board in boards:
                result_archs[board] = result_systems

        print(json.dumps(result_archs, indent=2, sort_keys=True, cls=SortedListEncoder))

    # Loads the .config file
    @staticmethod
    def loadConfig(configFile):
        config = {}
        with open(configFile) as fp:
            line = fp.readline()
            while line:
                m = re.search("^([^ ]+)=[ ]*(.*)[ ]*$", line)
                if m:
                    if m.group(2) == "y":
                        config[m.group(1)] = 1
                    else:
                        config[m.group(1)] = m.group(2)
                line = fp.readline()
        return config

    # Returns the validity of prerequisites
    @staticmethod
    def isValidRequirements(config, requirements):
        if len(requirements) == 0:
            return True
        for requirement in requirements:
            if isinstance(requirement, list):
                subreq = False
                for reqitem in requirement:
                    if reqitem in config:
                        subreq = True
                if subreq:
                    return True
            else:
                if requirement in config:
                    return True
        return False

    @staticmethod
    def listEmulators(arch, system, data, explanationsYaml, config, defaultEmulator, defaultCore):
        emulators_result = {}
        nb_variants = 0
        nb_all_variants = 0
        nb_explanations = 0
        nb_all_explanations = 0

        defaultFound = False

        emulators = {}
        if "emulators" in data:
            emulators = data["emulators"]

        for emulator in sorted(emulators):
            emulatorData = data["emulators"][emulator]
            result_cores = {}
            for core in sorted(emulatorData):
                result_cores[core] = {}
                nb_all_variants += 1
                if EsSystemConf.isValidRequirements(config, emulatorData[core]["requireAnyOf"]):
                    result_cores[core]["enabled"] = True
                    nb_variants += 1
                    # tell why this core is selected
                    if EsSystemConf.keys_exists(explanationsYaml, arch, system, emulator, core, "explanation"):
                        result_cores[core]["explanation"] = explanationsYaml[arch][system][emulator][core]["explanation"]
                        nb_explanations += 1
                    elif EsSystemConf.keys_exists(explanationsYaml, "default", system, emulator, core, "explanation"):
                        result_cores[core]["explanation"] = explanationsYaml["default"][system][emulator][core]["explanation"]
                        nb_explanations += 1
                    else:
                        result_cores[core]["explanation"] = None
                    # flags - flags are cumulative
                    setFlags = []
                    if EsSystemConf.keys_exists(explanationsYaml, arch, system, emulator, core, "flags"):
                        setFlags += explanationsYaml[arch][system][emulator][core]["flags"]
                    if EsSystemConf.keys_exists(explanationsYaml, "default", system, emulator, core, "flags"):
                        setFlags += explanationsYaml["default"][system][emulator][core]["flags"]
                    result_cores[core]["flags"] = setFlags
                    # default or not
                    if emulator == defaultEmulator and core == defaultCore:
                        result_cores[core]["default"] = True
                        defaultFound = True
                    else:
                        result_cores[core]["default"] = False
                else:
                    # explanations tell why a core is not enabled too
                    result_cores[core]["enabled"] = False
                    if EsSystemConf.keys_exists(explanationsYaml, arch, system, emulator, core, "explanation"):
                        result_cores[core]["explanation"] = explanationsYaml[arch][system][emulator][core]["explanation"]
                        nb_all_explanations += 1
                    elif EsSystemConf.keys_exists(explanationsYaml, "default", system, emulator, core, "explanation"):
                        result_cores[core]["explanation"] = explanationsYaml["default"][system][emulator][core]["explanation"]
                        nb_all_explanations += 1
                    else:
                        result_cores[core]["explanation"] = None
            emulators_result[emulator] = result_cores

        if nb_variants > 0 and defaultFound == False:
            raise Exception("default core ({}/{}) not enabled for {}/{}" . format(defaultEmulator, defaultCore, arch, system))

        result = {}
        result["name"] = data["name"]
        result["nb_variants"] = nb_variants
        result["nb_all_variants"] = nb_all_variants
        result["nb_explanations"] = nb_explanations
        result["nb_all_explanations"] = nb_all_explanations
        result["emulators"] = emulators_result
        return result

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
    parser.add_argument("yml",              help="es_systems.yml definition file")
    parser.add_argument("explanationsYaml", help="explanations.yml definition file")
    parser.add_argument("defaultsDir",      help="directory containing defaults cores configs")
    parser.add_argument("configsDir",       help="directory containing config buildroot files")
    args = parser.parse_args()
    EsSystemConf.generate(args.yml, args.explanationsYaml, args.configsDir, args.defaultsDir)
