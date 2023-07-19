################################################################################
#
# libretro-puae
#
################################################################################
# Version: Commits on Jul 19, 2023
LIBRETRO_PUAE_VERSION = a3ac83e50021b2d208cd02d17cd280db9857feb3
LIBRETRO_PUAE_SITE = $(call github,libretro,libretro-uae,$(LIBRETRO_PUAE_VERSION))
LIBRETRO_PUAE__LICENSE = GPLv2

LIBRETRO_PUAE_PLATFORM=$(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_PUAE_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_PUAE_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_PUAE_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_PUAE_PLATFORM = rpi4
endif

define LIBRETRO_PUAE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/ -f Makefile platform="$(LIBRETRO_PUAE_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_PUAE_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_PUAE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/puae_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/puae_libretro.so
endef

$(eval $(generic-package))
