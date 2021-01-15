################################################################################
#
# Retro8 - Pico-8 emulator
#
################################################################################
# Version.: Commits on Nov 20, 2020
LIBRETRO_RETRO8_VERSION = 87b5f5446a4dc7987f836ece5c6a3e23daeb9839
LIBRETRO_RETRO8_SITE = $(call github,jakz,retro8,$(LIBRETRO_RETRO8_VERSION))
LIBRETRO_RETRO8_LICENSE = GPLv3.0

LIBRETRO_RETRO8_PLATFORM = $(LIBRETRO_PLATFORM)

LIBRETRO_RETRO8_COMP_PLATFORM = unix

define LIBRETRO_RETRO8_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_RETRO8_COMP_PLATFORM)"
endef

define LIBRETRO_RETRO8_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/retro8_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/retro8_libretro.so
endef

$(eval $(generic-package))
