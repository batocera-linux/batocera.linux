################################################################################
#
# LIBRETRO REICAST OIT
#
################################################################################
# Version.: Commits on Aug 31, 2018
LIBRETRO_REICAST_OIT_VERSION = 6c1f972e793eb7d37edaa67f19f7d03e9f908075
LIBRETRO_REICAST_OIT_SITE = $(call github,libretro,reicast-emulator,$(LIBRETRO_REICAST_OIT_VERSION))

define LIBRETRO_REICAST_OIT_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" AR="$(TARGET_AR)" -C $(@D) -f Makefile HAVE_OPENMP=0 HAVE_OIT=1 platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_REICAST_OIT_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/reicast_oit_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/reicast_oit_libretro.so
endef

$(eval $(generic-package))
