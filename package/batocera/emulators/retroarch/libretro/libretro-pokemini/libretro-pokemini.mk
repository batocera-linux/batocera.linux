################################################################################
#
# libretro-pokemini
#
################################################################################
# Version: Commits on May 27, 2023
LIBRETRO_POKEMINI_VERSION = 9bf450887026d9b92d4f9432b5d2a5ed749a35e2
LIBRETRO_POKEMINI_SITE = $(call github,libretro,PokeMini,$(LIBRETRO_POKEMINI_VERSION))
LIBRETRO_POKEMINI_LICENSE = GPLv3

LIBRETRO_POKEMINI_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_POKEMINI_PLATFORM = armv
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_POKEMINI_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_POKEMINI_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_POKEMINI_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_POKEMINI_PLATFORM = rpi4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_POKEMINI_PLATFORM = rpi5
else ifeq ($(BR2_aarch64),y)
LIBRETRO_POKEMINI_PLATFORM = unix
endif

define LIBRETRO_POKEMINI_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_POKEMINI_PLATFORM)"
endef

define LIBRETRO_POKEMINI_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/pokemini_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pokemini_libretro.so
endef

$(eval $(generic-package))
