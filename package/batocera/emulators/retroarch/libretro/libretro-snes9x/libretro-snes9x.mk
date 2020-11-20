################################################################################
#
# SNES9X
#
################################################################################
# Version.: Commits on Nov 04, 2020
LIBRETRO_SNES9X_VERSION = 364aa1ba5d9cd5ca972373d3f5080f253f64e19e
LIBRETRO_SNES9X_SITE = $(call github,snes9xgit,snes9x,$(LIBRETRO_SNES9X_VERSION))
LIBRETRO_SNES9X_LICENSE = Non-commercial

LIBRETRO_SNES9X_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2)$(BR2_PACKAGE_BATOCERA_TARGET_VIM3),y)
	LIBRETRO_SNES9X_PLATFORM = CortexA73_G12B
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_SNES9X_PLATFORM = classic_armv8_a35
endif

define LIBRETRO_SNES9X_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/libretro -f Makefile platform="$(LIBRETRO_SNES9X_PLATFORM)"
endef

define LIBRETRO_SNES9X_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro/snes9x_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/snes9x_libretro.so
endef

$(eval $(generic-package))
