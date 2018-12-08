################################################################################
#
# PX68K
#
################################################################################
# Version.: Commits on Nov 30, 2018
LIBRETRO_PX68K_VERSION = 8c236cd1d890f3aa74ac79c6274327948d34a057
LIBRETRO_PX68K_SITE = $(call github,libretro,px68k-libretro,$(LIBRETRO_PX68K_VERSION))

define LIBRETRO_PX68K_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_PX68K_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/px68k_libretro.so \
	  $(TARGET_DIR)/usr/lib/libretro/px68k_libretro.so
endef

$(eval $(generic-package))
