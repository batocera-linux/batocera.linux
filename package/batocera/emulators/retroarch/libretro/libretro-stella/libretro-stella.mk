################################################################################
#
# libretro-stella
#
################################################################################
# Version: Commits on Oct 10, 2022
LIBRETRO_STELLA_VERSION = 9ce0d374f6b2764484a0ccb06135f3c7b747e115
LIBRETRO_STELLA_SITE = $(call github,stella-emu,stella,$(LIBRETRO_STELLA_VERSION))
LIBRETRO_STELLA_LICENSE = GPLv2

LIBRETRO_STELLA_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_STELLA_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_STELLA_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
LIBRETRO_STELLA_PLATFORM = rpi3

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_STELLA_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_STELLA_PLATFORM = rpi4
endif

define LIBRETRO_STELLA_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/src/os/libretro -f Makefile platform="$(LIBRETRO_STELLA_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_STELLA_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_STELLA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/src/os/libretro/stella_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/stella_libretro.so
endef

$(eval $(generic-package))
