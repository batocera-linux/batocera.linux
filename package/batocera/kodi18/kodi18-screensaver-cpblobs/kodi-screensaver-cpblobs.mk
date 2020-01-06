################################################################################
#
# kodi-screensaver-cpblobs
#
################################################################################

KODI18_SCREENSAVER_CPBLOBS_VERSION = e65b34fb75ac258a8563169b9c00ebf739dbc7ca
KODI18_SCREENSAVER_CPBLOBS_SITE = $(call github,xbmc,screensaver.cpblobs,$(KODI18_SCREENSAVER_CPBLOBS_VERSION))
KODI18_SCREENSAVER_CPBLOBS_LICENSE = GPL-2.0
KODI18_SCREENSAVER_CPBLOBS_LICENSE_FILES = LICENSE
KODI18_SCREENSAVER_CPBLOBS_DEPENDENCIES = kodi18 libsoil

$(eval $(cmake-package))
