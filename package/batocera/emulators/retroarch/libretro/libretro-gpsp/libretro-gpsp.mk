################################################################################
#
# GPSP
#
################################################################################
# Version.: Commits on Aug 12, 2018
LIBRETRO_GPSP_VERSION = d99f3ac9f1da201b6a0a3f90739503644dce1645
LIBRETRO_GPSP_SITE = $(call github,libretro,gpsp,$(LIBRETRO_GPSP_VERSION))

define LIBRETRO_GPSP_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_GPSP_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/gpsp_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gpsp_libretro.so
endef

$(eval $(generic-package))
