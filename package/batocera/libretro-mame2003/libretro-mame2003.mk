################################################################################
#
# MAME2003
#
################################################################################
# Version.: Commits on May 12, 2018
LIBRETRO_MAME2003_VERSION = 80b83cc3d1340aa1708187e33b568e66f58c9700
LIBRETRO_MAME2003_SITE = $(call github,libretro,mame2003-libretro,$(LIBRETRO_MAME2003_VERSION))



define LIBRETRO_MAME2003_BUILD_CMDS
	mkdir -p $(@D)/obj/mame/cpu/ccpu
	#CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_CC)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/ -f Makefile ARCH="$(TARGET_CFLAGS) -fsigned-char "
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_CC)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"

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
