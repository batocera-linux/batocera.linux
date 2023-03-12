################################################################################
#
# kodi20-screensaver-pyro
#
################################################################################

KODI20_SCREENSAVER_PYRO_VERSION = 20.1.0-Nexus
KODI20_SCREENSAVER_PYRO_SITE = $(call github,xbmc,screensaver.pyro,$(KODI20_SCREENSAVER_PYRO_VERSION))
KODI20_SCREENSAVER_PYRO_LICENSE = GPL-2.0+
KODI20_SCREENSAVER_PYRO_LICENSE_FILES = LICENSE.md
KODI20_SCREENSAVER_PYRO_DEPENDENCIES = kodi20

$(eval $(cmake-package))
