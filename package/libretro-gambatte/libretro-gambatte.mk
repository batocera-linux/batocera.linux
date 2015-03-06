################################################################################
#
# GAMBATTE
#
################################################################################
LIBRETRO_GAMBATTE_VERSION = e6a77e0b9ca8408f28c179cf6e0c07e671024588
LIBRETRO_GAMBATTE_SITE = $(call github,libretro,gambatte-libretro,$(LIBRETRO_GAMBATTE_VERSION))

define LIBRETRO_GAMBATTE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/libgambatte/ -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_GAMBATTE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libgambatte/gambatte_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gambatte_libretro.so
endef

$(eval $(generic-package))
