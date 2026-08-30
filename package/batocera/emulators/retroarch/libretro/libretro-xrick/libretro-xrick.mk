################################################################################
#
# libretro-xrick
#
################################################################################
# Version: Commits on Jul 28, 2026
LIBRETRO_XRICK_VERSION = fcfde3623a04b4e986548e06d46630fcd0bd1e18
LIBRETRO_XRICK_SITE = $(call github,libretro,xrick-libretro,$(LIBRETRO_XRICK_VERSION))
LIBRETRO_XRICK_LICENSE = GPL-3.0
LIBRETRO_XRICK_DEPENDENCIES += retroarch
LIBRETRO_XRICK_EMULATOR_INFO = xrick.libretro.core.yml

define LIBRETRO_XRICK_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="unix"
endef

define LIBRETRO_XRICK_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/xrick_libretro.so \
    $(TARGET_DIR)/usr/lib/libretro/xrick_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))