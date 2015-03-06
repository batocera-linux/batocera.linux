################################################################################
#
# POCKETSNESS
#
################################################################################
LIBRETRO_POCKETSNES_VERSION = fccecaa7c88b4943d85aebe6412a98f6165a8f36
LIBRETRO_POCKETSNES_SITE = $(call github,libretro,pocketsnes-libretro,$(LIBRETRO_POCKETSNES_VERSION))

define LIBRETRO_POCKETSNES_BUILD_CMDS
		CFLAGS="$(TARGET_CFLAGS)" LD="$(TARGET_LD)" \
		$(MAKE) CC="$(TARGET_CC)" CXX="$(TARGET_CXX)" -C $(@D)
endef

define LIBRETRO_POCKETSNES_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pocketsnes_libretro.so
endef

$(eval $(generic-package))
