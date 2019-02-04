################################################################################
#
# MAME2010
#
################################################################################
# Version.: Commits on Jan 3, 2019
LIBRETRO_MAME2010_VERSION = c87309dab5fc8db292e31737fcd1754de1fbae6a
LIBRETRO_MAME2010_SITE = $(call github,libretro,mame2010-libretro,$(LIBRETRO_MAME2010_VERSION))
LIBRETRO_MAME2010_LICENSE="MAME"

LIBRETRO_MAME2010_SUPP_OPT=

ifeq ($(BR2_x86_64),y)
	LIBRETRO_MAME2010_SUPP_OPT=ARCH=x86_64 PTR64=1
endif

ifeq ($(BR2_x86_i586),y)
	LIBRETRO_MAME2010_SUPP_OPT=PTR64=0
endif

ifeq ($(BR2_arm),y)
	LIBRETRO_MAME2010_SUPP_OPT=ARM_ENABLED=1 PTR64=0
endif

ifeq ($(BR2_aarch64),y)
	LIBRETRO_MAME2010_SUPP_OPT=ARM_ENABLED=1 PTR64=1
endif

define LIBRETRO_MAME2010_BUILD_CMDS
	mkdir -p $(@D)/obj/mame/cpu/ccpu
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CC="$(TARGET_CC)" LD="$(TARGET_CC)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/ -f Makefile "VRENDER=soft" platform="$(LIBRETRO_PLATFORM)" $(LIBRETRO_MAME2010_SUPP_OPT) emulator

endef

define LIBRETRO_MAME2010_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mame2010_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mame0139_libretro.so
endef

$(eval $(generic-package))
