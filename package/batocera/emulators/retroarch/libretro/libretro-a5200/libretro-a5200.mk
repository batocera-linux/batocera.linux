################################################################################
#
# libretro-a5200
#
################################################################################
# Version.: Commits on Jun 22, 2022
LIBRETRO_A5200_VERSION = 46035d00a5fb7ffd3a63172c2d0a8c6b6ae7efc1
LIBRETRO_A5200_SITE = $(call github,libretro,a5200,$(LIBRETRO_A5200_VERSION))
LIBRETRO_A5200_LICENSE = GPLv2

LIBRETRO_A5200_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_A5200_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_A5200_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
LIBRETRO_A5200_PLATFORM = rpi3

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
LIBRETRO_A5200_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_A5200_PLATFORM = rpi4

else ifeq ($(BR2_arm),y)
LIBRETRO_A5200_PLATFORM = ARCH=armv

else ifeq ($(BR2_aarch64),y)
LIBRETRO_A5200_PLATFORM = ARCH=aarch64
endif

define LIBRETRO_A5200_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_A5200_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_A5200_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_A5200_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/a5200_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/a5200_libretro.so
endef

$(eval $(generic-package))
