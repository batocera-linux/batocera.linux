################################################################################
#
# MUPEN64
#
################################################################################
LIBRETRO_MUPEN64_VERSION = master
LIBRETRO_MUPEN64_SITE = $(call github,libretro,mupen64plus-libretro,master)
LIBRETRO_MUPEN64_DEPENDENCIES = rpi-userland

define LIBRETRO_MUPEN64_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) platform="$(LIBRETRO_PLATFORM) gles"
endef

define LIBRETRO_MUPEN64_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mupen64plus_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mupen64plus_libretro.so
endef

$(eval $(generic-package))
