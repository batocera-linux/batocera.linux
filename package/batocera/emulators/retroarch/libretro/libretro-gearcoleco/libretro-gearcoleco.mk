################################################################################
#
# libretro-gearcoleco
#
################################################################################

LIBRETRO_GEARCOLECO_VERSION = 1.5.5
LIBRETRO_GEARCOLECO_SITE = $(call github,drhelius,Gearcoleco,$(LIBRETRO_GEARCOLECO_VERSION))
LIBRETRO_GEARCOLECO_LICENSE = GPLv3

define LIBRETRO_GEARCOLECO_BUILD_CMDS
    $(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)/platforms/libretro platform=unix
endef

define LIBRETRO_GEARCOLECO_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/usr/lib/libretro
    $(INSTALL) -D -m 0755 \
        $(@D)/platforms/libretro/gearcoleco_libretro.so \
        $(TARGET_DIR)/usr/lib/libretro/gearcoleco_libretro.so
endef

$(eval $(generic-package))
