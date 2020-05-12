################################################################################
#
# LIBRETRO-VICE
#
################################################################################
# Version.: Commits on Apr 30, 2020
LIBRETRO_VICE_VERSION = a0112ff3cf8733b4402d3f4be295fbfb23d08290
LIBRETRO_VICE_SITE = $(call github,libretro,vice-libretro,$(LIBRETRO_VICE_VERSION))
LIBRETRO_VICE_LICENSE = GPLv2

define LIBRETRO_VICE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_VICE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/vice_*_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/vice_libretro.so
endef

$(eval $(generic-package))
