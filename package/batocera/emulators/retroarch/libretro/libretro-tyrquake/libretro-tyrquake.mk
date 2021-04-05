################################################################################
#
# TYRQUAKE - Quake 1 Engine
#
################################################################################
# Version.: Commits on Mar 25, 2020
LIBRETRO_TYRQUAKE_VERSION = 8dc6d35c1ff0ccc5a0b5c56afee57ef8a094f2d3
LIBRETRO_TYRQUAKE_SITE = $(call github,libretro,tyrquake,$(LIBRETRO_TYRQUAKE_VERSION))
LIBRETRO_TYRQUAKE_LICENSE = GPLv2

LIBRETRO_TYRQUAKE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
	LIBRETRO_TYRQUAKE_PLATFORM = armv
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_TYRQUAKE_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_TYRQUAKE_PLATFORM = rpi4_64
else ifeq ($(BR2_aarch64),y)
LIBRETRO_TYRQUAKE_PLATFORM = unix
endif

define LIBRETRO_TYRQUAKE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_TYRQUAKE_PLATFORM)"
endef

define LIBRETRO_TYRQUAKE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/tyrquake_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/tyrquake_libretro.so
endef

$(eval $(generic-package))
