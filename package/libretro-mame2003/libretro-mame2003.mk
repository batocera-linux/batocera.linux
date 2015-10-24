################################################################################
#
# MAME2003
#
################################################################################
LIBRETRO_MAME2003_VERSION = 3ddeba45f648293a4b860f3283762e8a30c34903
LIBRETRO_MAME2003_SITE = $(call github,libretro,mame2003-libretro,$(LIBRETRO_MAME2003_VERSION))



define LIBRETRO_MAME2003_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/ -f Makefile

endef

define LIBRETRO_MAME2003_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mame078_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mame078_libretro.so
endef

$(eval $(generic-package))
