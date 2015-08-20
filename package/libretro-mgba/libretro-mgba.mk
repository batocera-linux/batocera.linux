################################################################################
#
# MGBA
#
################################################################################
LIBRETRO_MGBA_VERSION = 3b137e25f2368a57da02bc0489e83a90788fc23a
LIBRETRO_MGBA_SITE = $(call github,libretro,mgba,$(LIBRETRO_MGBA_VERSION))

define LIBRETRO_MGBA_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_MGBA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mgba_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mgba_libretro.so
endef

$(eval $(generic-package))
