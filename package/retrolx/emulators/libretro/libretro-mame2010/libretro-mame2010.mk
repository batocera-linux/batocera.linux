################################################################################
#
# MAME2010
#
################################################################################
# Version.: Commits on Apr 12, 2021
LIBRETRO_MAME2010_VERSION = 932e6f2c4f13b67b29ab33428a4037dee9a236a8
LIBRETRO_MAME2010_SITE = $(call github,libretro,mame2010-libretro,$(LIBRETRO_MAME2010_VERSION))
LIBRETRO_MAME2010_LICENSE = MAME

LIBRETRO_MAME2010_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_MAME2010_EXTRA_ARGS = VRENDER=soft emulator

LIBRETRO_MAME2010_PKG_DIR = $(TARGET_DIR)/opt/retrolx/libretro
LIBRETRO_MAME2010_PKG_INSTALL_DIR = /userdata/packages/$(BATOCERA_SYSTEM_ARCH)/lr-mame2010

ifeq ($(BR2_x86_64),y)
LIBRETRO_MAME2010_EXTRA_ARGS += PTR64=1 ARM_ENABLED=0 LCPU=x86_64

else ifeq ($(BR2_x86_i686),y)
LIBRETRO_MAME2010_EXTRA_ARGS += PTR64=0 ARM_ENABLED=0 LCPU=x86

else ifeq ($(BR2_arm),y)
LIBRETRO_MAME2010_EXTRA_ARGS += PTR64=0 ARM_ENABLED=1 LCPU=arm

else ifeq ($(BR2_aarch64),y)
LIBRETRO_MAME2010_PLATFORM = unix
LIBRETRO_MAME2010_EXTRA_ARGS += PTR64=1 ARM_ENABLED=1 LCPU=arm64
endif

define LIBRETRO_MAME2010_BUILD_CMDS
	mkdir -p $(@D)/obj/mame/cpu/ccpu
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_MAME2010_PLATFORM)" $(LIBRETRO_MAME2010_EXTRA_ARGS)
endef

define LIBRETRO_MAME2010_INSTALL_TARGET_CMDS
endef

define LIBRETRO_MAME2010_MAKEPKG
	# Create directories
	mkdir -p $(LIBRETRO_MAME2010_PKG_DIR)$(LIBRETRO_MAME2010_PKG_INSTALL_DIR)/bios/samples

	# Copy package files
	cp -pr $(@D)/mame2010_libretro.so $(LIBRETRO_MAME2010_PKG_DIR)$(LIBRETRO_MAME2010_PKG_INSTALL_DIR)
	$(INSTALL) -D $(@D)/metadata/* $(LIBRETRO_MAME2010_PKG_DIR)$(LIBRETRO_MAME2010_PKG_INSTALL_DIR)/bios/

	# Build Pacman package
	cd $(LIBRETRO_MAME2010_PKG_DIR) && $(BR2_EXTERNAL_BATOCERA_PATH)/scripts/retrolx-makepkg \
	$(BR2_EXTERNAL_BATOCERA_PATH)/package/retrolx/emulators/libretro/libretro-mame2010/PKGINFO \
	$(BATOCERA_SYSTEM_ARCH) $(HOST_DIR)
	mv $(TARGET_DIR)/opt/retrolx/*.zst $(BR2_EXTERNAL_BATOCERA_PATH)/repo/$(BATOCERA_SYSTEM_ARCH)/

	# Cleanup
	rm -Rf $(TARGET_DIR)/opt/retrolx/*
endef

LIBRETRO_MAME2010_POST_INSTALL_TARGET_HOOKS = LIBRETRO_MAME2010_MAKEPKG

$(eval $(generic-package))
