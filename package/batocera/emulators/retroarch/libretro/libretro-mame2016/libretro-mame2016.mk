################################################################################
#
# MAME2016
#
################################################################################
# Version.: Commits on Oct 16, 2021
LIBRETRO_MAME2016_VERSION = 02987af9b81a9c3294af8fb9d5a34f9826a2cf4d
LIBRETRO_MAME2016_SITE = $(call github,libretro,mame2016-libretro,$(LIBRETRO_MAME2016_VERSION))
LIBRETRO_MAME2016_LICENSE = MAME

LIBRETRO_MAME2016_EXTRA_ARGS = VRENDER=soft emulator

ifeq ($(BR2_x86_64),y)
	LIBRETRO_MAME2016_EXTRA_ARGS += PTR64=1 ARM_ENABLED=0 LCPU=x86_64
endif

ifeq ($(BR2_x86_i586),y)
	LIBRETRO_MAME2016_EXTRA_ARGS += PTR64=0 ARM_ENABLED=0 LCPU=x86
endif

ifeq ($(BR2_arm),y)
	LIBRETRO_MAME2016_EXTRA_ARGS += PTR64=0 ARM_ENABLED=1 LCPU=arm
endif

ifeq ($(BR2_aarch64),y)
	LIBRETRO_MAME2016_EXTRA_ARGS += PTR64=1 ARM_ENABLED=1 LCPU=arm64
endif

define LIBRETRO_MAME2016_BUILD_CMDS
	mkdir -p $(@D)/obj/mame/cpu/ccpu
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)" $(LIBRETRO_MAME2016_EXTRA_ARGS)
endef

define LIBRETRO_MAME2010_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mame2016_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mame0174_libretro.so

	# Bios
    # Need to think of another way to use these files.
    # They take up a lot of space on tmpfs.
	mkdir -p $(TARGET_DIR)/usr/share/batocera/datainit/bios/mame2016/samples
	$(INSTALL) -D $(@D)/metadata/* \
		$(TARGET_DIR)/usr/share/batocera/datainit/bios/mame2016
endef

$(eval $(generic-package))
