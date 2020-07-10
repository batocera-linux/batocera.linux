################################################################################
#
# ZX81
#
################################################################################
# Version.: Commits on Jun 13, 2020
LIBRETRO_81_VERSION = 7d769d09b1b6932466272aaf82b37922c1e2e61f
LIBRETRO_81_SITE = $(call github,libretro,81-libretro,$(LIBRETRO_81_VERSION))
LIBRETRO_81_LICENSE = GPLv3

LIBRETRO_81_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_81_PLATFORM = armv neon
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_81_PLATFORM = classic_armv8_a35
endif

define LIBRETRO_81_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_81_PLATFORM)"
endef

define LIBRETRO_81_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/81_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/81_libretro.so
endef

$(eval $(generic-package))
