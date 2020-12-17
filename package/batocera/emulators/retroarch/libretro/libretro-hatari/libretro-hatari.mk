################################################################################
#
# HATARI
#
################################################################################
# Version.: Commits on Oct 27, 2020
LIBRETRO_HATARI_VERSION = f19bc118b4e39f5b5131505d5ead09109384be8f
LIBRETRO_HATARI_SITE = $(call github,libretro,hatari,$(LIBRETRO_HATARI_VERSION))
LIBRETRO_HATARI_DEPENDENCIES = libcapsimage
LIBRETRO_HATARI_LICENSE = GPLv2

LIBRETRO_HATARI_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_HATARI_PLATFORM = armv
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI4),y)
	LIBRETRO_HATARI_PLATFORM = unix
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_HATARI_PLATFORM = classic_armv8_a35
endif

define LIBRETRO_HATARI_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_HATARI_PLATFORM)"
endef

define LIBRETRO_HATARI_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/hatari_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/hatari_libretro.so
endef

$(eval $(generic-package))
