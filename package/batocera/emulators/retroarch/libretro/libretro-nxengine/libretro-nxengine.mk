################################################################################
#
# NXENGINE
#
################################################################################
# Version.: Commits on Jan 4, 2019
LIBRETRO_NXENGINE_VERSION = f83ccdc9a3c14bdcc5e9c291230a603e4686cfec
LIBRETRO_NXENGINE_SITE = $(call github,libretro,nxengine-libretro,$(LIBRETRO_NXENGINE_VERSION))
LIBRETRO_NXENGINE_LICENSE = GPLv3

define LIBRETRO_NXENGINE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_NXENGINE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/nxengine_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/nxengine_libretro.so
endef

$(eval $(generic-package))
