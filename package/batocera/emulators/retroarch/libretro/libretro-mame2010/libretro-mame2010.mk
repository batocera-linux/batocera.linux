################################################################################
#
# MAME2010
#
################################################################################
# Version.: Commits on Apr 12, 2021
LIBRETRO_MAME2010_VERSION = 932e6f2c4f13b67b29ab33428a4037dee9a236a8
LIBRETRO_MAME2010_SITE = $(call github,libretro,mame2010-libretro,$(LIBRETRO_MAME2010_VERSION))
LIBRETRO_MAME2010_LICENSE = MAME
LIBRETRO_MAME2010_DEPENDENCIES = retroarch

LIBRETRO_MAME2010_PLATFORM = $(LIBRETRO_PLATFORM)
LIBRETRO_MAME2010_EXTRA_ARGS = VRENDER=soft emulator

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

# Bios
# Need to think of another way to use these files.
# They take up a lot of space on tmpfs.
define LIBRETRO_MAME2010_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mame2010_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mame0139_libretro.so

	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/mame2010/samples
	$(INSTALL) -D $(@D)/metadata/* \
		$(TARGET_DIR)/usr/share/batocera/datainit/bios/mame2010
endef

$(eval $(generic-package))
