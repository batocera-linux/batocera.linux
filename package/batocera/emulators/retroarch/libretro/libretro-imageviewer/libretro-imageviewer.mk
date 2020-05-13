################################################################################
#
# IMAGEVIEWER
#
################################################################################
LIBRETRO_IMAGEVIEWER_VERSION = 595f163c3594ec7dbd5309e3b298e6a4e5e529fc
LIBRETRO_IMAGEVIEWER_SITE = $(call github,batocera-linux,libretro-imageviewer-legacy,$(LIBRETRO_IMAGEVIEWER_VERSION))

define LIBRETRO_IMAGEVIEWER_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="unix"
endef

define LIBRETRO_IMAGEVIEWER_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/imageviewer_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/imageviewer_libretro.so
endef

$(eval $(generic-package))
