################################################################################
#
# BEETLE_SUPERGRAFX
#
################################################################################
# Version.: Commits on Jan 13, 2021
LIBRETRO_BEETLE_SUPERGRAFX_VERSION = 97c7d4c4c661663d69af4c858df61e06d6eac18a
LIBRETRO_BEETLE_SUPERGRAFX_SITE = $(call github,libretro,beetle-supergrafx-libretro,$(LIBRETRO_BEETLE_SUPERGRAFX_VERSION))
LIBRETRO_BEETLE_SUPERGRAFX_LICENSE = GPLv2

LIBRETRO_BEETLE_SUPERGRAFX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_BEETLE_SUPERGRAFX_PLATFORM = classic_armv8_a35
endif

define LIBRETRO_BEETLE_SUPERGRAFX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_BEETLE_SUPERGRAFX_PLATFORM)"
endef

define LIBRETRO_BEETLE_SUPERGRAFX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_supergrafx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mednafen_supergrafx_libretro.so
endef

$(eval $(generic-package))
