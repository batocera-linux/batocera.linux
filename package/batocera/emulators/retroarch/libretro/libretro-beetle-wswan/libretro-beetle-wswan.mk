################################################################################
#
# BEETLE_WSWAN
#
################################################################################
# Version.: Commits on Sep 18, 2021
LIBRETRO_BEETLE_WSWAN_VERSION = b631efbf08a09bb139461b17947c6a5309789820
LIBRETRO_BEETLE_WSWAN_SITE = $(call github,libretro,beetle-wswan-libretro,$(LIBRETRO_BEETLE_WSWAN_VERSION))
LIBRETRO_BEETLE_WSWAN_LICENSE = GPLv2

LIBRETRO_BEETLE_WSWAN_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
LIBRETRO_BEETLE_WSWAN_PLATFORM = rpi3_64
endif

define LIBRETRO_BEETLE_WSWAN_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_BEETLE_WSWAN_PLATFORM)"
endef

define LIBRETRO_BEETLE_WSWAN_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_wswan_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mednafen_wswan_libretro.so
endef

$(eval $(generic-package))
