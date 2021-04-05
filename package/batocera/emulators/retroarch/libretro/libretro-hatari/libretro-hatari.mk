################################################################################
#
# HATARI
#
################################################################################
# Version.: Commits on Mar 17, 2021
LIBRETRO_HATARI_VERSION = cea06eebf695b078fadc0e78bb0f2b2baaca799f
LIBRETRO_HATARI_SITE = $(call github,libretro,hatari,$(LIBRETRO_HATARI_VERSION))
LIBRETRO_HATARI_DEPENDENCIES = libcapsimage retroarch
LIBRETRO_HATARI_LICENSE = GPLv2

LIBRETRO_HATARI_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3)$(BR2_PACKAGE_BATOCERA_TARGET_S812),y)
	LIBRETRO_HATARI_PLATFORM = armv
endif

ifeq ($(BR2_aarch64),y)
	LIBRETRO_HATARI_PLATFORM = unix
endif

define LIBRETRO_HATARI_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_HATARI_PLATFORM)"
endef

define LIBRETRO_HATARI_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/hatari_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/hatari_libretro.so
endef

$(eval $(generic-package))
