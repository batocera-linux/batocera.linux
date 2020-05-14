################################################################################
#
# GAMBATTE
#
################################################################################
# Version.: Commits on Feb 07, 2020
LIBRETRO_GAMBATTE_VERSION = 132f36e990dfc6effdafa6cf261373432464f9bf
LIBRETRO_GAMBATTE_SITE = $(call github,libretro,gambatte-libretro,$(LIBRETRO_GAMBATTE_VERSION))
LIBRETRO_GAMBATTE_LICENSE = GPLv2

LIBRETRO_GAMBATTE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_GAMBATTE_PLATFORM = classic_armv8_a35
endif

define LIBRETRO_GAMBATTE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="$(LIBRETRO_GAMBATTE_PLATFORM)"
endef

define LIBRETRO_GAMBATTE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/gambatte_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gambatte_libretro.so
endef

$(eval $(generic-package))
