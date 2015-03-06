################################################################################
#
# BEETLE_PCE
#
################################################################################
LIBRETRO_BEETLE_PCE_VERSION = 6f5a52d9813b819d9f6a9b86b74d6aa3b93a2576
LIBRETRO_BEETLE_PCE_SITE = $(call github,libretro,beetle-pce-fast-libretro,$(LIBRETRO_BEETLE_PCE_VERSION))


define LIBRETRO_BEETLE_PCE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
	$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" AR="$(TARGET_AR)" RANLIB="$(TARGET_RANLIB)" -C $(@D) platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_BEETLE_PCE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_pce_fast_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pce_libretro.so
endef

$(eval $(generic-package))
