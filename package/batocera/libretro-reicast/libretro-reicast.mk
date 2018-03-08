################################################################################
#
# REICAST
#
################################################################################
LIBRETRO_REICAST_VERSION = fff2eb2f92251db82cb763d3ab1d19be4a705f95
LIBRETRO_REICAST_SITE = $(call github,libretro,reicast-emulator,$(LIBRETRO_REICAST_VERSION))

define LIBRETRO_REICAST_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" AR="$(TARGET_AR)" -C $(@D) -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_REICAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/reicast_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/libretro-reicast_libretro.so
endef

$(eval $(generic-package))
