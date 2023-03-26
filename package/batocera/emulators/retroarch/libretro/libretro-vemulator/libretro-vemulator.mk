################################################################################
#
# libretro-vemulator
#
################################################################################
# Version: Commits on Mar 11, 2023
LIBRETRO_VEMULATOR_VERSION = ff9c39714fe64960b4050c6884c70c24e63de4fd
LIBRETRO_VEMULATOR_SITE = $(call github,libretro,vemulator-libretro,$(LIBRETRO_VEMULATOR_VERSION))
LIBRETRO_VEMULATOR_LICENSE = GPLv3

define LIBRETRO_VEMULATOR_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="unix"
endef

define LIBRETRO_VEMULATOR_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/vemulator_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/vemulator_libretro.so
endef

$(eval $(generic-package))
