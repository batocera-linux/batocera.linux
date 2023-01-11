################################################################################
#
# libretro-lowresnx
#
################################################################################
# Version: Commits on Jun 9, 2022
LIBRETRO_LOWRESNX_VERSION = 58af12f
LIBRETRO_LOWRESNX_SITE = $(call github,timoinutilis,lowres-nx,$(LIBRETRO_LOWRESNX_VERSION))
LIBRETRO_LOWRESNX_LICENSE = zlib

LIBRETRO_LOWRESNX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_LOWRESNX_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_LOWRESNX_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_LOWRESNX_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_LOWRESNX_PLATFORM = rpi4

else ifeq ($(BR2_arm),y)
LIBRETRO_LOWRESNX_PLATFORM = ARCH=armv

else ifeq ($(BR2_aarch64),y)
LIBRETRO_LOWRESNX_PLATFORM = ARCH=aarch64
endif

define LIBRETRO_LOWRESNX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/platform/LibRetro -f Makefile platform=$(LIBRETRO_LOWRESNX_PLATFORM) \
        GIT_VERSION="-$(shell echo $(LIBRETRO_LOWRESNX_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_LOWRESNX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/platform/LibRetro/lowresnx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/lowresnx_libretro.so
endef

$(eval $(generic-package))
