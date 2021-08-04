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

define LIBRETRO_XMIL_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/libretro -f Makefile platform="unix"
endef

define LIBRETRO_XMIL_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro/x1_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/x1_libretro.so
endef

$(eval $(generic-package))
