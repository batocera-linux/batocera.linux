################################################################################
#
# faudio
#
################################################################################

FAUDIO_VERSION = 24.11
FAUDIO_SITE = $(call github,FNA-XNA,FAudio,$(FAUDIO_VERSION))
FAUDIO_LICENSE = ZLIB
FAUDIO_LICENSE_FILES = LICENSE
FAUDIO_SUPPORTS_IN_SOURCE_BUILD = NO
FAUDIO_INSTALL_STAGING = YES

FAUDIO_DEPENDENCIES = host-bison host-flex host-libtool gstreamer1 gst1-plugins-base

ifeq ($(BR2_PACKAGE_WINE_TKG),y)
FAUDIO_DEPENDENCIES += host-wine-tkg
endif

FAUDIO_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
FAUDIO_CONF_OPTS += -DSDL2_INCLUDE_DIRS=$(STAGING_DIR)/usr/include/SDL2
FAUDIO_CONF_OPTS += -DSDL2_LIBRARIES=$(STAGING_DIR)/usr/lib/libSDL2.so
FAUDIO_CONF_OPTS += -DGSTREAMER=ON

$(eval $(cmake-package))
