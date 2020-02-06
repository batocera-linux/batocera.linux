################################################################################
#
# SNES9X_NEXT
#
################################################################################
# Version.: Commits on Dec 27, 2019
LIBRETRO_SNES9X_NEXT_VERSION = ba9f2240360f8db270fb6ba5465c79c317070560
LIBRETRO_SNES9X_NEXT_SITE = $(call github,libretro,snes9x2010,$(LIBRETRO_SNES9X_NEXT_VERSION))
LIBRETRO_SNES9X_NEXT_LICENSE = Non-commercial

define LIBRETRO_SNES9X_NEXT_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		-C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_SNES9X_NEXT_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/snes9x2010_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/snes9x_next_libretro.so
endef

$(eval $(generic-package))
