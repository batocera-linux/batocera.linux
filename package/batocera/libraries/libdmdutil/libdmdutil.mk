################################################################################
#
# libdmdutil
#
################################################################################
# Version: Commits on Mar 11, 2024
LIBDMDUTIL_VERSION = 188e3e71bc2b323dddf6f0fb2a1d757593477e6f
LIBDMDUTIL_SITE = $(call github,vpinball,libdmdutil,$(LIBDMDUTIL_VERSION))
LIBDMDUTIL_LICENSE = BSD-3-Clause
LIBDMDUTIL_LICENSE_FILES = LICENSE
LIBDMDUTIL_DEPENDENCIES = libserialport sockpp cargs libzedmd libserum
LIBDMDUTIL_SUPPORTS_IN_SOURCE_BUILD = NO

LIBDMDUTIL_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBDMDUTIL_CONF_OPTS += -DBUILD_STATIC=OFF
LIBDMDUTIL_CONF_OPTS += -DPLATFORM=linux
LIBDMDUTIL_CONF_OPTS += -DARCH=$(BUILD_ARCH)
LIBDMDUTIL_CONF_OPTS += -DPOST_BUILD_COPY_EXT_LIBS=OFF

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

define LIBDMDUTIL_CMAKE_HACKS
   ## derived from platforms/${PLATFORM}/${BUILD_ARCH}/external.sh and CMakeLists.txt ##
   $(SED) 's:third-party/include$$:$(STAGING_DIR)/usr/include/\n   third-party/include:g' $(@D)/CMakeLists.txt
   $(SED) 's:$${CMAKE_SOURCE_DIR}/third-party/runtime-libs/$${PLATFORM}/$${ARCH}/:$(STAGING_DIR)/usr/lib/:g' $(@D)/CMakeLists.txt
   $(SED) 's:third-party/runtime-libs/$${PLATFORM}/$${ARCH}:$(STAGING_DIR)/usr/lib/:g' $(@D)/CMakeLists.txt
endef

# Install to staging to build Visual Pinball Standalone
LIBDMDUTIL_INSTALL_STAGING = YES

LIBDMDUTIL_PRE_CONFIGURE_HOOKS += LIBDMDUTIL_CMAKE_HACKS

define LIBDMDUTIL_INSTALL_SERVER
   $(INSTALL) -D -m 0755 $(LIBDMDUTIL_BUILDDIR)/dmdserver $(TARGET_DIR)/usr/bin/dmdserver

   mkdir -p $(TARGET_DIR)/usr/share/batocera/services
   install -m 0755 $(BR2_EXTERNAL_BATOCERA_PATH)/package/batocera/libraries/libdmdutil/dmd_server.service $(TARGET_DIR)/usr/share/batocera/services/dmd_real
endef

LIBDMDUTIL_POST_INSTALL_TARGET_HOOKS += LIBDMDUTIL_INSTALL_SERVER

$(eval $(cmake-package))
