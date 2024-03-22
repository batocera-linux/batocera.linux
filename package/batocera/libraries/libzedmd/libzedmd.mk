################################################################################
#
# libzedmd
#
################################################################################
# Version: Commits on Feb 28, 2024
LIBZEDMD_VERSION = 42d95ed6f1fe2065ecbd247502d177d7e5eb7e4c
LIBZEDMD_SITE = $(call github,PPUC,libzedmd,$(LIBZEDMD_VERSION))
LIBZEDMD_LICENSE = GPLv3
LIBZEDMD_LICENSE_FILES = LICENSE
LIBZEDMD_DEPENDENCIES = libserialport
LIBZEDMD_SUPPORTS_IN_SOURCE_BUILD = NO

LIBZEDMD_CONF_OPTS += -DCMAKE_BUILD_TYPE=Release
LIBZEDMD_CONF_OPTS += -DBUILD_STATIC=OFF
LIBZEDMD_CONF_OPTS += -DPLATFORM=linux
LIBZEDMD_CONF_OPTS += -DARCH=$(BUILD_ARCH)

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

define LIBZEDMD_CMAKE_HACKS
   ## derived from platforms/${PLATFORM}/${BUILD_ARCH}/external.sh and CMakeLists.txt ##
   $(SED) 's:third-party/include$$:$(STAGING_DIR)/usr/include/\n   third-party/include:g' $(@D)/CMakeLists.txt
   $(SED) 's:$${CMAKE_SOURCE_DIR}/third-party/runtime-libs/$${PLATFORM}/$${ARCH}/:$(STAGING_DIR)/usr/lib/:g' $(@D)/CMakeLists.txt
   $(SED) 's:third-party/runtime-libs/$${PLATFORM}/$${ARCH}:$(STAGING_DIR)/usr/lib/:g' $(@D)/CMakeLists.txt
endef

# Install to staging to build Visual Pinball Standalone
LIBZEDMD_INSTALL_STAGING = YES

LIBZEDMD_PRE_CONFIGURE_HOOKS += LIBZEDMD_CMAKE_HACKS

$(eval $(cmake-package))
