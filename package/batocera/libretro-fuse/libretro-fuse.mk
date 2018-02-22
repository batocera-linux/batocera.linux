################################################################################
#
# FUSE
#
################################################################################
LIBRETRO_FUSE_VERSION = 58ec13fe80c0aa2172d0fede9368c07dc42a107e
LIBRETRO_FUSE_SITE = $(call github,libretro,fuse-libretro,$(LIBRETRO_FUSE_VERSION))

define LIBRETRO_FUSE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" LDFLAGS="$(TARGET_LDFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro
endef

define LIBRETRO_FUSE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fuse_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fuse_libretro.so
endef

$(eval $(generic-package))
