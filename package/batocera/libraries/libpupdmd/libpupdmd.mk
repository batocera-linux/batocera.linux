################################################################################
#
# libpupdmd
#
################################################################################
# Version: Commits on May 8, 2026
LIBPUPDMD_VERSION = 4a1123220e6dce73c87cc584494df2ac82cb6f4c
LIBPUPDMD_SITE = $(call github,ppuc,LIBPUPDMD,$(LIBPUPDMD_VERSION))
LIBPUPDMD_LICENSE = GPL-3.0 license
LIBPUPDMD_LICENSE_FILES = LICENSE
LIBPUPDMD_DEPENDENCIES = 
LIBPUPDMD_SUPPORTS_IN_SOURCE_BUILD = NO

LIBPUPDMD_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBPUPDMD_CONF_OPTS += -DBUILD_STATIC=OFF
LIBPUPDMD_CONF_OPTS += -DPLATFORM=linux
LIBPUPDMD_CONF_OPTS += -DARCH=$(BUILD_ARCH)
LIBPUPDMD_CONF_OPTS += -DPOST_BUILD_COPY_EXT_LIBS=OFF

# handle supported target platforms
ifeq ($(BR2_aarch64),y)
    BUILD_ARCH = aarch64
else ifeq ($(BR2_x86_64),y)
    BUILD_ARCH = x64
endif

# Install to staging to build Visual Pinball Standalone
LIBPUPDMD_INSTALL_STAGING = YES

$(eval $(cmake-package))
