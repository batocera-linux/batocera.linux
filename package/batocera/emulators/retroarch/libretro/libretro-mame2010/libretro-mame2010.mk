################################################################################
#
# MAME2010
#
################################################################################
# Version.: Commits on Jul 06, 2020
LIBRETRO_MAME2010_VERSION = 9b0e3b3384cc8e86e78870262f4027bdce9de0f4
LIBRETRO_MAME2010_SITE = $(call github,libretro,mame2010-libretro,$(LIBRETRO_MAME2010_VERSION))
LIBRETRO_MAME2010_LICENSE = MAME

LIBRETRO_MAME2010_EXTRA_ARGS = VRENDER=soft emulator

ifeq ($(BR2_x86_64),y)
	LIBRETRO_MAME2010_EXTRA_ARGS += PTR64=1 ARM_ENABLED=0 LCPU=x86_64
endif

ifeq ($(BR2_x86_i586),y)
	LIBRETRO_MAME2010_EXTRA_ARGS += PTR64=0 ARM_ENABLED=0 LCPU=x86
endif

ifeq ($(BR2_arm),y)
	LIBRETRO_MAME2010_EXTRA_ARGS += PTR64=0 ARM_ENABLED=1 LCPU=arm
endif

ifeq ($(BR2_aarch64),y)
	LIBRETRO_MAME2010_EXTRA_ARGS += PTR64=1 ARM_ENABLED=1 LCPU=arm64
endif

define LIBRETRO_MAME2010_BUILD_CMDS
	mkdir -p $(@D)/obj/mame/cpu/ccpu
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)" $(LIBRETRO_MAME2010_EXTRA_ARGS)
endef

define LIBRETRO_MAME2010_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mame2010_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mame0139_libretro.so

	# Bios
    # Need to think of another way to use these files.
    # They take up a lot of space on tmpfs.
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/mame2010/samples
	$(INSTALL) -D $(@D)/metadata/* \
		$(TARGET_DIR)/usr/share/batocera/datainit/bios/mame2010
endef

$(eval $(generic-package))
