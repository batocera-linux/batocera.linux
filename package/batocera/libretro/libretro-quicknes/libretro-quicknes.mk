################################################################################
#
# QUICKNES
#
################################################################################
# Version.: Commits on Apr 24, 2018
LIBRETRO_QUICKNES_VERSION = 6d50e29d1869ad5b69af013c3441a542e2c2b205
LIBRETRO_QUICKNES_SITE = $(call github,libretro,quicknes_core,$(LIBRETRO_QUICKNES_VERSION))

define LIBRETRO_QUICKNES_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_QUICKNES_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/quicknes_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/quicknes_libretro.so
endef

$(eval $(generic-package))
