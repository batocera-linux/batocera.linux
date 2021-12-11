################################################################################
#
# PUAE
#
################################################################################
# Last commit: Nov 27, 2021
LIBRETRO_PUAE_VERSION = 3ec4903f23197ace99a451b77ff819eeb248da07
LIBRETRO_PUAE_SITE = $(call github,libretro,libretro-uae,$(LIBRETRO_PUAE_VERSION))
LIBRETRO_PUAE__LICENSE = GPLv2

LIBRETRO_PUAE_PLATFORM=$(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_PUAE_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_PUAE_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    ifeq ($(BR2_arm),y)
        LIBRETRO_PUAE_PLATFORM = rpi3
    else
        LIBRETRO_PUAE_PLATFORM = rpi3_64
    endif

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_PUAE_PLATFORM = rpi4
endif

define LIBRETRO_PUAE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PUAE_PLATFORM)"
endef

define LIBRETRO_PUAE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/puae_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/puae_libretro.so
endef

$(eval $(generic-package))
