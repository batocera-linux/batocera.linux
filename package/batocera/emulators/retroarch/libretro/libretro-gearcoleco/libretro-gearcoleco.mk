################################################################################
#
# libretro-gearcoleco
#
################################################################################

LIBRETRO_GEARCOLECO_VERSION = 1.5.5
LIBRETRO_GEARCOLECO_SITE = $(call github,drhelius,Gearcoleco,$(LIBRETRO_GEARCOLECO_VERSION))
LIBRETRO_GEARCOLECO_LICENSE = GPLv3

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
GEARCOLECO_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
GEARCOLECO_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
GEARCOLECO_PLATFORM = rpi3
else
GEARCOLECO_PLATFORM = unix
endif

define LIBRETRO_GEARCOLECO_BUILD_CMDS
    $(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)/platforms/libretro \
        platform=$(GEARCOLECO_PLATFORM)
endef

define LIBRETRO_GEARCOLECO_INSTALL_TARGET_CMDS
    $(INSTALL) -D -m 0755 \
        $(@D)/platforms/libretro/gearcoleco_libretro.so \
        $(TARGET_DIR)/usr/lib/libretro/gearcoleco_libretro.so
endef

$(eval $(generic-package))
