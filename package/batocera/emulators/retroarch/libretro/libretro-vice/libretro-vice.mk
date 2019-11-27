################################################################################
#
# LIBRETRO-VICE
#
################################################################################
# Version.: Commits on Nov 19, 2019
LIBRETRO_VICE_VERSION = 628db1cce0ac5dbc09e67bb78c244f7389a2a8c7
LIBRETRO_VICE_SITE = $(call github,libretro,vice-libretro,$(LIBRETRO_VICE_VERSION))
LIBRETRO_VICE_LICENSE = GPLv2

define LIBRETRO_VICE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D) -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_VICE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/vice_*_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/vice_libretro.so
endef

$(eval $(generic-package))
