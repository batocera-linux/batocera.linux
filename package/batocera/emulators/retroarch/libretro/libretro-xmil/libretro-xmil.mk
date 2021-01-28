################################################################################
#
# xmil - Sharp X1 emulator
#
################################################################################
# Version.: Commits on Jan 8, 2021
LIBRETRO_XMIL_VERSION = ceb72fc953207cb9f83a0862b76f2d7f40c84974
LIBRETRO_XMIL_SITE_METHOD=git
LIBRETRO_XMIL_SITE=https://github.com/libretro/xmil-libretro
LIBRETRO_XMIL_GIT_SUBMODULES=YES
LIBRETRO_XMIL_LICENSE = BSD-3

LIBRETRO_XMIL_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
        LIBRETRO_XMIL_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
        LIBRETRO_XMIL_PLATFORM = classic_armv8_a35
endif

LIBRETRO_XMIL_COMP_PLATFORM = unix

define LIBRETRO_XMIL_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/libretro -f Makefile platform="$(LIBRETRO_XMIL_COMP_PLATFORM)"
endef

define LIBRETRO_XMIL_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro/x1_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/x1_libretro.so
endef

$(eval $(generic-package))
