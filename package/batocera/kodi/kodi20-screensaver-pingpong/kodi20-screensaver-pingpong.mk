################################################################################
#
# kodi20-screensaver-pingpong
#
################################################################################

KODI20_SCREENSAVER_PINGPONG_VERSION = 20.1.0-Nexus
KODI20_SCREENSAVER_PINGPONG_SITE = $(call github,xbmc,screensaver.pingpong,$(KODI20_SCREENSAVER_PINGPONG_VERSION))
KODI20_SCREENSAVER_PINGPONG_LICENSE = GPL-2.0+
KODI20_SCREENSAVER_PINGPONG_LICENSE_FILES = LICENSE.md
KODI20_SCREENSAVER_PINGPONG_DEPENDENCIES = glm kodi20

KODI20_SCREENSAVER_PINGPONG_CONF_OPTS = -DADDONS_TO_BUILD=screensaver.pingpong

$(eval $(cmake-package))
