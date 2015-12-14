################################################################################
#
# IMAGEVIEWER
#
################################################################################
LIBRETRO_IMAGEVIEWER_VERSION = ae1465c610ef301c1fe51b32aa9c7ee8f2b59022
LIBRETRO_IMAGEVIEWER_SITE = $(call github,libretro,imageviewer-libretro,$(LIBRETRO_IMAGEVIEWER_VERSION))

define LIBRETRO_IMAGEVIEWER_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_IMAGEVIEWER_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/imageviewer_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/imageviewer_libretro.so
endef

$(eval $(generic-package))
