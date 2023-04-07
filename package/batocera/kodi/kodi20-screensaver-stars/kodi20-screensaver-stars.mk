################################################################################
#
# kodi20-screensaver-stars
#
################################################################################

KODI20_SCREENSAVER_STARS_VERSION = 20.1.0-Nexus
KODI20_SCREENSAVER_STARS_SITE = $(call github,xbmc,screensaver.stars,$(KODI20_SCREENSAVER_STARS_VERSION))
KODI20_SCREENSAVER_STARS_LICENSE = GPL-2.0+
KODI20_SCREENSAVER_STARS_LICENSE_FILES = LICENSE.md
KODI20_SCREENSAVER_STARS_DEPENDENCIES = kodi20

KODI20_SCREENSAVER_STARS_CONF_OPTS = -DADDONS_TO_BUILD=screensaver.stars

$(eval $(cmake-package))
