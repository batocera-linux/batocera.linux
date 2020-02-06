################################################################################
#
# BEETLE_PCFX
#
################################################################################
# Version.: Commits on Oct 30, 2019
LIBRETRO_BEETLE_PCFX_VERSION = 7e9a586d75468098cba25f604f545a4162c2f376
LIBRETRO_BEETLE_PCFX_SITE = $(call github,libretro,beetle-pcfx-libretro,$(LIBRETRO_BEETLE_PCFX_VERSION))
LIBRETRO_BEETLE_PCFX_LICENSE = GPLv2

define LIBRETRO_BEETLE_PCFX_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		LD="$(TARGET_CXX)" AR="$(TARGET_AR)" RANLIB="$(TARGET_RANLIB)" -C $(@D) platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_BEETLE_PCFX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_pcfx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pcfx_libretro.so
endef

$(eval $(generic-package))
