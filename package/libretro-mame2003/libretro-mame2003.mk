################################################################################
#
# MAME2003
#
################################################################################
#LIBRETRO_MAME2003_VERSION = 3ddeba45f648293a4b860f3283762e8a30c34903
LIBRETRO_MAME2003_VERSION = ae84f5d45fa6ff4beded68cfd19a4217f595703c
LIBRETRO_MAME2003_SITE = $(call github,libretro,mame2003-libretro,$(LIBRETRO_MAME2003_VERSION))



define LIBRETRO_MAME2003_BUILD_CMDS
	mkdir -p $(@D)/obj/mame/cpu/ccpu
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_CC)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/ -f Makefile ARCH="$(TARGET_CFLAGS) -fsigned-char"

endef

define LIBRETRO_MAME2003_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mame2003_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mame078_libretro.so
endef

define LIBRETRO_MAME2003_NAMCO_QUICK_FIX
        $(SED) 's|O3|O2|g' $(@D)/Makefile
        $(SED) 's|to continue|on Keyboard, or Left, Right on Joystick to continue|g' $(@D)/src/ui_text.c 
endef

LIBRETRO_MAME2003_PRE_BUILD_HOOKS += LIBRETRO_MAME2003_NAMCO_QUICK_FIX

$(eval $(generic-package))
