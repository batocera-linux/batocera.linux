################################################################################
#
# QUICKNES
#
################################################################################
LIBRETRO_QUICKNES_VERSION = d712e2fbfb4fa1855360736540c3e7c56c5ff217
LIBRETRO_QUICKNES_SITE = $(call github,libretro,quicknes_core,$(LIBRETRO_QUICKNES_VERSION))

define LIBRETRO_QUICKNES_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_QUICKNES_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/quicknes_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/quicknes_libretro.so
endef

$(eval $(generic-package))
