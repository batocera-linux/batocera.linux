################################################################################
#
# POKEMINI
#
################################################################################
# Version.: Commits on Nov 16, 2020
LIBRETRO_POKEMINI_VERSION = 7a2016e09fe979ff60c9f2e19a4bda57c4ea4de4
LIBRETRO_POKEMINI_SITE = $(call github,libretro,PokeMini,$(LIBRETRO_POKEMINI_VERSION))
LIBRETRO_POKEMINI_LICENSE = GPLv3

LIBRETRO_POKEMINI_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_POKEMINI_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
	LIBRETRO_POKEMINI_PLATFORM = rpi4
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_POKEMINI_PLATFORM = classic_armv8_a35
endif

define LIBRETRO_POKEMINI_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_POKEMINI_PLATFORM)"
endef

define LIBRETRO_POKEMINI_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/pokemini_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pokemini_libretro.so
endef

$(eval $(generic-package))
