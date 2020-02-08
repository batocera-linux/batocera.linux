################################################################################
#
# BEETLE_PCE
#
################################################################################
# Version.: Commits on Jan 30, 2020
LIBRETRO_BEETLE_PCE_VERSION = 40a42b7f43f029760c92bf0b2097e7d4b90ed29c
LIBRETRO_BEETLE_PCE_SITE = $(call github,libretro,beetle-pce-fast-libretro,$(LIBRETRO_BEETLE_PCE_VERSION))
LIBRETRO_BEETLE_PCE_LICENSE = GPLv2

define LIBRETRO_BEETLE_PCE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		LD="$(TARGET_CXX)" AR="$(TARGET_AR)" RANLIB="$(TARGET_RANLIB)" -C $(@D) platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_BEETLE_PCE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_pce_fast_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pce_libretro.so
endef

$(eval $(generic-package))
