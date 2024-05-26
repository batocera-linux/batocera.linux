################################################################################
#
# libretro-desmume
#
################################################################################
# Version: Commits on Jan 11, 2024
LIBRETRO_DESMUME_VERSION = b518fec54b79f2f71a7536715efcdcd7f60638a8
LIBRETRO_DESMUME_SITE = $(call github,libretro,desmume,$(LIBRETRO_DESMUME_VERSION))
LIBRETRO_DESMUME_LICENSE = GPLv2
LIBRETRO_DESMUME_DEPENDENCIES = libpcap

define LIBRETRO_DESMUME_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/desmume/src/frontend/libretro \
		-f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_DESMUME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/desmume/src/frontend/libretro/desmume_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/desmume_libretro.so
endef

$(eval $(generic-package))
