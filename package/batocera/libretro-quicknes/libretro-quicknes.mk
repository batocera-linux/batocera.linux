################################################################################
#
# QUICKNES
#
################################################################################
LIBRETRO_QUICKNES_VERSION = b4598fdf3fd7518c037db5bdd6bf69cc169a021d
LIBRETRO_QUICKNES_SITE = $(call github,libretro,quicknes_core,$(LIBRETRO_QUICKNES_VERSION))

define LIBRETRO_QUICKNES_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_QUICKNES_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/quicknes_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/quicknes_libretro.so
endef

$(eval $(generic-package))
