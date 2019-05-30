################################################################################
#
# MAME2003
#
################################################################################
# Version.: Commits on Apr 26, 2019
LIBRETRO_MAME2003_VERSION = 9d38610d536253b6df0836b38bcfe2fb4e138ecb
LIBRETRO_MAME2003_SITE = $(call github,libretro,mame2003-libretro,$(LIBRETRO_MAME2003_VERSION))
LIBRETRO_MAME2003_LICENSE = MAME

define LIBRETRO_MAME2003_BUILD_CMDS
	mkdir -p $(@D)/obj/mame/cpu/ccpu
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_CC)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_MAME2003_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mame2003_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mame078_libretro.so

	# Bios
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/mame2003/samples
	$(INSTALL) -D $(@D)/metadata/* \
		$(TARGET_DIR)/usr/share/batocera/datainit/bios/mame2003
endef

define LIBRETRO_MAME2003_NAMCO_QUICK_FIX
        $(SED) 's|O3|O2|g' $(@D)/Makefile
        $(SED) 's|to continue|on Keyboard, or Left, Right on Joystick to continue|g' $(@D)/src/ui_text.c 
endef

LIBRETRO_MAME2003_PRE_BUILD_HOOKS += LIBRETRO_MAME2003_NAMCO_QUICK_FIX

$(eval $(generic-package))
