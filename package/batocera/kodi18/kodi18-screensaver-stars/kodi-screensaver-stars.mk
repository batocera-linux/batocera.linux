################################################################################
#
# kodi-screensaver-stars
#
################################################################################

KODI18_SCREENSAVER_STARS_VERSION = 2.1.4-Leia
KODI18_SCREENSAVER_STARS_SITE = $(call github,xbmc,screensaver.stars,$(KODI18_SCREENSAVER_STARS_VERSION))
KODI18_SCREENSAVER_STARS_LICENSE = GPL-2.0+
KODI18_SCREENSAVER_STARS_LICENSE_FILES = LICENSE.md
KODI18_SCREENSAVER_STARS_DEPENDENCIES = kodi18

$(eval $(cmake-package))
