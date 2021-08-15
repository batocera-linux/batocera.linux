################################################################################
#
# EMUSCV
#
################################################################################
# Version.: Commits on Apr 24, 2021
LIBRETRO_EMUSCV_VERSION = eb14596d4f3cefef9ed178cf4eea7aca992e18a6
LIBRETRO_EMUSCV_SITE = $(call gitlab,MaaaX-EmuSCV,libretro-emuscv,$(LIBRETRO_EMUSCV_VERSION))
LIBRETRO_EMUSCV_LICENSE = GPLv2

LIBRETRO_EMUSCV_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_EMUSCV_EXTRA_ARGS = 


ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
        LIBRETRO_EMUSCV_PLATFORM = armv cortexa9 neon hardfloat
endif

ifeq ($(BR2_aarch64),y)
	LIBRETRO_EMUSCV_PLATFORM = unix
	LIBRETRO_EMUSCV_EXTRA_ARGS += ARCH=arm64
endif

ifeq ($(BR2_x86_64),y)
	LIBRETRO_EMUSCV_EXTRA_ARGS += ARCH=x86_64
endif

define LIBRETRO_EMUSCV_FIXSDL2_PATH
	sed -i "s+\`sdl2-config+\`$(STAGING_DIR)/usr/bin/sdl2-config+g" $(@D)/Makefile.libretro
endef

LIBRETRO_EMUSCV_PRE_CONFIGURE_HOOKS += LIBRETRO_EMUSCV_FIXSDL2_PATH

define LIBRETRO_EMUSCV_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_EMUSCV_PLATFORM)" $(LIBRETRO_EMUSCV_EXTRA_ARGS)
endef

define LIBRETRO_EMUSCV_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/emuscv_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/emuscv_libretro.so
endef

$(eval $(generic-package))
