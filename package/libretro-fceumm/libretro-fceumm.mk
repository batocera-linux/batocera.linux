################################################################################
#
# FCEUMM
#
################################################################################
LIBRETRO_FCEUMM_VERSION = 19054984ff26aefa6b405661565c95a5c11c56a4
LIBRETRO_FCEUMM_SITE = $(call github,libretro,libretro-fceumm,$(LIBRETRO_FCEUMM_VERSION))

define LIBRETRO_FCEUMM_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_FCEUMM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fceumm_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fceumm_libretro.so
endef

$(eval $(generic-package))
