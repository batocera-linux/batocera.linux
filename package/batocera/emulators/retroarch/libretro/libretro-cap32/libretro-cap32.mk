################################################################################
#
# CAP32
#
################################################################################
# Version.: Commits on Sep 7, 2019
LIBRETRO_CAP32_VERSION = 8681fbdc5623830078b38d713935caf4682e5295
LIBRETRO_CAP32_SITE = $(call github,libretro,libretro-cap32,$(LIBRETRO_CAP32_VERSION))
LIBRETRO_CAP32_LICENSE = GPLv2

define LIBRETRO_CAP32_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_CAP32_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/cap32_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/cap32_libretro.so
endef

$(eval $(generic-package))
