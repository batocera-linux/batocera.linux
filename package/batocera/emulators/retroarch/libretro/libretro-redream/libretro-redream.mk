################################################################################
#
# REDREAM
#
################################################################################
# Version.: Commits on Apr 18, 2018
LIBRETRO_REDREAM_VERSION = ffb7302245ff40515cb9f0f0b0e233a4b39342d3
LIBRETRO_REDREAM_SITE = $(call github,inolen,redream,$(LIBRETRO_REDREAM_VERSION))
LIBRETRO_REDREAM_LICENSE="MIT"

define LIBRETRO_REDREAM_BUILD_CMDS
        CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" \
		CC="$(TARGET_CC)" AR="$(TARGET_AR)" -C $(@D)/deps/libretro/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_REDREAM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/deps/libretro/redream_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/redream_libretro.so
endef

$(eval $(generic-package))
