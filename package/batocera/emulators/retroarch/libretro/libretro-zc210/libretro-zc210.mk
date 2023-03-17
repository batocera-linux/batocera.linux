################################################################################
#
# libretro-zc210
#
################################################################################
# Version: Commits on April 25, 2022
LIBRETRO_ZC210_VERSION = b6426da40b074245fda097fd345fa7c9cdbf152a
LIBRETRO_ZC210_SITE = https://github.com/netux79/zc210-libretro.git
LIBRETRO_ZC210_SITE_METHOD=git
LIBRETRO_ZC210_GIT_SUBMODULES=YES
LIBRETRO_ZC210_LICENSE = GPLv2
LIBRETRO_ZC210_DEPENDENCIES = retroarch

LIBRETRO_ZC210_PLATFORM = $(LIBRETRO_PLATFORM)

LIBRETRO_ZC210_EXTRA_ARGS =

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_ZC210_PLATFORM = armv

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2835),y)
LIBRETRO_ZC210_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2836),y)
LIBRETRO_ZC210_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2837),y)
LIBRETRO_ZC210_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_BCM2711),y)
LIBRETRO_ZC210_PLATFORM = rpi4_64

else ifeq ($(BR2_aarch64),y)
LIBRETRO_ZC210_PLATFORM = unix
endif

ifeq ($(BR2_x86_64),y)
LIBRETRO_ZC210_PLATFORM = unix
LIBRETRO_ZC210_EXTRA_ARGS +=
endif

ZC210_CONFIGURE_OPTS = platform=$(LIBRETRO_ZC210_PLATFORM)

define LIBRETRO_ZC210_BUILD_CMDS
	$(ZC210_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile $(LIBRETRO_ZC210_EXTRA_ARGS) \
        GIT_VERSION="-$(shell echo $(LIBRETRO_ZC210_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_ZC210_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/zc210_libretro.so $(TARGET_DIR)/usr/lib/libretro/zc210_libretro.so
endef

$(eval $(generic-package))
