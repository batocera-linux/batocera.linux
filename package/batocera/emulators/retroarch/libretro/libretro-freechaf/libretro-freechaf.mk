################################################################################
#
# FreeChaF - Fairchild Channel F emulator
#
################################################################################
# Version.: Commits on Jan 2, 2021
LIBRETRO_FREECHAF_VERSION = 9bce290eda4497df316dba66aaccfe6cd1024b29
LIBRETRO_FREECHAF_SITE_METHOD=git
LIBRETRO_FREECHAF_SITE=https://github.com/libretro/FreeChaF.git
LIBRETRO_FREECHAF_GIT_SUBMODULES=YES
LIBRETRO_FREECHAF_LICENSE = GPLv3.0

LIBRETRO_FREECHAF_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
        LIBRETRO_FREECHAF_PLATFORM = rpi3
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
        LIBRETRO_FREECHAF_PLATFORM = classic_armv8_a35
endif

LIBRETRO_FREECHAF_COMP_PLATFORM = unix

define LIBRETRO_FREECHAF_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_FREECHAF_COMP_PLATFORM)"
endef

define LIBRETRO_FREECHAF_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/freechaf_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/freechaf_libretro.so
endef

$(eval $(generic-package))
