################################################################################
#
# SNES9X_NEXT
#
################################################################################
# Version.: Commits on Nov 11, 2020
LIBRETRO_SNES9X_NEXT_VERSION = bea042df986703233b3e7229d23dc17f2cc90258
LIBRETRO_SNES9X_NEXT_SITE = $(call github,libretro,snes9x2010,$(LIBRETRO_SNES9X_NEXT_VERSION))
LIBRETRO_SNES9X_NEXT_LICENSE = Non-commercial

LIBRETRO_SNES9X_NEXT_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2)$(BR2_PACKAGE_BATOCERA_TARGET_VIM3),y)
	LIBRETRO_SNES9X_NEXT_PLATFORM = CortexA73_G12B
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_SNES9X_NEXT_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
	LIBRETRO_SNES9X_NEXT_PLATFORM = rpi4_64
endif

define LIBRETRO_SNES9X_NEXT_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_SNES9X_NEXT_PLATFORM)"
endef

define LIBRETRO_SNES9X_NEXT_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/snes9x2010_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/snes9x_next_libretro.so
endef

$(eval $(generic-package))
