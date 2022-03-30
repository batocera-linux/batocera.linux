################################################################################
#
# libretro-lutro
#
################################################################################
# Version: Commits on Mar 6, 2022
LIBRETRO_LUTRO_VERSION = cc6b06db98bcb7d0379082a876fed870e203ccb3
LIBRETRO_LUTRO_SITE = $(call github,libretro,libretro-lutro,$(LIBRETRO_LUTRO_VERSION))
LIBRETRO_LUTRO_LICENSE = MIT

LIBRETRO_LUTRO_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_LUTRO_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_LUTRO_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    ifeq ($(BR2_arm),y)
        LIBRETRO_LUTRO_PLATFORM = rpi3
    else
        LIBRETRO_LUTRO_PLATFORM = rpi3_64
    endif

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_LUTRO_PLATFORM = rpi4_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_LUTRO_PLATFORM = armv neon

else ifeq ($(BR2_arm),y)
LIBRETRO_LUTRO_PLATFORM = armv neon

else ifeq ($(BR2_aarch64),y)
LIBRETRO_LUTRO_PLATFORM = unix
endif

define LIBRETRO_LUTRO_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_LUTRO_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_LUTRO_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_LUTRO_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/lutro_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/lutro_libretro.so
endef

$(eval $(generic-package))
