################################################################################
#
# GW
#
################################################################################
# Version.: Commits on Apr 25, 2021
LIBRETRO_GW_VERSION = 50538984da8755db55577683cc98912e26ee8d8a
LIBRETRO_GW_SITE = $(call github,libretro,gw-libretro,$(LIBRETRO_GW_VERSION))
LIBRETRO_GW_LICENSE = GPLv3

LIBRETRO_GW_PLATFORM = $(LIBRETRO_PLATFORM)

define LIBRETRO_GW_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_GW_PLATFORM)"
endef

define LIBRETRO_GW_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/gw_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gw_libretro.so
endef

$(eval $(generic-package))
