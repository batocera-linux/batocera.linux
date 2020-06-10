
################################################################################
#
# NEOCD
#
################################################################################
# Version.: Commits on May 06, 2020
# Commit e58c46d1653a4a309767ba286f19abdbdcbb7f87 is causing a long delay when starting the game, 
# in the next update check if this problem has been fixed.
LIBRETRO_NEOCD_VERSION = 8a17bc1736f04acbaa7e2c3c5ac33f20f992c4a1
LIBRETRO_NEOCD_SITE = https://github.com/libretro/neocd_libretro.git
LIBRETRO_NEOCD_SITE_METHOD=git
LIBRETRO_NEOCD_GIT_SUBMODULES=YES
LIBRETRO_NEOCD_LICENSE = GPLv3

define LIBRETRO_NEOCD_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_NEOCD_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/neocd_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/neocd_libretro.so
endef

$(eval $(generic-package))
