################################################################################
#
# kodi-screensaver-cpblobs
#
################################################################################

KODI18_SCREENSAVER_CPBLOBS_VERSION = 3.0.4-Leia
KODI18_SCREENSAVER_CPBLOBS_SITE = $(call github,xbmc,screensaver.cpblobs,$(KODI18_SCREENSAVER_CPBLOBS_VERSION))
KODI18_SCREENSAVER_CPBLOBS_LICENSE = GPL-2.0
KODI18_SCREENSAVER_CPBLOBS_LICENSE_FILES = LICENSE
KODI18_SCREENSAVER_CPBLOBS_DEPENDENCIES = kodi18 libsoil

$(eval $(cmake-package))
