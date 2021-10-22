################################################################################
#
# xmil - Sharp X1 emulator
#
################################################################################
# Version.: Commits on Mar 14, 2021
LIBRETRO_XMIL_VERSION = 4b4227b5098a21914c04fb873d755e4958928305
LIBRETRO_XMIL_SITE_METHOD=git
LIBRETRO_XMIL_SITE=https://github.com/libretro/xmil-libretro
LIBRETRO_XMIL_GIT_SUBMODULES=YES
LIBRETRO_XMIL_LICENSE = BSD-3

LIBRETRO_XMIL_PLATFORM = unix

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI1),y)
LIBRETRO_XMIL_PLATFORM = rpi1

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI2),y)
LIBRETRO_XMIL_PLATFORM = rpi2

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
LIBRETRO_XMIL_PLATFORM = rpi3_64

else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
LIBRETRO_XMIL_PLATFORM = rpi4_64
endif

define LIBRETRO_XMIL_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/libretro -f Makefile.libretro platform=$(LIBRETRO_XMIL_PLATFORM)
endef

define LIBRETRO_XMIL_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro/x1_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/x1_libretro.so
endef

$(eval $(generic-package))
