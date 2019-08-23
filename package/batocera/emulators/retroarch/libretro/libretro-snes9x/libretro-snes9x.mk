################################################################################
#
# SNES9X
#
################################################################################
# Version.: Commits on Aug 23, 2019
LIBRETRO_SNES9X_VERSION = bd9eca377303448ebf4ed7b5c157a4e2dd605346
LIBRETRO_SNES9X_SITE = $(call github,snes9xgit,snes9x,$(LIBRETRO_SNES9X_VERSION))
LIBRETRO_SNES9X_LICENSE = Non-commercial

define LIBRETRO_SNES9X_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		-C $(@D)/libretro -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_SNES9X_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro/snes9x_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/snes9x_libretro.so
endef

$(eval $(generic-package))
