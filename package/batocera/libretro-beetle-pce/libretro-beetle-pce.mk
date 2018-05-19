################################################################################
#
# BEETLE_PCE
#
################################################################################
# Version.: Commits on Apr 24, 2018
LIBRETRO_BEETLE_PCE_VERSION = 11f7aaaf0271ca150e2ad77b21ead59baf327bbe
LIBRETRO_BEETLE_PCE_SITE = $(call github,libretro,beetle-pce-fast-libretro,$(LIBRETRO_BEETLE_PCE_VERSION))


define LIBRETRO_BEETLE_PCE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
	$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" AR="$(TARGET_AR)" RANLIB="$(TARGET_RANLIB)" -C $(@D) platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_BEETLE_PCE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_pce_fast_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pce_libretro.so
endef

$(eval $(generic-package))
