################################################################################
#
# libpupdmd
#
################################################################################
# Version: Commits on Mar 30, 2024
LIBPUPDMD_VERSION = 332fc4aab2639a1b159545375df15e405cb2c82c
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
ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RK3588),y)
    BUILD_ARCH = aarch64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711)$(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
    BUILD_ARCH = aarch64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_X86_64_ANY),y)
    BUILD_ARCH = x64
endif

define LIBPUPDMD_CMAKE_HACKS
   ## derived from platforms/${PLATFORM}/${BUILD_ARCH}/external.sh and CMakeLists.txt ##
   $(SED) 's:third-party/include$$:$(STAGING_DIR)/usr/include/\n   third-party/include:g' $(@D)/CMakeLists.txt
   $(SED) 's:$${CMAKE_SOURCE_DIR}/third-party/runtime-libs/$${PLATFORM}/$${ARCH}/:$(STAGING_DIR)/usr/lib/:g' $(@D)/CMakeLists.txt
   $(SED) 's:third-party/runtime-libs/$${PLATFORM}/$${ARCH}:$(STAGING_DIR)/usr/lib/:g' $(@D)/CMakeLists.txt
endef

# Install to staging to build Visual Pinball Standalone
LIBPUPDMD_INSTALL_STAGING = YES

LIBPUPDMD_PRE_CONFIGURE_HOOKS += LIBPUPDMD_CMAKE_HACKS

$(eval $(cmake-package))
