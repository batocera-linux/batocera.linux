################################################################################
#
# kodi-screensaver-pyro
#
################################################################################

KODI18_SCREENSAVER_PYRO_VERSION = 3.0.1Leia
KODI18_SCREENSAVER_PYRO_SITE = $(call github,xbmc,screensaver.pyro,$(KODI18_SCREENSAVER_PYRO_VERSION))
KODI18_SCREENSAVER_PYRO_LICENSE = GPL-2.0+
KODI18_SCREENSAVER_PYRO_LICENSE_FILES = src/Pyro.cpp
KODI18_SCREENSAVER_PYRO_DEPENDENCIES = kodi18

$(eval $(cmake-package))
