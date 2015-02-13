################################################################################
#
# FCEUNEXT
#
################################################################################
LIBRETRO_FCEUNEXT_VERSION = master
LIBRETRO_FCEUNEXT_SITE = $(call github,libretro,fceu-next,master)

define LIBRETRO_FCEUNEXT_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/fceumm-code -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_FCEUNEXT_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fceumm-code/fceumm_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fceunext_libretro.so
endef

$(eval $(generic-package))
