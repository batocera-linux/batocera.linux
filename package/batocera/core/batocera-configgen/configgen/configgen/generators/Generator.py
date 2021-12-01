from abc import ABCMeta, abstractmethod


class Generator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def generate(self, system, rom, playersControllers, gameResolution):
        pass

    def getResolutionMode(self, config):
        return config['videomode']

    def getMouseMode(self, config):
        return False

    def executionDirectory(self, config, rom):
        return None

    def supportsInternalBezels(self):
        return False

    def getInGameRatio(self, config, gameResolution):
        # put a default value, but it should be overriden by generators
        return 4/3
