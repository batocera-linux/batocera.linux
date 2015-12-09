################################################################################
#
# UAE
#
################################################################################
LIBRETRO_UAE_VERSION = 7cbc2304d064cf58455bc4bdf589cb3fd51865a8
LIBRETRO_UAE_SITE = $(call github,libretro,libretro-uae,master)

define LIBRETRO_UAE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" LDFLAGS="$(TARGET_LDFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="rpi"
endef

define LIBRETRO_UAE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/puae_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/puae_libretro.so
endef

$(eval $(generic-package))
