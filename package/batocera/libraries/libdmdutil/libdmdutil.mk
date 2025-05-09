################################################################################
#
# libdmdutil
#
################################################################################
# Version: Commits on May 7, 2025
LIBDMDUTIL_VERSION = bb4e0ae9a2313373423b3f675ec5f8a3fc915a16
LIBDMDUTIL_SITE = $(call github,vpinball,libdmdutil,$(LIBDMDUTIL_VERSION))
LIBDMDUTIL_LICENSE = BSD-3-Clause
LIBDMDUTIL_LICENSE_FILES = LICENSE
LIBDMDUTIL_DEPENDENCIES = libserialport sockpp cargs libzedmd libserum libpupdmd
LIBDMDUTIL_SUPPORTS_IN_SOURCE_BUILD = NO
# Install to staging to build Visual Pinball Standalone
LIBDMDUTIL_INSTALL_STAGING = YES

LIBDMDUTIL_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBDMDUTIL_CONF_OPTS += -DBUILD_STATIC=OFF
LIBDMDUTIL_CONF_OPTS += -DPLATFORM=linux
LIBDMDUTIL_CONF_OPTS += -DARCH=$(BUILD_ARCH)
LIBDMDUTIL_CONF_OPTS += -DPOST_BUILD_COPY_EXT_LIBS=OFF

# handle supported target platforms
ifeq ($(BR2_aarch64),y)
    BUILD_ARCH = aarch64
else ifeq ($(BR2_x86_64),y)
    BUILD_ARCH = x64
endif

define LIBDMDUTIL_INSTALL_SERVER
   $(INSTALL) -D -m 0755 $(LIBDMDUTIL_BUILDDIR)/dmdserver \
       $(TARGET_DIR)/usr/bin/dmdserver

   mkdir -p $(TARGET_DIR)/usr/share/batocera/services
   install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/libraries/libdmdutil/dmd_server.service \
       $(TARGET_DIR)/usr/share/batocera/services/dmd_real
   install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/libraries/libdmdutil/dmdserver-config.py \
       $(TARGET_DIR)/usr/bin/dmdserver-config
   # pixelcade
   install -m 0644 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/libraries/libdmdutil/99-pixelcade.rules \
       $(TARGET_DIR)/etc/udev/rules.d/99-pixelcade.rules
   $(INSTALL) -m 0755 -D $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/libraries/libdmdutil/pixelcade-add \
       $(TARGET_DIR)/usr/bin/pixelcade-add
endef

LIBDMDUTIL_POST_INSTALL_TARGET_HOOKS += LIBDMDUTIL_INSTALL_SERVER

$(eval $(cmake-package))
