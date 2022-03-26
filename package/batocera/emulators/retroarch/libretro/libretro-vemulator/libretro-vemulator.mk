################################################################################
#
# libretro-vemulator
#
################################################################################
# Version: Commits on Nov 18, 2021
LIBRETRO_VEMULATOR_VERSION = bc5100a2558a1031ef2f00c31dc259ed85cf8b10
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
