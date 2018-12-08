################################################################################
#
# STELLA
#
################################################################################
# Version.: Commits on Nov 11, 2018
LIBRETRO_STELLA_VERSION = 6a8e20909e0a39a4e01f9102dc935113e38cd62b
LIBRETRO_STELLA_SITE = $(call github,libretro,stella-libretro,$(LIBRETRO_STELLA_VERSION))

define LIBRETRO_STELLA_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
	$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" AR="$(TARGET_AR)" -C $(@D)
endef

define LIBRETRO_STELLA_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/stella_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/stella_libretro.so
endef

$(eval $(generic-package))
