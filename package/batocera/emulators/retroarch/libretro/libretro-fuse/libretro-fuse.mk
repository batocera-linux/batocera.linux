################################################################################
#
# FUSE
#
################################################################################
# Version.: Commits on Aug 12, 2018
LIBRETRO_FUSE_VERSION = 411487a48a158e2c352ba077bd7f00ee1132a3d3
LIBRETRO_FUSE_SITE = $(call github,libretro,fuse-libretro,$(LIBRETRO_FUSE_VERSION))

define LIBRETRO_FUSE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" LDFLAGS="$(TARGET_LDFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro
endef

define LIBRETRO_FUSE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fuse_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fuse_libretro.so
endef

$(eval $(generic-package))
