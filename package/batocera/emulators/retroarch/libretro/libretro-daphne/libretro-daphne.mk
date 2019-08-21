################################################################################
#
# DAPHNE
#
################################################################################
LIBRETRO_DAPHNE_VERSION = 5949fa10f376fd09d6237212a8606428b79626e0
LIBRETRO_DAPHNE_SITE = $(call github,libretro,daphne,$(LIBRETRO_DAPHNE_VERSION))

define LIBRETRO_DAPHNE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="unix"
endef

define LIBRETRO_DAPHNE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/daphne_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/daphne_libretro.so
endef

$(eval $(generic-package))
