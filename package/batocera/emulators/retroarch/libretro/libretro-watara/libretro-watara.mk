################################################################################
#
# libretro-watara
#
################################################################################
# Version: Commits on May 27, 2023
LIBRETRO_WATARA_VERSION = aed31f9254cada9826c65ff4528cc8bdda338275
LIBRETRO_WATARA_SITE = $(call github,libretro,potator,$(LIBRETRO_WATARA_VERSION))
LIBRETRO_WATARA_LICENSE = GPLv2

LIBRETRO_WATARA_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_WATARA_EXTRA_ARGS =

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_WATARA_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_WATARA_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_WATARA_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_WATARA_PLATFORM = rpi4
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_WATARA_PLATFORM = rpi5
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_WATARA_PLATFORM = armv cortexa9 neon hardfloat
else ifeq ($(BR2_aarch64),y)
LIBRETRO_WATARA_PLATFORM = aarch64
LIBRETRO_WATARA_EXTRA_ARGS += ARCH=arm64
else ifeq ($(BR2_x86_64),y)
LIBRETRO_WATARA_EXTRA_ARGS += ARCH=x86_64
endif

define LIBRETRO_WATARA_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/platform/libretro -f Makefile platform="$(LIBRETRO_WATARA_PLATFORM)" $(LIBRETRO_WATARA_EXTRA_ARGS) \
        GIT_VERSION="-$(shell echo $(LIBRETRO_WATARA_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_WATARA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/platform/libretro/potator_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/potator_libretro.so
endef

$(eval $(generic-package))
