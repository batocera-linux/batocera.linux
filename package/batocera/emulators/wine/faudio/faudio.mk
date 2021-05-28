################################################################################
#
# Faudio
#
################################################################################

FAUDIO_VERSION = 21.05
FAUDIO_SITE = $(call github,FNA-XNA,FAudio,$(FAUDIO_VERSION))

FAUDIO_LICENSE = ZLIB
FAUDIO_LICENSE_FILES = LICENSE
FAUDIO_DEPENDENCIES = host-bison host-flex host-wine-lutris host-libtool gstreamer1 gst1-plugins-base

FAUDIO_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
FAUDIO_CONF_OPTS += -DSDL2_INCLUDE_DIRS=$(STAGING_DIR)/usr/include/SDL2
FAUDIO_CONF_OPTS += -DSDL2_LIBRARIES=$(STAGING_DIR)/usr/lib/libSDL2.so
FAUDIO_CONF_OPTS += -DGSTREAMER=ON

# Should be set when the package cannot be built inside the source tree but needs a separate build directory.
FAUDIO_SUPPORTS_IN_SOURCE_BUILD = NO

# Install to staging to build wine with Faudio support
FAUDIO_INSTALL_STAGING = YES

$(eval $(cmake-package))
