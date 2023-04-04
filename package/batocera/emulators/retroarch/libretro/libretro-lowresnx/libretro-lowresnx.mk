################################################################################
#
# libretro-lowresnx
#
################################################################################
# Version: Commits on Mar 23, 2023
LIBRETRO_LOWRESNX_VERSION = 10a48e309ac5284724010eea56372fbc72b9f975
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
endif

LOWRESNX_CONFIGURE_OPTS = GIT_DISCOVERY_ACROSS_FILESYSTEM=1 platform=$(LIBRETRO_LOWRESNX_PLATFORM)

define LIBRETRO_LOWRESNX_BUILD_CMDS
	$(LOWRESNS_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/platform/LibRetro -f Makefile \
        GIT_VERSION="-$(shell echo $(LIBRETRO_LOWRESNX_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_LOWRESNX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/platform/LibRetro/lowresnx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/lowresnx_libretro.so
endef

$(eval $(generic-package))
