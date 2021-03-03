################################################################################
#
# FMSX
#
################################################################################
# Version.: Commits on Jan 15, 2021
LIBRETRO_FMSX_VERSION = cac8e381f40767e8fe80db4a06fc7ed9b6d21d56
LIBRETRO_FMSX_SITE = $(call github,libretro,fmsx-libretro,$(LIBRETRO_FMSX_VERSION))
LIBRETRO_FMSX_LICENSE = GPLv2

LIBRETRO_FMSX_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_FMSX_EXTRA_ARGS = 


ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
        LIBRETRO_FMSX_PLATFORM = armv cortexa9 neon hardfloat
endif

ifeq ($(BR2_aarch64),y)
	LIBRETRO_FMSX_PLATFORM = unix
	LIBRETRO_FMSX_EXTRA_ARGS += ARCH=arm64
endif

ifeq ($(BR2_x86_64),y)
	LIBRETRO_FMSX_EXTRA_ARGS += ARCH=x86_64
endif

define LIBRETRO_FMSX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_FMSX_PLATFORM)" $(LIBRETRO_FMSX_EXTRA_ARGS)
endef

define LIBRETRO_FMSX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fmsx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fmsx_libretro.so
endef

$(eval $(generic-package))
