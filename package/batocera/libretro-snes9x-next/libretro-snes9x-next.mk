################################################################################
#
# SNES9X_NEXT
#
################################################################################
LIBRETRO_SNES9X_NEXT_VERSION = a992e2f43444aac5279247026eb712f551865d8c
LIBRETRO_SNES9X_NEXT_SITE = $(call github,libretro,snes9x-next,$(LIBRETRO_SNES9X_NEXT_VERSION))

define LIBRETRO_SNES9X_NEXT_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_SNES9X_NEXT_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/snes9x2010_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/snes9x_next_libretro.so
endef

$(eval $(generic-package))
