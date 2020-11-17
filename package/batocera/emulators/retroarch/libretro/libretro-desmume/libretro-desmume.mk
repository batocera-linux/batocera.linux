################################################################################
#
# DESMUME
#
################################################################################
# Version.: Commits on Oct 09, 2020
LIBRETRO_DESMUME_VERSION = d9923420d55e8bda61aaa15cb003b498375a2cb6
LIBRETRO_DESMUME_SITE = $(call github,libretro,desmume,$(LIBRETRO_DESMUME_VERSION))
LIBRETRO_DESMUME_LICENSE = GPLv2
LIBRETRO_DESMUME_DEPENDENCIES = libpcap

define LIBRETRO_DESMUME_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/desmume/src/frontend/libretro -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_DESMUME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/desmume/src/frontend/libretro/desmume_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/desmume_libretro.so
endef

$(eval $(generic-package))
