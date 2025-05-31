################################################################################
#
# libpinmame
#
################################################################################
# Version: Commits on May 31, 2025
LIBPINMAME_VERSION = e92f9e25bc666e09b791a32712269e1096c88445
LIBPINMAME_SITE = $(call github,vpinball,pinmame,$(LIBPINMAME_VERSION))
LIBPINMAME_LICENSE = BSD-3-Clause
LIBPINMAME_LICENSE_FILES = LICENSE
LIBPINMAME_DEPENDENCIES = zlib
LIBPINMAME_SUPPORTS_IN_SOURCE_BUILD = NO
# Install to staging to build Visual Pinball Standalone
LIBPINMAME_INSTALL_STAGING = YES

LIBPINMAME_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBPINMAME_CONF_OPTS += -DBUILD_STATIC=OFF
LIBPINMAME_CONF_OPTS += -DPLATFORM=linux
LIBPINMAME_CONF_OPTS += -DARCH=$(BUILD_ARCH)

define LIBPINMAME_RENAME_CMAKE
    cp $(@D)/cmake/libpinmame/CMakeLists.txt $(@D)
    rm $(@D)/makefile
endef

# handle supported target platforms
ifeq ($(BR2_aarch64),y)
    BUILD_ARCH = aarch64
else ifeq ($(BR2_x86_64),y)
    BUILD_ARCH = x64
endif

LIBPINMAME_PRE_CONFIGURE_HOOKS += LIBPINMAME_RENAME_CMAKE

$(eval $(cmake-package))
