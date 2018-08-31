################################################################################
#
# VECX
#
################################################################################
# Version.: Commits on Aug 12, 2018
LIBRETRO_VECX_VERSION = 7c16fe2eaff5c0538df2ce63467ff7111b49d56b
LIBRETRO_VECX_SITE = $(call github,libretro,libretro-vecx,$(LIBRETRO_VECX_VERSION))

define LIBRETRO_VECX_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_VECX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/vecx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/vecx_libretro.so
endef

$(eval $(generic-package))
