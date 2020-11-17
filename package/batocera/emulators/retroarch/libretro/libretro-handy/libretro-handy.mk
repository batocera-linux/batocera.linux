################################################################################
#
# LIBRETRO HANDY
#
################################################################################
# Version.: Commits on Oct 19, 2020
LIBRETRO_HANDY_VERSION = dba810a87ebae87392259c68dcab7a35f6000aac
LIBRETRO_HANDY_SITE = $(call github,libretro,libretro-handy,$(LIBRETRO_HANDY_VERSION))
LIBRETRO_HANDY_LICENSE = Zlib

LIBRETRO_HANDY_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDGOA),y)
	LIBRETRO_HANDY_PLATFORM = classic_armv8_a35
endif

define LIBRETRO_HANDY_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_HANDY_PLATFORM)"
endef

define LIBRETRO_HANDY_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/handy_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/handy_libretro.so
endef

$(eval $(generic-package))
