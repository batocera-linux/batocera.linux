################################################################################
#
# kodi-screensaver-asteroids
#
################################################################################

KODI18_SCREENSAVER_ASTEROIDS_VERSION = 2.3.2-Leia
KODI18_SCREENSAVER_ASTEROIDS_SITE = $(call github,xbmc,screensaver.asteroids,$(KODI18_SCREENSAVER_ASTEROIDS_VERSION))
KODI18_SCREENSAVER_ASTEROIDS_LICENSE = GPL-2.0+
KODI18_SCREENSAVER_ASTEROIDS_LICENSE_FILES = debian/copyright
KODI18_SCREENSAVER_ASTEROIDS_DEPENDENCIES = glm kodi18

$(eval $(cmake-package))
