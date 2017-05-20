################################################################################
#
# LIBRETRO_BEETLE_PSX
#
################################################################################
LIBRETRO_BEETLE_PSX_VERSION = 76862abefdde9097561e2b795e75b49247deff17
LIBRETRO_BEETLE_PSX_SITE = $(call github,libretro,beetle-psx-libretro,$(LIBRETRO_BEETLE_PSX_VERSION))

define LIBRETRO_BEETLE_PSX_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" AR="$(TARGET_AR)" -C $(@D) -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_BEETLE_PSX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_psx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mednafen_psx_libretro.so
endef

$(eval $(generic-package))
