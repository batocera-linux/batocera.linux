################################################################################
#
# libretro-beetle-pce-fast
#
################################################################################
# Version: Commits on Oct 6, 2023
LIBRETRO_BEETLE_PCE_FAST_VERSION = 1ce7a4a941b10aa0c2973cb441b89ee99e2c8d0e
LIBRETRO_BEETLE_PCE_FAST_SITE = $(call github,libretro,beetle-pce-fast-libretro,$(LIBRETRO_BEETLE_PCE_FAST_VERSION))
LIBRETRO_BEETLE_PCE_FAST_LICENSE = GPLv2

LIBRETRO_BEETLE_PCE_FAST_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_BEETLE_PCE_FAST_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_BEETLE_PCE_FAST_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_BEETLE_PCE_FAST_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_BEETLE_PCE_FAST_PLATFORM = rpi4_64
endif

define LIBRETRO_BEETLE_PCE_FAST_BUILD_CMDS
    $(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D) platform="$(LIBRETRO_BEETLE_PCE_FAST_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_BEETLE_PCE_FAST_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_BEETLE_PCE_FAST_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_pce_fast_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pce_fast_libretro.so
endef

$(eval $(generic-package))
