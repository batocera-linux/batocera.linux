################################################################################
#
# PROSYSTEM
#
################################################################################
# Version.: Commits on Jan 24, 2021
LIBRETRO_PROSYSTEM_VERSION = 67fcad4e5f444af69477d27d8e3e990da17f1e6b
LIBRETRO_PROSYSTEM_SITE = $(call github,libretro,prosystem-libretro,$(LIBRETRO_PROSYSTEM_VERSION))
LIBRETRO_PROSYSTEM_LICENSE = GPLv2

LIBRETRO_PROSYSTEM_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_PROSYSTEM_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
        LIBRETRO_PROSYSTEM_PLATFORM = armv
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_PROSYSTEM_PLATFORM = rpi4
else ifeq ($(BR2_aarch64),y)
LIBRETRO_PROSYSTEM_PLATFORM = unix
endif

define LIBRETRO_PROSYSTEM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PROSYSTEM_PLATFORM)"
endef

define LIBRETRO_PROSYSTEM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/prosystem_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/prosystem_libretro.so
endef

$(eval $(generic-package))
