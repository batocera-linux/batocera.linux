################################################################################
#
# MAME2010
#
################################################################################
LIBRETRO_MAME2010_VERSION = 81c75bb2966a210c26e8fca1c6a2ecf62e7b715a
LIBRETRO_MAME2010_SITE = $(call github,libretro,mame2010-libretro,$(LIBRETRO_MAME2010_VERSION))



define LIBRETRO_MAME2010_BUILD_CMDS
	mkdir -p $(@D)/obj/mame/cpu/ccpu
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_CC)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/ -f Makefile "VRENDER=soft" platform="$(LIBRETRO_PLATFORM)" emulator

endef

define LIBRETRO_MAME2010_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mame2010_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mame0139_libretro.so
endef

$(eval $(generic-package))
