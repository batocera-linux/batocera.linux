#!/usr/bin/env python

from distutils.core import setup
setup(name='batocera-configgen',
      version='1.0',
      py_modules=['configgen'],
      packages=['configgen', 
        'configgen.generators', 
        'configgen.generators.kodi', 
        'configgen.generators.libretro', 
        'configgen.generators.linapple', 
        'configgen.generators.moonlight', 
        'configgen.generators.mupen', 
        'configgen.generators.scummvm', 
        'configgen.generators.dosbox',
        'configgen.generators.vice',
        'configgen.generators.fsuae',
        'configgen.generators.amiberry',
        'configgen.generators.ppsspp',
        'configgen.generators.reicast',
        'configgen.generators.dolphin',
        'configgen.generators.pcsx2',
        'configgen.generators.citra',
        'configgen.generators.daphne',
        'configgen.settings',
        'configgen.utils']
      )
