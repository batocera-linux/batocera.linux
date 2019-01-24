################################################################################
#
# LIBRETRO-KRONOS
#
################################################################################
# Version.: Commits on Dec 25, 2018
LIBRETRO_KRONOS_VERSION = 8ba32ca31cb26a816ea61fcfa6a86668dfe6d1ee
LIBRETRO_KRONOS_SITE = $(call github,libretro-mirrors,Kronos,$(LIBRETRO_KRONOS_VERSION))

define LIBRETRO_KRONOS_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/libretro -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_KRONOS_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro/kronos_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/kronos_libretro.so
endef

$(eval $(generic-package))
