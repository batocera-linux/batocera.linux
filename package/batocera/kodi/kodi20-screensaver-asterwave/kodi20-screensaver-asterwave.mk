################################################################################
#
# kodi20-screensaver-asterwave
#
################################################################################

KODI20_SCREENSAVER_ASTERWAVE_VERSION = 20.1.0-Nexus
KODI20_SCREENSAVER_ASTERWAVE_SITE = $(call github,xbmc,screensaver.asterwave,$(KODI20_SCREENSAVER_ASTERWAVE_VERSION))
KODI20_SCREENSAVER_ASTERWAVE_LICENSE = GPL-2.0+
KODI20_SCREENSAVER_ASTERWAVE_LICENSE_FILES = LICENSE.md
KODI20_SCREENSAVER_ASTERWAVE_DEPENDENCIES = glm kodi20

KODI20_SCREENSAVER_ASTERWAVE_CONF_OPTS += \
    -DADDONS_TO_BUILD=screensaver.asterwave \
	-DCMAKE_C_FLAGS="$(TARGET_CFLAGS) `$(PKG_CONFIG_HOST_BINARY) --cflags egl`" \
	-DCMAKE_CXX_FLAGS="$(TARGET_CXXFLAGS) `$(PKG_CONFIG_HOST_BINARY) --cflags egl`"

$(eval $(cmake-package))
