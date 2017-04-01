################################################################################
#
# REICAST
#
################################################################################
LIBRETRO_REICAST_VERSION = 148638c654a61aa32df7023498f261c4fb23c9aa
LIBRETRO_REICAST_SITE = $(call github,libretro,reicast-emulator,$(LIBRETRO_REICAST_VERSION))

define LIBRETRO_REICAST_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" AR="$(TARGET_AR)" -C $(@D) -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_REICAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/reicast_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/reicast_libretro.so
endef

$(eval $(generic-package))
