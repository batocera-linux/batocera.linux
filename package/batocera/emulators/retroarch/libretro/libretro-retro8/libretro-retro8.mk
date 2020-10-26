################################################################################
#
# Retro8 - Pico-8 emulator
#
################################################################################
# Version.: Commits on Oct 20, 2020
LIBRETRO_RETRO8_VERSION = cda293422156a75775794c46a86d14838b4dd8a6
LIBRETRO_RETRO8_SITE = $(call github,jakz,retro8,$(LIBRETRO_RETRO8_VERSION))
LIBRETRO_RETRO8_LICENSE = GPLv3.0

LIBRETRO_RETRO8_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_RETRO8_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_RETRO8_PLATFORM = classic_armv8_a35
endif

define LIBRETRO_RETRO8_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_RETRO8_PLATFORM)"
endef

define LIBRETRO_RETRO8_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/retro8_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/retro8_libretro.so
endef

$(eval $(generic-package))
