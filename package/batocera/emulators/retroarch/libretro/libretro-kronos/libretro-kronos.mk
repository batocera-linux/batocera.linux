################################################################################
#
# LIBRETRO-KRONOS
#
################################################################################
# Version.: Commits on Mar 17, 2019 (1.6.0)
LIBRETRO_KRONOS_VERSION = 4b9c39c5767b0a9d78ff5e13ad95929f9f287cae
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
