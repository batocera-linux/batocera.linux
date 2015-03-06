################################################################################
#
# FCEUNEXT
#
################################################################################
LIBRETRO_FCEUNEXT_VERSION = 1b3d4d72e658b2a32a20e31b87007d10e9061d13
LIBRETRO_FCEUNEXT_SITE = $(call github,libretro,fceu-next,$(LIBRETRO_FCEUNEXT_VERSION))

define LIBRETRO_FCEUNEXT_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/fceumm-code -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_FCEUNEXT_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fceumm-code/fceumm_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fceunext_libretro.so
endef

$(eval $(generic-package))
