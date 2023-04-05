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

KODI20_SCREENSAVER_PYRO_CONF_OPTS = -DADDONS_TO_BUILD=screensaver.pyro

$(eval $(cmake-package))
