################################################################################
#
# kodi20-screensaver-asteroids
#
################################################################################

KODI20_SCREENSAVER_ASTEROIDS_VERSION = 20.1.0-Nexus
KODI20_SCREENSAVER_ASTEROIDS_SITE = $(call github,xbmc,screensaver.asteroids,$(KODI20_SCREENSAVER_ASTEROIDS_VERSION))
KODI20_SCREENSAVER_ASTEROIDS_LICENSE = GPL-2.0+
KODI20_SCREENSAVER_ASTEROIDS_LICENSE_FILES = LICENSE.md
KODI20_SCREENSAVER_ASTEROIDS_DEPENDENCIES = glm kodi20
KODI20_SCREENSAVER_ASTEROIDS_CONF_OPTS = -DADDONS_TO_BUILD=screensaver.asteroids

$(eval $(cmake-package))
