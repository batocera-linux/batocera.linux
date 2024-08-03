################################################################################
#
# libretro-freechaf
#
################################################################################
# Version: Commits on Jun 28, 2024
LIBRETRO_FREECHAF_VERSION = cdb8ad6fcecb276761b193650f5ce9ae8b878067
LIBRETRO_FREECHAF_SITE_METHOD=git
LIBRETRO_FREECHAF_SITE=https://github.com/libretro/FreeChaF.git
LIBRETRO_FREECHAF_GIT_SUBMODULES=YES
LIBRETRO_FREECHAF_LICENSE = GPLv3.0

LIBRETRO_FREECHAF_PLATFORM = unix

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_FREECHAF_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_FREECHAF_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_FREECHAF_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_FREECHAF_PLATFORM = rpi4_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_FREECHAF_PLATFORM = rpi5_64
endif

define LIBRETRO_FREECHAF_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/ -f Makefile platform=$(LIBRETRO_FREECHAF_PLATFORM)
endef

define LIBRETRO_FREECHAF_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/freechaf_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/freechaf_libretro.so
endef

$(eval $(generic-package))
