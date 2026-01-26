################################################################################
#
# libserum
#
################################################################################
# Version: Commits on Apr 13, 2026
LIBSERUM_VERSION = 55939dfe645f6a2e01785bec2cf6d723bf62def4
LIBSERUM_SITE = $(call github,ppuc,libserum,$(LIBSERUM_VERSION))
LIBSERUM_LICENSE = GPLv2+
LIBSERUM_LICENSE_FILES = LICENSE.md
LIBSERUM_DEPENDENCIES = 
LIBSERUM_SUPPORTS_IN_SOURCE_BUILD = NO
# Install to staging to build Visual Pinball Standalone
LIBSERUM_INSTALL_STAGING = YES

LIBSERUM_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBSERUM_CONF_OPTS += -DBUILD_STATIC=OFF
LIBSERUM_CONF_OPTS += -DPLATFORM=linux
LIBSERUM_CONF_OPTS += -DARCH=$(BUILD_ARCH)

# handle supported target platforms
ifeq ($(BR2_aarch64),y)
    BUILD_ARCH = aarch64
else ifeq ($(BR2_x86_64),y)
    BUILD_ARCH = x64
endif

$(eval $(cmake-package))
