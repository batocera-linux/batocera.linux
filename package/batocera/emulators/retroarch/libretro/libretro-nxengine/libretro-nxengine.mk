################################################################################
#
# NXENGINE
#
################################################################################
# Version.: Commits on Oct 20, 2020
LIBRETRO_NXENGINE_VERSION = 10c4381f8848fd288e95936c70ffde6db62a82c9
LIBRETRO_NXENGINE_SITE = $(call github,libretro,nxengine-libretro,$(LIBRETRO_NXENGINE_VERSION))
LIBRETRO_NXENGINE_LICENSE = GPLv3

LIBRETRO_NXENGINE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_NXENGINE_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
        LIBRETRO_NXENGINE_PLATFORM = armv
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_NXENGINE_PLATFORM = rpi4_64
else ifeq ($(BR2_aarch64),y)
LIBRETRO_NXENGINE_PLATFORM = unix
endif

define LIBRETRO_NXENGINE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_NXENGINE_PLATFORM)"
endef

define LIBRETRO_NXENGINE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/nxengine_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/nxengine_libretro.so
endef

$(eval $(generic-package))
