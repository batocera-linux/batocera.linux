################################################################################
#
# libretro-superbroswar
#
################################################################################
# Version: Commits on Sep 1, 2026
LIBRETRO_SUPERBROSWAR_VERSION = 7f94e03163e1641ecd2a5703eb9ca7e1312b5e8d
LIBRETRO_SUPERBROSWAR_SITE = https://github.com/libretro/superbroswar-libretro.git
LIBRETRO_SUPERBROSWAR_SITE_METHOD = git
LIBRETRO_SUPERBROSWAR_LICENSE = GPLv3
LIBRETRO_SUPERBROSWAR_GIT_SUBMODULES = YES
LIBRETRO_SUPERBROSWAR_DEPENDENCIES += retroarch
LIBRETRO_SUPERBROSWAR_EMULATOR_INFO = superbroswar.libretro.core.yml

LIBRETRO_SUPERBROSWAR_CONF_ENV += LDFLAGS="-fPIC" CFLAGS="-fPIC" CXX_FLAGS="-fPIC"

# Workaround GCC 14 strictness
LIBRETRO_SUPERBROSWAR_CFLAGS = $(TARGET_CFLAGS) -Wno-error=incompatible-pointer-types

define LIBRETRO_SUPERBROSWAR_BUILD_CMDS
    $(TARGET_CONFIGURE_OPTS) CFLAGS="$(LIBRETRO_SUPERBROSWAR_CFLAGS)" $(MAKE) \
	    -C $(@D)/ -I $(@D)/dependencies -f Makefile.libretro platform="unix"
endef

define LIBRETRO_SUPERBROSWAR_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/superbroswar_libretro.so \
	$(TARGET_DIR)/usr/lib/libretro/superbroswar_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
