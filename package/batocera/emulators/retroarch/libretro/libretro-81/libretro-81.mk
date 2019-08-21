################################################################################
#
# ZX81
#
################################################################################
# Version.: Commits on Nov 18, 2018
LIBRETRO_81_VERSION = 7900d647e084edb71ab587bbf34fe8cb83d28bff
LIBRETRO_81_SITE = $(call github,libretro,81-libretro,$(LIBRETRO_81_VERSION))
LIBRETRO_81_LICENSE = GPLv3

define LIBRETRO_81_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_81_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/81_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/81_libretro.so
endef

$(eval $(generic-package))
