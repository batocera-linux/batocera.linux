################################################################################
#
# libretro-zc210
#
################################################################################
# Version: Commits on Feb 28, 2022
LIBRETRO_ZC210_VERSION = 4d0997606b9ea1eba0222b8d287b12171729395c
LIBRETRO_ZC210_SITE = https://github.com/netux79/zc210-libretro.git
LIBRETRO_ZC210_SITE_METHOD=git
LIBRETRO_ZC210_GIT_SUBMODULES=YES
LIBRETRO_ZC210_LICENSE = GPLv2
LIBRETRO_ZC210_DEPENDENCIES = retroarch

LIBRETRO_ZC210_PLATFORM = $(LIBRETRO_PLATFORM)

LIBRETRO_ZC210_EXTRA_ARGS =

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
LIBRETRO_ZC210_PLATFORM = armv

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_ZC210_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_ZC210_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPIZERO2),y)
LIBRETRO_ZC210_PLATFORM = rpi3

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
LIBRETRO_ZC210_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_ZC210_PLATFORM = rpi4_64

else ifeq ($(BR2_aarch64),y)
LIBRETRO_ZC210_PLATFORM = unix
endif

ifeq ($(BR2_x86_64),y)
LIBRETRO_ZC210_PLATFORM = unix
LIBRETRO_ZC210_EXTRA_ARGS +=
endif

define LIBRETRO_ZC210_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_ZC210_PLATFORM)" $(LIBRETRO_ZC210_EXTRA_ARGS) \
        GIT_VERSION="-$(shell echo $(LIBRETRO_ZC210_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_ZC210_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/zc210_libretro.so $(TARGET_DIR)/usr/lib/libretro/zc210_libretro.so
endef

$(eval $(generic-package))
