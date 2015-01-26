################################################################################
#
# FCEUMM
#
################################################################################
LIBRETRO_FCEUMM_VERSION = master
LIBRETRO_FCEUMM_SITE = $(call github,libretro,libretro-fceumm,master)
#		CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" 

define LIBRETRO_FCEUMM_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile.libretro platform="armv6-hardfloat"
endef

define LIBRETRO_FCEUMM_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fceumm_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fceumm_libretro.so
endef

$(eval $(generic-package))
