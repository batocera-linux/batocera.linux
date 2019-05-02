################################################################################
#
# STELLA
#
################################################################################
# Version.: Commits on Feb 4, 2019
LIBRETRO_STELLA_VERSION = b0b63615fc2c7a30470fc1ac31ffdc18fdf4518b
LIBRETRO_STELLA_SITE = $(call github,libretro,stella-libretro,$(LIBRETRO_STELLA_VERSION))
LIBRETRO_STELLA_LICENSE = GPLv2

define LIBRETRO_STELLA_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
	$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" AR="$(TARGET_AR)" -C $(@D)
endef

define LIBRETRO_STELLA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/stella_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/stella_libretro.so
endef

$(eval $(generic-package))
