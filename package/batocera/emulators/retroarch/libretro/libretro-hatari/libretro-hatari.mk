################################################################################
#
# HATARI
#
################################################################################
# Version.: Commits on Apr 2, 2020
LIBRETRO_HATARI_VERSION = f8c35958ec1c93c32d41d61fa4903b2f5daec78c
LIBRETRO_HATARI_SITE = $(call github,libretro,hatari,$(LIBRETRO_HATARI_VERSION))
LIBRETRO_HATARI_DEPENDENCIES = libcapsimage
LIBRETRO_HATARI_LICENSE = GPLv2

define LIBRETRO_HATARI_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_HATARI_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/hatari_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/hatari_libretro.so
endef

$(eval $(generic-package))
