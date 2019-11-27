################################################################################
#
# STELLA
#
################################################################################
# Version.: Commits on Sep 21, 2019
LIBRETRO_STELLA_VERSION = 6d74ad9a0fd779145108cf1213229798d409ed37
LIBRETRO_STELLA_SITE = $(call github,libretro,stella2014-libretro,$(LIBRETRO_STELLA_VERSION))
LIBRETRO_STELLA_LICENSE = GPLv2

define LIBRETRO_STELLA_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
	$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" AR="$(TARGET_AR)" -C $(@D)
endef

define LIBRETRO_STELLA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/stella2014_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/stella_libretro.so
endef

$(eval $(generic-package))
