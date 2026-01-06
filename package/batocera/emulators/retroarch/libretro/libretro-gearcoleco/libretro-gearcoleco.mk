################################################################################
#
# libretro-gearcoleco
#
################################################################################

LIBRETRO_GEARCOLECO_VERSION = 1.5.5
LIBRETRO_GEARCOLECO_SITE = $(call github,drhelius,Gearcoleco,$(LIBRETRO_GEARCOLECO_VERSION))
LIBRETRO_GEARCOLECO_SITE_METHOD = tar
LIBRETRO_GEARCOLECO_LICENSE = GPLv3
LIBRETRO_GEARCOLECO_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_GEARCOLECO_BUILD_SUBDIR = platforms/libretro
LIBRETRO_GEARCOLECO_MAKE_OPTS += \
    platform=unix

define LIBRETRO_GEARCOLECO_BUILD_CMDS
    $(TARGET_MAKE_ENV) $(MAKE) \
        platform=unix \
        -C $(@D)/platforms/libretro
endef

define LIBRETRO_GEARCOLECO_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 \
        $(@D)/platforms/libretro/gearcoleco_libretro.so \
        $(TARGET_DIR)/usr/lib/libretro/gearcoleco_libretro.so
endef

$(eval $(generic-package))
