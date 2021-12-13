################################################################################
#
# NXENGINE
#
################################################################################
# Version.: Commits on Nov 16, 2021
LIBRETRO_NXENGINE_VERSION = 4e2ea9ffe86bb7a0605677636b68431d470b4572
LIBRETRO_NXENGINE_SITE = $(call github,libretro,nxengine-libretro,$(LIBRETRO_NXENGINE_VERSION))
LIBRETRO_NXENGINE_LICENSE = GPLv3

LIBRETRO_NXENGINE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_NXENGINE_PLATFORM = armv

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_NXENGINE_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_NXENGINE_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    ifeq ($(BR2_arm),y)
        LIBRETRO_NXENGINE_PLATFORM = rpi3
    else
        LIBRETRO_NXENGINE_PLATFORM = rpi3_64
    endif

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_NXENGINE_PLATFORM = rpi4_64

else ifeq ($(BR2_aarch64),y)
LIBRETRO_NXENGINE_PLATFORM = unix
endif

define LIBRETRO_NXENGINE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_NXENGINE_PLATFORM)"
endef

define LIBRETRO_NXENGINE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/nxengine_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/nxengine_libretro.so
endef

$(eval $(generic-package))
