################################################################################
#
# LIBRETRO-VICE
#
################################################################################
# Version.: Commits on Jul 11, 2020
LIBRETRO_VICE_VERSION = 3db970b7f9b932bd5b4e60d0fad874486c79f53f
LIBRETRO_VICE_SITE = $(call github,libretro,vice-libretro,$(LIBRETRO_VICE_VERSION))
LIBRETRO_VICE_LICENSE = GPLv2

LIBRETRO_VICE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_RPI3),y)
	LIBRETRO_VICE_PLATFORM = armv neon
endif

define LIBRETRO_VICE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile platform="$(LIBRETRO_VICE_PLATFORM)"
endef

define LIBRETRO_VICE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/vice_*_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/vice_libretro.so
endef

$(eval $(generic-package))
