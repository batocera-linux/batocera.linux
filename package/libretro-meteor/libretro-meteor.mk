################################################################################
#
# METEOR
#
################################################################################
LIBRETRO_METEOR_VERSION = 51be4349a178da09a9e376065187237b3c201fe7
LIBRETRO_METEOR_SITE = $(call github,libretro,meteor-libretro,$(LIBRETRO_METEOR_VERSION))


define LIBRETRO_METEOR_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
	$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" AR="$(TARGET_AR)" RANLIB="$(TARGET_RANLIB)" -C $(@D)/libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_METEOR_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro/meteor_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/meteor_libretro.so
endef

$(eval $(generic-package))
