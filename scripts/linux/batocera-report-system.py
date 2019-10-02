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
    def generate(rulesYaml, configsDir):
        #rules = yaml.load(open(rulesYaml, "r"), Loader=yaml.FullLoader)
        rules = yaml.load(open(rulesYaml, "r"))
        result_archs = {}

        for configFile in os.listdir(configsDir):
            archName = configFile.replace("config_", "")
            config = EsSystemConf.loadConfig(configsDir + "/" + configFile)
            result_systems = {}
            for system in rules:
                emulators = EsSystemConf.listEmulators(rules[system], config)
                if any(emulators["emulators"]):
                    emulators["red_flag"] = emulators["nb_variants"] > 1
                    result_systems[system] = emulators
            result_archs[archName] = result_systems

        print(json.dumps(result_archs, indent=2, sort_keys=True, cls=SortedListEncoder))

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

    @staticmethod
    def listEmulators(data, config):
        emulators_result = {}
        nb_variants = 0
        
        emulators = {}
        if "emulators" in data:
            emulators = data["emulators"]

        for emulator in sorted(emulators):
            emulatorData = data["emulators"][emulator]
            result_cores = []
            for core in sorted(emulatorData):
                if EsSystemConf.isValidRequirements(config, emulatorData[core]["requireAnyOf"]):
                    result_cores.append(core)
                    nb_variants += 1
            emulators_result[emulator] = result_cores

        result = {}
        result["name"] = data["name"]
        result["nb_variants"] = nb_variants
        result["emulators"] = emulators_result
        return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("yml",        help="es_systems.yml definition file")
    parser.add_argument("configs",     help="directory containing config buildroot files")
    args = parser.parse_args()
    EsSystemConf.generate(args.yml, args.configs)
