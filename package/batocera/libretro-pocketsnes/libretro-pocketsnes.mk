################################################################################
#
# POCKETSNESS
#
################################################################################
LIBRETRO_POCKETSNES_VERSION = 04c179c85e266cb60c1135eb6c9cc6e7af2bb8de
LIBRETRO_POCKETSNES_SITE = $(call github,libretro,pocketsnes-libretro,$(LIBRETRO_POCKETSNES_VERSION))

define LIBRETRO_POCKETSNES_BUILD_CMDS
		CFLAGS="$(TARGET_CFLAGS)" LD="$(TARGET_LD)" \
		$(MAKE) CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" -C $(@D)
endef

define LIBRETRO_POCKETSNES_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/snes9x2002_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pocketsnes_libretro.so
endef

$(eval $(generic-package))
