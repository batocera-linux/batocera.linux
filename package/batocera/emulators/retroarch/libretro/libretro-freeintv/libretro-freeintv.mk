################################################################################
#
# LIBRETRO_FREEINTV
#
################################################################################
# Version.: Commits on Nov 11, 2018
LIBRETRO_FREEINTV_VERSION = cc72320d81b1352e452ad79b671fc83b87fc67a9
LIBRETRO_FREEINTV_SITE = $(call github,libretro,freeintv,$(LIBRETRO_FREEINTV_VERSION))

define LIBRETRO_FREEINTV_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D) -f Makefile platform="unix"
endef

define LIBRETRO_FREEINTV_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/freeintv_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/freeintv_libretro.so
endef

$(eval $(generic-package))
