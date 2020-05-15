
################################################################################
#
# NEOCD
#
################################################################################
# Version.: Commits on Apr 22, 2020
LIBRETRO_NEOCD_VERSION = 9565de1a9f37b13b7626a308aa87f6432879e4e1
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
