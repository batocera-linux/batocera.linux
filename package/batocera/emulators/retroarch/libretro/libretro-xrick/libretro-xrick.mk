################################################################################
#
# libretro-xrick
#
################################################################################
# Version: Commits on Mar 31, 2022
LIBRETRO_XRICK_VERSION = 10d7318c374de3e0eb056e6c7e823c644a7ce078
LIBRETRO_XRICK_SITE = $(call github,libretro,xrick-libretro,$(LIBRETRO_XRICK_VERSION))
LIBRETRO_XRICK_LICENSE = GPL-3.0

define LIBRETRO_XRICK_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="unix"
endef

define LIBRETRO_XRICK_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/xrick_libretro.so \
    $(TARGET_DIR)/usr/lib/libretro/xrick_libretro.so
endef

$(eval $(generic-package))
