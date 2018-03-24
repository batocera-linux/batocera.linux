################################################################################
#
# VIRTUALJAGUAR
#
################################################################################
LIBRETRO_VIRTUALJAGUAR_VERSION = 48739c26741cf4b18ae43542a401bdb2078ad563
LIBRETRO_VIRTUALJAGUAR_SITE = $(call github,libretro,virtualjaguar-libretro,$(LIBRETRO_VIRTUALJAGUAR_VERSION))

define LIBRETRO_VIRTUALJAGUAR_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)
endef

define LIBRETRO_VIRTUALJAGUAR_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/virtualjaguar_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/virtualjaguar_libretro.so
endef

$(eval $(generic-package))
