################################################################################
#
# kodi20-screensaver-greynetic
#
################################################################################

KODI20_SCREENSAVER_GREYNETIC_VERSION = 20.1.0-Nexus
KODI20_SCREENSAVER_GREYNETIC_SITE = $(call github,xbmc,screensaver.greynetic,$(KODI20_SCREENSAVER_GREYNETIC_VERSION))
KODI20_SCREENSAVER_GREYNETIC_LICENSE = GPL-2.0+
KODI20_SCREENSAVER_GREYNETIC_LICENSE_FILES = LICENSE.md
KODI20_SCREENSAVER_GREYNETIC_DEPENDENCIES = glm kodi20

KODI20_SCREENSAVER_GREYNETIC_CONF_OPTS = -DADDONS_TO_BUILD=screensaver.greynetic

$(eval $(cmake-package))
