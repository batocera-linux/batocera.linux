################################################################################
#
# libretro-atari800
#
################################################################################
# Version: Commits on Nov 14, 2023
LIBRETRO_ATARI800_VERSION = 410d7bf0c215f3444793a9cec51c129e7b67c400
LIBRETRO_ATARI800_SITE = $(call github,libretro,libretro-atari800,$(LIBRETRO_ATARI800_VERSION))
LIBRETRO_ATARI800_LICENSE = GPL

LIBRETRO_ATARI800_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_ATARI800_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_ATARI800_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837)),y)
LIBRETRO_ATARI800_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_ATARI800_PLATFORM = rpi4

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_ATARI800_PLATFORM = rpi5

endif

define LIBRETRO_ATARI800_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/ -f Makefile platform="$(LIBRETRO_ATARI800_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_ATARI800_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_ATARI800_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/atari800_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/atari800_libretro.so
endef

$(eval $(generic-package))
