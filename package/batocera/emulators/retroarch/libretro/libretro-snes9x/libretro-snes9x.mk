################################################################################
#
# SNES9X
#
################################################################################
# Version.: Commits on Mar 31, 2020
LIBRETRO_SNES9X_VERSION = 432fc08498b33190a41ae659c3c5fccbeb5b8b3e
LIBRETRO_SNES9X_SITE = $(call github,snes9xgit,snes9x,$(LIBRETRO_SNES9X_VERSION))
LIBRETRO_SNES9X_LICENSE = Non-commercial

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_SNES9X_PLATFORM = classic_armv8_a35
else
	LIBRETRO_SNES9X_PLATFORM = $(LIBRETRO_PLATFORM)
endif

define LIBRETRO_SNES9X_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		-C $(@D)/libretro -f Makefile platform="$(LIBRETRO_SNES9X_PLATFORM)"
endef

define LIBRETRO_SNES9X_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro/snes9x_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/snes9x_libretro.so
endef

$(eval $(generic-package))
