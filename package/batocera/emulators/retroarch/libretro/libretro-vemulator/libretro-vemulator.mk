################################################################################
#
# libretro-vemulator
#
################################################################################
# Version: Commits on Aug 23, 2026
LIBRETRO_VEMULATOR_VERSION = 27a062f6ae532e5028e4fb54f523cc689e78146a
LIBRETRO_VEMULATOR_SITE = $(call github,libretro,vemulator-libretro,$(LIBRETRO_VEMULATOR_VERSION))
LIBRETRO_VEMULATOR_LICENSE = GPLv3
LIBRETRO_VEMULATOR_DEPENDENCIES += retroarch
LIBRETRO_VEMULATOR_EMULATOR_INFO = vemulator.libretro.core.yml

define LIBRETRO_VEMULATOR_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="unix"
endef

define LIBRETRO_VEMULATOR_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/vemulator_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/vemulator_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))