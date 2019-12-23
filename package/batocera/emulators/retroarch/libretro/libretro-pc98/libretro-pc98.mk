################################################################################
#
# LIBRETRO PC98
#
################################################################################
# Version.: Commits on Dec 10, 2019
LIBRETRO_PC98_VERSION = 8fe2d007cc9d339908b726654e9489094a6510ac
LIBRETRO_PC98_SITE = $(call github,AZO234,NP2kai,$(LIBRETRO_PC98_VERSION))
LIBRETRO_PC98_LICENSE = GPLv3

define LIBRETRO_PC98_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		-C $(@D)/sdl2/ -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_PC98_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/sdl2/np2kai_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/np2kai_libretro.so
endef

$(eval $(generic-package))
