################################################################################
#
# LIBRETRO THEODORE
#
################################################################################
# Version.: Commits on May 8, 2020
LIBRETRO_THEODORE_VERSION = 837b5d16a60828491575626ceffacce574ba3ba3
LIBRETRO_THEODORE_SITE = $(call github,Zlika,theodore,$(LIBRETRO_THEODORE_VERSION))
LIBRETRO_THEODORE_LICENSE = GPLv3

LIBRETRO_THEODORE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_THEODORE_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_THEODORE_PLATFORM = classic_armv8_a35
endif

define LIBRETRO_THEODORE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_THEODORE_PLATFORM)"
endef

define LIBRETRO_THEODORE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/theodore_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/theodore_libretro.so
endef

$(eval $(generic-package))
