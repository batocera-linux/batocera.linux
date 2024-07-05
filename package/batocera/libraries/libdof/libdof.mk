################################################################################
#
# libdof
#
################################################################################
# Version: Commits on Jul 2, 2024
LIBDOF_VERSION = 42160a6835ead9d64f101e687dc277a0fe766f25
LIBDOF_SITE = $(call github,jsm174,libdof,$(LIBDOF_VERSION))
LIBDOF_LICENSE = BSD-3-Clause
LIBDOF_LICENSE_FILES = LICENSE
LIBDOF_DEPENDENCIES = libserialport hidapi sockpp cargs
LIBDOF_SUPPORTS_IN_SOURCE_BUILD = NO

LIBDOF_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBDOF_CONF_OPTS += -DBUILD_STATIC=OFF
LIBDOF_CONF_OPTS += -DPLATFORM=linux
LIBDOF_CONF_OPTS += -DARCH=$(BUILD_ARCH)
LIBDOF_CONF_OPTS += -DPOST_BUILD_COPY_EXT_LIBS=OFF

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
LIBDOF_INSTALL_STAGING = YES

$(eval $(cmake-package))
