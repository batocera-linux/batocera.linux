################################################################################
#
# libretro-beetle-supergrafx
#
################################################################################
# Version: Commits on Oct 6, 2023
LIBRETRO_BEETLE_SUPERGRAFX_VERSION = 733b29460bfa254ccea096d29e8cc566e48aa633
LIBRETRO_BEETLE_SUPERGRAFX_SITE = $(call github,libretro,beetle-supergrafx-libretro,$(LIBRETRO_BEETLE_SUPERGRAFX_VERSION))
LIBRETRO_BEETLE_SUPERGRAFX_LICENSE = GPLv2

LIBRETRO_BEETLE_SUPERGRAFX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_BEETLE_SUPERGRAFX_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_BEETLE_SUPERGRAFX_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_BEETLE_SUPERGRAFX_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_BEETLE_SUPERGRAFX_PLATFORM = rpi4_64
endif

define LIBRETRO_BEETLE_SUPERGRAFX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/ -f Makefile platform="$(LIBRETRO_BEETLE_SUPERGRAFX_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_BEETLE_SUPERGRAFX_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_BEETLE_SUPERGRAFX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_supergrafx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mednafen_supergrafx_libretro.so
endef

$(eval $(generic-package))
