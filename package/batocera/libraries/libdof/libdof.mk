################################################################################
#
# libdof
#
################################################################################
# Version: Commits on May 27, 2025
LIBDOF_VERSION = 6a5c15c3f16d76e77bc2bc8b3abcb1c1f8856d23
LIBDOF_SITE = $(call github,jsm174,libdof,$(LIBDOF_VERSION))
LIBDOF_LICENSE = BSD-3-Clause
LIBDOF_LICENSE_FILES = LICENSE
LIBDOF_DEPENDENCIES = libserialport hidapi sockpp cargs
LIBDOF_SUPPORTS_IN_SOURCE_BUILD = NO
# Install to staging to build Visual Pinball Standalone
LIBDOF_INSTALL_STAGING = YES

LIBDOF_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBDOF_CONF_OPTS += -DBUILD_STATIC=OFF
LIBDOF_CONF_OPTS += -DPLATFORM=linux
LIBDOF_CONF_OPTS += -DARCH=$(BUILD_ARCH)
LIBDOF_CONF_OPTS += -DPOST_BUILD_COPY_EXT_LIBS=OFF

# handle supported target platforms
ifeq ($(BR2_aarch64),y)
    BUILD_ARCH = aarch64
else ifeq ($(BR2_x86_64),y)
    BUILD_ARCH = x64
endif

$(eval $(cmake-package))
