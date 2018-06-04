################################################################################
#
# THEODORE
#
################################################################################
# Version : Commits on May 28, 2018
LIBRETRO_THEODORE_VERSION = 9998e1cc95446b1d176bb3b70c7de90327652266
LIBRETRO_THEODORE_SITE = $(call github,Zlika,theodore,$(LIBRETRO_THEODORE_VERSION))

define LIBRETRO_THEODORE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_THEODORE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/theodore_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/theodore_libretro.so
endef

$(eval $(generic-package))
