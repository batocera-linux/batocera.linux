################################################################################
#
# LIBRETRO PC98
#
################################################################################
# Version.: Commits on Apr 14, 2019
LIBRETRO_PC98_VERSION = 63c51ce80fabdcebf1325e926225d6462c797ffd
LIBRETRO_PC98_SITE = $(call github,AZO234,NP2kai,$(LIBRETRO_PC98_VERSION))
LIBRETRO_PC98_LICENSE = GPLv3

define LIBRETRO_PC98_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)/sdl2/ -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_PC98_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/np2kai
	$(INSTALL) -D $(@D)/sdl2/np2kai_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/np2kai_libretro.so
endef

$(eval $(generic-package))
