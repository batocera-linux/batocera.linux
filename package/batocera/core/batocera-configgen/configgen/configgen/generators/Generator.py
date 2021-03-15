#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod


class Generator(object, metaclass=ABCMeta):
    @abstractmethod
    def generate(self, system, rom, playersControllers, gameResolution):
        pass

    def getResolutionMode(self, config):
        return config['videomode']

    def getMouseMode(self, config):
        return False
