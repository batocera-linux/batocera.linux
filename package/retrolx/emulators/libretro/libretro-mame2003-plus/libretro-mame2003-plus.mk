################################################################################
#
# MAME2003 PLUS
#
################################################################################
# Version.: Commits on July 05, 2021
LIBRETRO_MAME2003_PLUS_VERSION = 4cd65b604b52f3b622e7b45519f476526b2b39ce
LIBRETRO_MAME2003_PLUS_SITE = $(call github,libretro,mame2003-plus-libretro,$(LIBRETRO_MAME2003_PLUS_VERSION))
LIBRETRO_MAME2003_PLUS_LICENSE = MAME

LIBRETRO_MAME2003_PLUS_PLATFORM = $(LIBRETRO_PLATFORM)

LIBRETRO_MAME2003_PLUS_PKG_DIR = $(TARGET_DIR)/opt/retrolx/libretro
LIBRETRO_MAME2003_PLUS_PKG_INSTALL_DIR = /userdata/packages/$(BATOCERA_SYSTEM_ARCH)/lr-mame2003-plus

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
LIBRETRO_MAME2003_PLUS_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_MAME2003_PLUS_PLATFORM = rpi4_64
else ifeq ($(BR2_aarch64),y)
LIBRETRO_MAME2003_PLUS_PLATFORM = unix
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
    LIBRETRO_MAME2003_PLUS_PLATFORM = s812
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_PC),y)
    LIBRETRO_MAME2003_PLUS_PLATFORM = rpi2
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_CHA),y)
    LIBRETRO_MAME2003_PLUS_PLATFORM = rpi2
endif

define LIBRETRO_MAME2003_PLUS_BUILD_CMDS
	mkdir -p $(@D)/obj/mame/cpu/ccpu
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_MAME2003_PLUS_PLATFORM)"
endef

define LIBRETRO_MAME2003_PLUS_INSTALL_TARGET_CMDS
endef

define LIBRETRO_MAME2003_PLUS_NAMCO_QUICK_FIX
	$(SED) 's|O3|O2|g' $(@D)/Makefile
	$(SED) 's|to continue|on Keyboard, or Left, Right on Joystick to continue|g' $(@D)/src/ui_text.c
endef

define LIBRETRO_MAME2003_PLUS_MAKEPKG
	# Create directories
	mkdir -p $(LIBRETRO_MAME2003_PLUS_PKG_DIR)$(LIBRETRO_MAME2003_PLUS_PKG_INSTALL_DIR)/bios/samples

	# Copy package files
	cp -pr $(@D)/mame2003_plus_libretro.so $(LIBRETRO_MAME2003_PLUS_PKG_DIR)$(LIBRETRO_MAME2003_PLUS_PKG_INSTALL_DIR)
	cp -pr $(@D)/metadata/* $(LIBRETRO_MAME2003_PLUS_PKG_DIR)$(LIBRETRO_MAME2003_PLUS_PKG_INSTALL_DIR)/bios/

	# Build Pacman package
	cd $(LIBRETRO_MAME2003_PLUS_PKG_DIR) && $(BR2_EXTERNAL_BATOCERA_PATH)/scripts/retrolx-makepkg \
	$(BR2_EXTERNAL_BATOCERA_PATH)/package/retrolx/emulators/libretro/libretro-mame2003-plus/PKGINFO \
	$(BATOCERA_SYSTEM_ARCH) $(HOST_DIR)
	mv $(TARGET_DIR)/opt/retrolx/*.zst $(BR2_EXTERNAL_BATOCERA_PATH)/repo/$(BATOCERA_SYSTEM_ARCH)/

	# Cleanup
	rm -Rf $(TARGET_DIR)/opt/retrolx/*
endef

LIBRETRO_MAME2003_PLUS_PRE_BUILD_HOOKS += LIBRETRO_MAME2003_PLUS_NAMCO_QUICK_FIX
LIBRETRO_MAME2003_PLUS_POST_INSTALL_TARGET_HOOKS = LIBRETRO_MAME2003_PLUS_MAKEPKG
$(eval $(generic-package))
