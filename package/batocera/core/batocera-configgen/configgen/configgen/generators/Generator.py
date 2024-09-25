from abc import ABCMeta, abstractmethod


class Generator(metaclass=ABCMeta):
    @abstractmethod
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
        pass

    def getResolutionMode(self, config):
        return config['videomode']

    def getMouseMode(self, config, rom):
        return False

    def executionDirectory(self, config, rom):
        return None

    # mame or libretro have internal bezels, don't display the one of mangohud
    def supportsInternalBezels(self):
        return False

    # mangohud must be called by the generator itself (wine based emulator for example)
    def hasInternalMangoHUDCall(self):
        return False

    def getInGameRatio(self, config, gameResolution, rom):
        # put a default value, but it should be overriden by generators
        return 4/3

    def getHotkeysContext(self):
        return {
            "name": "configgen",
            "keys": {}
        }
