################################################################################
#
# libzedmd
#
################################################################################
# Version: Commits on Jun 10, 2026
LIBZEDMD_VERSION = 5c44646f2af4b1419b4cdcaed3a2799ca9439221
LIBZEDMD_SITE = $(call github,PPUC,libzedmd,$(LIBZEDMD_VERSION))
LIBZEDMD_LICENSE = GPLv3
LIBZEDMD_LICENSE_FILES = LICENSE
LIBZEDMD_DEPENDENCIES = cargs libserialport sockpp libframeutil
LIBZEDMD_SUPPORTS_IN_SOURCE_BUILD = NO
# Install to staging to build Visual Pinball Standalone
LIBZEDMD_INSTALL_STAGING = YES

LIBZEDMD_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBZEDMD_CONF_OPTS += -DBUILD_STATIC=OFF
LIBZEDMD_CONF_OPTS += -DPLATFORM=linux
LIBZEDMD_CONF_OPTS += -DARCH=$(BUILD_ARCH)
LIBZEDMD_CONF_OPTS += -DPOST_BUILD_COPY_EXT_LIBS=OFF

# handle supported target platforms
ifeq ($(BR2_aarch64),y)
BUILD_ARCH = aarch64
ifeq ($(BR2_PACKAGE_LIBGPIOD2),y)
LIBZEDMD_DEPENDENCIES += libgpiod2
else ifeq ($(BR2_PACKAGE_LIBGPIOD),y)
LIBZEDMD_DEPENDENCIES += libgpiod
endif
else ifeq ($(BR2_x86_64),y)
BUILD_ARCH = x64
endif

define LIBZEDMD_POST_PROCESS
	mkdir -p $(TARGET_DIR)/usr/bin
	$(INSTALL) -m 755 $(@D)/buildroot-build/zedmd-client \
        $(TARGET_DIR)/usr/bin/zedmd-client
endef

LIBZEDMD_POST_INSTALL_TARGET_HOOKS += LIBZEDMD_POST_PROCESS

$(eval $(cmake-package))
