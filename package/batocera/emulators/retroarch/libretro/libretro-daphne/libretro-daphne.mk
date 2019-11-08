################################################################################
#
# DAPHNE
#
################################################################################
# Version.: Commits on Sep 14, 2019
LIBRETRO_DAPHNE_VERSION = 7e5cac88d0509c6f4722100c5b8a9b5ee91f404a
LIBRETRO_DAPHNE_SITE = $(call github,libretro,daphne,$(LIBRETRO_DAPHNE_VERSION))

define LIBRETRO_DAPHNE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="unix"
endef

define LIBRETRO_DAPHNE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/daphne_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/daphne_libretro.so
endef

$(eval $(generic-package))
