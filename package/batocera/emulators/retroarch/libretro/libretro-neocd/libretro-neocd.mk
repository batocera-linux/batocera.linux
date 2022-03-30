
################################################################################
#
# libretro-neocd
#
################################################################################
# Version: Commits on Mar 26, 2022
LIBRETRO_NEOCD_VERSION = 327aeceecdf71c8a0c0af3d6dc53686c94fe44ad
LIBRETRO_NEOCD_SITE = https://github.com/libretro/neocd_libretro.git
LIBRETRO_NEOCD_SITE_METHOD=git
LIBRETRO_NEOCD_GIT_SUBMODULES=YES
LIBRETRO_NEOCD_LICENSE = GPLv3

LIBRETRO_NEOCD_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_NEOCD_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_NEOCD_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
    ifeq ($(BR2_arm),y)
        LIBRETRO_NEOCD_PLATFORM = rpi3
    else
        LIBRETRO_NEOCD_PLATFORM = rpi3_64
    endif

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_NEOCD_PLATFORM = rpi4_64
endif

define LIBRETRO_NEOCD_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="$(LIBRETRO_NEOCD_PLATFORM)"
endef

define LIBRETRO_NEOCD_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/neocd_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/neocd_libretro.so
endef

$(eval $(generic-package))
