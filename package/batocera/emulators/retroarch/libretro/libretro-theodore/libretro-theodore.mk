################################################################################
#
# LIBRETRO THEODORE
#
################################################################################
# Version.: Commits on Jan 9, 2020
LIBRETRO_THEODORE_VERSION = d74a2c7a6bc7d6ee5f8226ffd6873b8ec0144268
LIBRETRO_THEODORE_SITE = $(call github,Zlika,theodore,$(LIBRETRO_THEODORE_VERSION))
LIBRETRO_THEODORE_LICENSE = GPLv3

define LIBRETRO_THEODORE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		-C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_THEODORE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/theodore_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/theodore_libretro.so
endef

$(eval $(generic-package))
