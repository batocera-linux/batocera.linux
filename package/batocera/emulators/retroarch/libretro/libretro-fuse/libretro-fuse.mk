################################################################################
#
# FUSE
#
################################################################################
# Version.: Commits on Feb 07, 2020
LIBRETRO_FUSE_VERSION = ef603d165914afc3f54971d082e69adea187c8ec
LIBRETRO_FUSE_SITE = $(call github,libretro,fuse-libretro,$(LIBRETRO_FUSE_VERSION))
LIBRETRO_FUSE_LICENSE = GPLv3

define LIBRETRO_FUSE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" LDFLAGS="$(TARGET_LDFLAGS)" $(MAKE) \
		CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro
endef

define LIBRETRO_FUSE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fuse_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fuse_libretro.so
endef

$(eval $(generic-package))
