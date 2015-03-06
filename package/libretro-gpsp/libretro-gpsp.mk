################################################################################
#
# GPSP
#
################################################################################
LIBRETRO_GPSP_VERSION = d57f89f3f1cb7730fdaabda0237833ef3235c22c
LIBRETRO_GPSP_SITE = $(call github,libretro,gpsp,$(LIBRETRO_GPSP_VERSION))

define LIBRETRO_GPSP_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_GPSP_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/gpsp_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gpsp_libretro.so
endef

$(eval $(generic-package))
