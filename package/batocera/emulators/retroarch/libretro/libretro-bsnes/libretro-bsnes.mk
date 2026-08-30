################################################################################
#
# libretro-bsnes
#
################################################################################
# Version: Commits on Aug 12, 2026
LIBRETRO_BSNES_VERSION = 6d19eef5835a792e241e33194b4c1e9b75405b88
LIBRETRO_BSNES_SITE = $(call github,libretro,bsnes-libretro,$(LIBRETRO_BSNES_VERSION))
LIBRETRO_BSNES_LICENSE = GPLv3
LIBRETRO_BSNES_LICENSE_FILE = LICENSE.txt
LIBRETRO_BSNES_DEPENDENCIES += retroarch
LIBRETRO_BSNES_EMULATOR_INFO = bsnes.libretro.core.yml

define LIBRETRO_BSNES_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/ -f Makefile platform="unix"
endef

define LIBRETRO_BSNES_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bsnes_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bsnes_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))