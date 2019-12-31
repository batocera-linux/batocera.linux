################################################################################
#
# LIBRETRO-KRONOS
#
################################################################################
# Version.: Commits on Dec 30, 2019
LIBRETRO_KRONOS_VERSION = 3937ab74ee61ecda2b77b9a1626f47fb8766a02e
LIBRETRO_KRONOS_SITE = $(call github,libretro,yabause,$(LIBRETRO_KRONOS_VERSION))
LIBRETRO_KRONOS_LICENSE = BSD-3-Clause

define LIBRETRO_KRONOS_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/yabause/src/libretro -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_KRONOS_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/yabause/src/libretro/kronos_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/kronos_libretro.so
endef

$(eval $(generic-package))
