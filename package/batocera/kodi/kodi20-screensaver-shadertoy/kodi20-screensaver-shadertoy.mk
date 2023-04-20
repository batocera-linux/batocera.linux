################################################################################
#
# kodi20-screensaver-shadertoy
#
################################################################################

KODI20_SCREENSAVER_SHADERTOY_VERSION = 20.1.0-Nexus
KODI20_SCREENSAVER_SHADERTOY_SITE = $(call github,xbmc,screensaver.shadertoy,$(KODI20_SCREENSAVER_SHADERTOY_VERSION))
KODI20_SCREENSAVER_SHADERTOY_LICENSE = GPL-2.0+
KODI20_SCREENSAVER_SHADERTOY_LICENSE_FILES = LICENSE.md
KODI20_SCREENSAVER_SHADERTOY_DEPENDENCIES = kodi20

KODI20_SCREENSAVER_SHADERTOY_CONF_OPTS = -DADDONS_TO_BUILD=screensaver.shadertoy

$(eval $(cmake-package))
