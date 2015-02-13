################################################################################
#
# GAMBATTE
#
################################################################################
LIBRETRO_GAMBATTE_VERSION = master
LIBRETRO_GAMBATTE_SITE = $(call github,libretro,gambatte-libretro,master)

define LIBRETRO_GAMBATTE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/libgambatte/ -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_GAMBATTE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libgambatte/gambatte_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gambatte_libretro.so
endef

$(eval $(generic-package))
