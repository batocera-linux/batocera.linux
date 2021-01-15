################################################################################
#
# PROSYSTEM
#
################################################################################
# Version.: Commits on Nov 17, 2020
LIBRETRO_PROSYSTEM_VERSION = c0f59a19a163cc5f18121ce48c25f2f58de223df
LIBRETRO_PROSYSTEM_SITE = $(call github,libretro,prosystem-libretro,$(LIBRETRO_PROSYSTEM_VERSION))
LIBRETRO_PROSYSTEM_LICENSE = GPLv2

LIBRETRO_PROSYSTEM_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_PROSYSTEM_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
	LIBRETRO_PROSYSTEM_PLATFORM = rpi4
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_PROSYSTEM_PLATFORM = classic_armv8_a35
endif

define LIBRETRO_PROSYSTEM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PROSYSTEM_PLATFORM)"
endef

define LIBRETRO_PROSYSTEM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/prosystem_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/prosystem_libretro.so
endef

$(eval $(generic-package))
