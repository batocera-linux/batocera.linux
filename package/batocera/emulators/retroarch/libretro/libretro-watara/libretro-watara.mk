################################################################################
#
# WATARA
#
################################################################################
# Version.: Commits on Mar 25, 2021
LIBRETRO_WATARA_VERSION = 2873c42f28012992c1132fd083787f5b76b99418
LIBRETRO_WATARA_SITE = $(call github,libretro,potator,$(LIBRETRO_WATARA_VERSION))
LIBRETRO_WATARA_LICENSE = GPLv2

LIBRETRO_WATARA_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_WATARA_EXTRA_ARGS = 

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
    LIBRETRO_WATARA_PLATFORM = rpi1
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
    LIBRETRO_WATARA_PLATFORM = rpi2
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
    LIBRETRO_WATARA_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
    LIBRETRO_WATARA_PLATFORM = rpi4
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
	LIBRETRO_WATARA_PLATFORM = armv cortexa9 neon hardfloat
endif

ifeq ($(BR2_aarch64),y)
	LIBRETRO_WATARA_EXTRA_ARGS += ARCH=arm64
endif

ifeq ($(BR2_x86_64),y)
	LIBRETRO_WATARA_EXTRA_ARGS += ARCH=x86_64
endif

define LIBRETRO_WATARA_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/platform/libretro -f Makefile platform="$(LIBRETRO_WATARA_PLATFORM)" $(LIBRETRO_WATARA_EXTRA_ARGS)
endef

define LIBRETRO_WATARA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/platform/libretro/potator_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/potator_libretro.so
endef

$(eval $(generic-package))
