################################################################################
#
# UAE
#
################################################################################
LIBRETRO_UAE_VERSION = master
LIBRETRO_UAE_SITE = $(call github,libretro,libretro-uae,master)

define LIBRETRO_UAE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" LDFLAGS="$(TARGET_LDFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/build/ -f Makefile platform="armv7-neon-hardfloat"
endef

define LIBRETRO_UAE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/puae_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/puae_libretro.so
endef

$(eval $(generic-package))
