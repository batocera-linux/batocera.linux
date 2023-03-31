################################################################################
#
# kodi20-screensaver-matrixtrails
#
################################################################################

KODI20_SCREENSAVER_MATRIXTRAILS_VERSION = 20.1.0-Nexus
KODI20_SCREENSAVER_MATRIXTRAILS_SITE = $(call github,xbmc,screensaver.matrixtrails,$(KODI20_SCREENSAVER_MATRIXTRAILS_VERSION))
KODI20_SCREENSAVER_MATRIXTRAILS_LICENSE = GPL-2.0+
KODI20_SCREENSAVER_MATRIXTRAILS_LICENSE_FILES = LICENSE.md
KODI20_SCREENSAVER_MATRIXTRAILS_DEPENDENCIES = kodi20

KODI20_SCREENSAVER_MATRIXTRAILS_CONF_OPTS += \
	-DCMAKE_C_FLAGS="$(TARGET_CFLAGS) `$(PKG_CONFIG_HOST_BINARY) --cflags egl`" \
	-DCMAKE_CXX_FLAGS="$(TARGET_CXXFLAGS) `$(PKG_CONFIG_HOST_BINARY) --cflags egl`"

$(eval $(cmake-package))
