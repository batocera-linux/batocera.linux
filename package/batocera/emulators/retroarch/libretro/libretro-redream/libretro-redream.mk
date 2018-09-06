################################################################################
#
# REDREAM
#
################################################################################
# Version.: Commits on Jul 27, 2018
LIBRETRO_REDREAM_VERSION = 3dfea38c8200152e53a228df9bc5c2d0dc146516
LIBRETRO_REDREAM_SITE = $(call github,libretro,redream,$(LIBRETRO_REDREAM_VERSION))

define LIBRETRO_REDREAM_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" \
		CC="$(TARGET_CC)" AR="$(TARGET_AR)" -C $(@D)/deps/libretro/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_REDREAM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/deps/libretro/redream_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/redream_libretro.so
endef

$(eval $(generic-package))
