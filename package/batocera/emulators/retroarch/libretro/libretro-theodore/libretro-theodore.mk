################################################################################
#
# libretro-theodore
#
################################################################################
# Version: Commits on Mar 3, 2022
LIBRETRO_THEODORE_VERSION = 563fb989f12c7176824b34bbc726bf24d933e86c
LIBRETRO_THEODORE_SITE = $(call github,Zlika,theodore,$(LIBRETRO_THEODORE_VERSION))
LIBRETRO_THEODORE_LICENSE = GPLv3

LIBRETRO_THEODORE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_THEODORE_PLATFORM = armv

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_THEODORE_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_THEODORE_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
LIBRETRO_THEODORE_PLATFORM = rpi3

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
LIBRETRO_THEODORE_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_THEODORE_PLATFORM = rpi4_64

else ifeq ($(BR2_aarch64),y)
LIBRETRO_THEODORE_PLATFORM = unix
endif

define LIBRETRO_THEODORE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_THEODORE_PLATFORM)" \
        GIT_VERSION=" $(shell echo $(LIBRETRO_THEODORE_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_THEODORE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/theodore_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/theodore_libretro.so
endef

$(eval $(generic-package))
