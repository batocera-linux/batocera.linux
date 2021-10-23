################################################################################
#
# VEMULATOR
#
################################################################################
# Version.: Commits on Mar 27, 2021
LIBRETRO_VEMULATOR_VERSION = d7f48a2cca5f9694f9d6c8b2ff8b6a831e53b3c5
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
