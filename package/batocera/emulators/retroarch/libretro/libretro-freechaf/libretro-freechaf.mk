################################################################################
#
# FreeChaF - Fairchild Channel F emulator
#
################################################################################
# Version.: Commits on Aug 18, 2021
LIBRETRO_FREECHAF_VERSION = 7275a3e067ed3fd701e0bbcfbcfec8f528587735
LIBRETRO_FREECHAF_SITE_METHOD=git
LIBRETRO_FREECHAF_SITE=https://github.com/libretro/FreeChaF.git
LIBRETRO_FREECHAF_GIT_SUBMODULES=YES
LIBRETRO_FREECHAF_LICENSE = GPLv3.0

LIBRETRO_FREECHAF_PLATFORM = unix

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_FREECHAF_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_FREECHAF_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    ifeq ($(BR2_arm),y)
        LIBRETRO_FREECHAF_PLATFORM = rpi3
    else
        LIBRETRO_FREECHAF_PLATFORM = rpi3_64
    endif

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_FREECHAF_PLATFORM = rpi4_64
endif

define LIBRETRO_FREECHAF_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform=$(LIBRETRO_FREECHAF_PLATFORM)
endef

define LIBRETRO_FREECHAF_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/freechaf_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/freechaf_libretro.so
endef

$(eval $(generic-package))
