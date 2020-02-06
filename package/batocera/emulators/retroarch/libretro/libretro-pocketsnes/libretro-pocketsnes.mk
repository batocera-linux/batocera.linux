################################################################################
#
# POCKETSNESS
#
################################################################################
# Version.: Commits on Sep 14, 2019
LIBRETRO_POCKETSNES_VERSION = 354bcb5acea0aa45b56ae553e0b2b4f10792dfeb
LIBRETRO_POCKETSNES_SITE = $(call github,libretro,snes9x2002,$(LIBRETRO_POCKETSNES_VERSION))
LIBRETRO_POCKETSNES_LICENSE = Non-commercial

define LIBRETRO_POCKETSNES_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" LD="$(TARGET_LD)" $(MAKE) CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" -C $(@D)
endef

define LIBRETRO_POCKETSNES_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/snes9x2002_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pocketsnes_libretro.so
endef

$(eval $(generic-package))
