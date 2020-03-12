################################################################################
#
# kodi-screensaver-asterwave
#
################################################################################

KODI18_SCREENSAVER_ASTERWAVE_VERSION = 3.0.4-Leia
KODI18_SCREENSAVER_ASTERWAVE_SITE = $(call github,xbmc,screensaver.asterwave,$(KODI18_SCREENSAVER_ASTERWAVE_VERSION))
KODI18_SCREENSAVER_ASTERWAVE_DEPENDENCIES = kodi18 libglu libsoil

$(eval $(cmake-package))
