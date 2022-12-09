################################################################################
#
# libretro-prosystem
#
################################################################################
# Version: Commits on Aug 26, 2022
LIBRETRO_PROSYSTEM_VERSION = cf544d3c8e40ff197ea5bb177a1269db31077803
LIBRETRO_PROSYSTEM_SITE = $(call github,libretro,prosystem-libretro,$(LIBRETRO_PROSYSTEM_VERSION))
LIBRETRO_PROSYSTEM_LICENSE = GPLv2

LIBRETRO_PROSYSTEM_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_PROSYSTEM_PLATFORM = armv

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_PROSYSTEM_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_PROSYSTEM_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
LIBRETRO_PROSYSTEM_PLATFORM = rpi3

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_PROSYSTEM_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_PROSYSTEM_PLATFORM = rpi4

else ifeq ($(BR2_aarch64),y)
LIBRETRO_PROSYSTEM_PLATFORM = unix
endif

define LIBRETRO_PROSYSTEM_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PROSYSTEM_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_PROSYSTEM_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_PROSYSTEM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/prosystem_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/prosystem_libretro.so
endef

$(eval $(generic-package))
