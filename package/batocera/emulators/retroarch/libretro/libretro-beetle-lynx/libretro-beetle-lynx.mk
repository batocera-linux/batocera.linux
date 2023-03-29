################################################################################
#
# libretro-beetle-lynx
#
################################################################################
# Version.: Commits on Mar 17, 2023
LIBRETRO_BEETLE_LYNX_VERSION = 66a4bc8d7d5328877684c20581c8cee34abb1b37
LIBRETRO_BEETLE_LYNX_SITE = $(call github,libretro,beetle-lynx-libretro,$(LIBRETRO_BEETLE_LYNX_VERSION))
LIBRETRO_BEETLE_LYNX_LICENSE = GPLv2

LIBRETRO_BEETLE_LYNX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_BEETLE_LYNX_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_BEETLE_LYNX_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_BEETLE_LYNX_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_BEETLE_LYNX_PLATFORM = rpi4_64
endif

define LIBRETRO_BEETLE_LYNX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_BEETLE_LYNX_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_BEETLE_LYNX_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_BEETLE_LYNX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_lynx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mednafen_lynx_libretro.so
endef

$(eval $(generic-package))
