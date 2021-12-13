################################################################################
#
# BEETLE_WSWAN
#
################################################################################
# Version.: Commits on Nov 25, 2021
LIBRETRO_BEETLE_WSWAN_VERSION = ea00c1d8eb9894538dd8758975cd9d6ae99ead1e
LIBRETRO_BEETLE_WSWAN_SITE = $(call github,libretro,beetle-wswan-libretro,$(LIBRETRO_BEETLE_WSWAN_VERSION))
LIBRETRO_BEETLE_WSWAN_LICENSE = GPLv2

LIBRETRO_BEETLE_WSWAN_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_BEETLE_WSWAN_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_BEETLE_WSWAN_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    ifeq ($(BR2_arm),y)
        LIBRETRO_BEETLE_WSWAN_PLATFORM = rpi3
    else
        LIBRETRO_BEETLE_WSWAN_PLATFORM = rpi3_64
    endif

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_BEETLE_WSWAN_PLATFORM = rpi4
endif

define LIBRETRO_BEETLE_WSWAN_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_BEETLE_WSWAN_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_BEETLE_WSWAN_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_BEETLE_WSWAN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_wswan_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mednafen_wswan_libretro.so
endef

$(eval $(generic-package))
