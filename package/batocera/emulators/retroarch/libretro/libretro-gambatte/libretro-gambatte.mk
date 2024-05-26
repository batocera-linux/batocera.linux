################################################################################
#
# libretro-gambatte
#
################################################################################
# Version: Commits on Feb 23, 2024
LIBRETRO_GAMBATTE_VERSION = 4041d5a6c474d2d01b4cb1e81324b06b51d0147b
LIBRETRO_GAMBATTE_SITE = $(call github,libretro,gambatte-libretro,$(LIBRETRO_GAMBATTE_VERSION))
LIBRETRO_GAMBATTE_LICENSE = GPLv2

LIBRETRO_GAMBATTE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_GAMBATTE_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_GAMBATTE_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_GAMBATTE_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_GAMBATTE_PLATFORM = rpi4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_GAMBATTE_PLATFORM = rpi5
endif

define LIBRETRO_GAMBATTE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) \
	    -f Makefile platform="$(LIBRETRO_GAMBATTE_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_GAMBATTE_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_GAMBATTE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/gambatte_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gambatte_libretro.so
endef

$(eval $(generic-package))
