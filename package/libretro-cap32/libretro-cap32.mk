################################################################################
#
# CAP32
#
################################################################################
LIBRETRO_CAP32_VERSION = 7036672b930b17ea35effc13bbc867c85cd430de
LIBRETRO_CAP32_SITE = $(call github,libretro,libretro-cap32,$(LIBRETRO_CAP32_VERSION))

define LIBRETRO_CAP32_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" LDFLAGS="$(TARGET_LDFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile
endef

define LIBRETRO_CAP32_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/cap32_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/cap32_libretro.so
endef

$(eval $(generic-package))
