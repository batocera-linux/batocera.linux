################################################################################
#
# kodi20-screensaver-cpblobs
#
################################################################################

KODI20_SCREENSAVER_CPBLOBS_VERSION = 20.1.0-Nexus
KODI20_SCREENSAVER_CPBLOBS_SITE = $(call github,xbmc,screensaver.cpblobs,$(KODI20_SCREENSAVER_CPBLOBS_VERSION))
KODI20_SCREENSAVER_CPBLOBS_LICENSE = GPL-2.0
KODI20_SCREENSAVER_CPBLOBS_LICENSE_FILES = LICENSE.md
KODI20_SCREENSAVER_CPBLOBS_DEPENDENCIES = glm kodi20

KODI20_SCREENSAVER_CPBLOBS_CONF_OPTS += \
	-DCMAKE_C_FLAGS="$(TARGET_CFLAGS) `$(PKG_CONFIG_HOST_BINARY) --cflags egl`" \
	-DCMAKE_CXX_FLAGS="$(TARGET_CXXFLAGS) `$(PKG_CONFIG_HOST_BINARY) --cflags egl`"

$(eval $(cmake-package))
