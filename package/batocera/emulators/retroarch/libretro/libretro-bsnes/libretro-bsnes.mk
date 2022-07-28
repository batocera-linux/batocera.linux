################################################################################
#
# libretro-bsnes
#
################################################################################
# Version.: Commits on Jun 14, 2022
LIBRETRO_BSNES_VERSION = 4eeaf860fd21a5b96b9993c25e732dccc19d98de
LIBRETRO_BSNES_SITE = $(call github,libretro,bsnes-libretro,$(LIBRETRO_BSNES_VERSION))
LIBRETRO_BSNES_LICENSE = GPLv3
LIBRETRO_BSNES_LICENSE_FILE = LICENSE.txt

define LIBRETRO_BSNES_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="unix"
endef

define LIBRETRO_BSNES_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bsnes_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bsnes_libretro.so
endef

$(eval $(generic-package))
