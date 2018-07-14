################################################################################
#
# LIBRETRO REICAST OIT
#
################################################################################
# Version.: Commits on Jul 14, 2018
LIBRETRO_REICAST_OIT_VERSION = fc8eb6db0484def28291466f3d03d305db1098bc
LIBRETRO_REICAST_OIT_SITE = $(call github,libretro,reicast-emulator,$(LIBRETRO_REICAST_OIT_VERSION))

define LIBRETRO_REICAST_OIT_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" AR="$(TARGET_AR)" -C $(@D) -f Makefile platform="$(LIBRETRO_PLATFORM)" HAVE_OIT=1
endef

define LIBRETRO_REICAST_OIT_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/reicast_oit_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/reicast_oit_libretro.so
endef

$(eval $(generic-package))
