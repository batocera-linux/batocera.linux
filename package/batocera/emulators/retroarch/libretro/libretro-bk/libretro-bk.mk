################################################################################
#
# libretro-bk
#
################################################################################
# Version: Commits on Jan 25, 2026
LIBRETRO_BK_VERSION = f95d929c8eca6c85075cd5c56a08aac9c58f3802
LIBRETRO_BK_SITE = $(call github,libretro,bk-emulator,$(LIBRETRO_BK_VERSION))
LIBRETRO_BK_LICENSE = Non-commercial
LIBRETRO_BK_DEPENDENCIES = retroarch

LIBRETRO_BK_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_BK_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_BK_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_BK_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_BK_PLATFORM = rpi4_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_BK_PLATFORM = rpi5_64
endif

define LIBRETRO_BK_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) \
	    -f Makefile.libretro platform="$(LIBRETRO_BK_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_BK_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_BK_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bk_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bk_libretro.so
endef

$(eval $(generic-package))
