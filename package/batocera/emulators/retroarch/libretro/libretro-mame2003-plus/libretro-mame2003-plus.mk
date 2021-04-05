################################################################################
#
# MAME2003 PLUS
#
################################################################################
# Version.: Commits on Apr 04, 2021
LIBRETRO_MAME2003_PLUS_VERSION = 1eeb9c935ca710bcbe2af951bd2936dae625ffa4
LIBRETRO_MAME2003_PLUS_SITE = $(call github,libretro,mame2003-plus-libretro,$(LIBRETRO_MAME2003_PLUS_VERSION))
LIBRETRO_MAME2003_PLUS_LICENSE = MAME

LIBRETRO_MAME2003_PLUS_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_MAME2003_PLUS_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_MAME2003_PLUS_PLATFORM = rpi4_64
else ifeq ($(BR2_aarch64),y)
LIBRETRO_MAME2003_PLUS_PLATFORM = unix
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
    LIBRETRO_MAME2003_PLUS_PLATFORM = s812
endif

define LIBRETRO_MAME2003_PLUS_BUILD_CMDS
	mkdir -p $(@D)/obj/mame/cpu/ccpu
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_MAME2003_PLUS_PLATFORM)"
endef

define LIBRETRO_MAME2003_PLUS_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mame2003_plus_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mame078plus_libretro.so

	# Bios
    # Need to think of another way to use these files.
    # They take up a lot of space on tmpfs.
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/mame2003-plus/samples
	cp -r $(@D)/metadata/* \
		$(TARGET_DIR)/usr/share/batocera/datainit/bios/mame2003-plus
endef

define LIBRETRO_MAME2003_PLUS_NAMCO_QUICK_FIX
	$(SED) 's|O3|O2|g' $(@D)/Makefile
	$(SED) 's|to continue|on Keyboard, or Left, Right on Joystick to continue|g' $(@D)/src/ui_text.c 
endef

LIBRETRO_MAME2003_PLUS_PRE_BUILD_HOOKS += LIBRETRO_MAME2003_PLUS_NAMCO_QUICK_FIX

$(eval $(generic-package))
