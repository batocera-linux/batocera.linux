################################################################################
#
# GAMBATTE
#
################################################################################
# Version.: Commits on Jan 13, 2021
LIBRETRO_GAMBATTE_VERSION = 2960cc981e42ed717d2209e68c32d7fad5c02e38
LIBRETRO_GAMBATTE_SITE = $(call github,libretro,gambatte-libretro,$(LIBRETRO_GAMBATTE_VERSION))
LIBRETRO_GAMBATTE_LICENSE = GPLv2

LIBRETRO_GAMBATTE_PLATFORM = $(LIBRETRO_PLATFORM)

define LIBRETRO_GAMBATTE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="$(LIBRETRO_GAMBATTE_PLATFORM)"
endef

define LIBRETRO_GAMBATTE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/gambatte_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gambatte_libretro.so
endef

$(eval $(generic-package))
