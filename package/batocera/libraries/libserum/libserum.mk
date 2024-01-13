################################################################################
#
# libserum
#
################################################################################
# Version: Commits on Jan 8, 2024
LIBSERUM_VERSION = b69d2b436bc93570a2e7e78d0946cd3c43f7aed5
LIBSERUM_SITE = $(call github,zesinger,libserum,$(LIBSERUM_VERSION))
LIBSERUM_LICENSE = GPLv2+
LIBSERUM_LICENSE_FILES = LICENSE.md
LIBSERUM_DEPENDENCIES = 
LIBSERUM_SUPPORTS_IN_SOURCE_BUILD = NO

LIBSERUM_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBSERUM_CONF_OPTS += -DBUILD_STATIC=OFF
LIBSERUM_CONF_OPTS += -DPLATFORM=linux
LIBSERUM_CONF_OPTS += -DARCH=$(BUILD_ARCH)

# handle supported target platforms
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
    BUILD_ARCH = aarch64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
    BUILD_ARCH = aarch64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    BUILD_ARCH = x64
endif

# Install to staging to build Visual Pinball Standalone
LIBSERUM_INSTALL_STAGING = YES

$(eval $(cmake-package))
