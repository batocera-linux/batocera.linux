################################################################################
#
# libretro-theodore
#
################################################################################
# Version: Commits on Aug 17, 2026
LIBRETRO_THEODORE_VERSION = 4d469ce0f71ee046ceb78cdbf8e9f18364aaa918
LIBRETRO_THEODORE_SITE = https://github.com/Zlika/theodore.git
LIBRETRO_THEODORE_SITE_METHOD = git
LIBRETRO_THEODORE_GIT_SUBMODULES = YES
LIBRETRO_THEODORE_LICENSE = GPLv3
LIBRETRO_THEODORE_DEPENDENCIES += retroarch
LIBRETRO_THEODORE_EMULATOR_INFO = theodore.libretro.core.yml

LIBRETRO_THEODORE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_THEODORE_PLATFORM = armv
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_THEODORE_PLATFORM = rpi1
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_THEODORE_PLATFORM = rpi2
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_THEODORE_PLATFORM = rpi3_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_THEODORE_PLATFORM = rpi4_64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2712),y)
LIBRETRO_THEODORE_PLATFORM = rpi5_64
else ifeq ($(BR2_aarch64),y)
LIBRETRO_THEODORE_PLATFORM = unix
endif

define LIBRETRO_THEODORE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D)/ -f Makefile platform="$(LIBRETRO_THEODORE_PLATFORM)" \
        GIT_VERSION=" $(shell echo $(LIBRETRO_THEODORE_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_THEODORE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/theodore_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/theodore_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))