################################################################################
#
# libretro-beetle-wswan
#
################################################################################
# Version: Commits on Nov 1, 2023
LIBRETRO_BEETLE_WSWAN_VERSION = 32bf70a3032a138baa969c22445f4b7821632c30
LIBRETRO_BEETLE_WSWAN_SITE = $(call github,libretro,beetle-wswan-libretro,$(LIBRETRO_BEETLE_WSWAN_VERSION))
LIBRETRO_BEETLE_WSWAN_LICENSE = GPLv2

LIBRETRO_BEETLE_WSWAN_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_BEETLE_WSWAN_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_BEETLE_WSWAN_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_BEETLE_WSWAN_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_BEETLE_WSWAN_PLATFORM = rpi4

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_BEETLE_WSWAN_PLATFORM = rpi5

endif

define LIBRETRO_BEETLE_WSWAN_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/ -f Makefile platform="$(LIBRETRO_BEETLE_WSWAN_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_BEETLE_WSWAN_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_BEETLE_WSWAN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_wswan_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mednafen_wswan_libretro.so
endef

$(eval $(generic-package))
