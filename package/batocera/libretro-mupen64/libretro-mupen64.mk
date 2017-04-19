################################################################################
#
# MUPEN64
#
################################################################################
#LIBRETRO_MUPEN64_VERSION = 53c38fefaf51d5c18af23f9eaceab32e80c4034c
#LIBRETRO_MUPEN64_SITE = $(call github,libretro,mupen64plus-libretro,$(LIBRETRO_MUPEN64_VERSION))
##LIBRETRO_MUPEN64_VERSION = bd444b70a522a56e3cbc72a295d38325ddc35232
##LIBRETRO_MUPEN64_SITE = $(call github,rockaddicted,mupen64plus-libretro,$(LIBRETRO_MUPEN64_VERSION))
LIBRETRO_MUPEN64_VERSION = a72d5c0b5a8f1a4700ebf7727fa50b8e52a373d8
LIBRETRO_MUPEN64_SITE = $(call github,gizmo98,mupen64plus-libretro,$(LIBRETRO_MUPEN64_VERSION))
LIBRETRO_MUPEN64_DEPENDENCIES = rpi-userland


ifeq ($(BR2_cortex_a7),y)
        LIBRETRO_MUPEN64_PLATFORM=rpi2
else
        LIBRETRO_MUPEN64_PLATFORM=rpi
endif

define LIBRETRO_MUPEN64_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_MUPEN64_PLATFORM)" WITH_DYNAREC=arm
endef

define LIBRETRO_MUPEN64_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mupen64plus_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mupen64plus_libretro.so
endef

$(eval $(generic-package))
