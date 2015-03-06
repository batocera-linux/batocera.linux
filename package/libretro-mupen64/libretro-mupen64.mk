################################################################################
#
# MUPEN64
#
################################################################################
LIBRETRO_MUPEN64_VERSION = e0b091c49f967b5b0e7c1c45d5503c8621bc4911
LIBRETRO_MUPEN64_SITE = $(call github,libretro,mupen64plus-libretro,$(LIBRETRO_MUPEN64_VERSION))
LIBRETRO_MUPEN64_DEPENDENCIES = rpi-userland


ifeq ($(BR2_cortex_a7),y)
        LIBRETRO_MUPEN64_PLATFORM=rpi2
else
        LIBRETRO_MUPEN64_PLATFORM=rpi
endif

define LIBRETRO_MUPEN64_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) platform="$(LIBRETRO_MUPEN64_PLATFORM)"
endef

define LIBRETRO_MUPEN64_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mupen64plus_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mupen64plus_libretro.so
endef

$(eval $(generic-package))
