################################################################################
#
# libretro-handy
#
################################################################################
# Version: Commits on Jan 1, 2024
LIBRETRO_HANDY_VERSION = 65d6b865544cd441ef2bd18cde7bd834c23d0e48
LIBRETRO_HANDY_SITE = $(call github,libretro,libretro-handy,$(LIBRETRO_HANDY_VERSION))
LIBRETRO_HANDY_LICENSE = Zlib

LIBRETRO_HANDY_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_HANDY_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_HANDY_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_HANDY_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_HANDY_PLATFORM = rpi4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_HANDY_PLATFORM = rpi5
endif

define LIBRETRO_HANDY_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ \
	    -f Makefile platform="$(LIBRETRO_HANDY_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_HANDY_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_HANDY_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/handy_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/handy_libretro.so
endef

$(eval $(generic-package))
