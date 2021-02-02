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
