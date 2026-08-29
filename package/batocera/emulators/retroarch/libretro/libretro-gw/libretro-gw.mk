################################################################################
#
# libretro-gw
#
################################################################################
# Version: Commits on Apr 20, 2026
LIBRETRO_GW_VERSION = 91d599b951e7bfe7e040347f58667cba20074adc
LIBRETRO_GW_SITE = $(call github,libretro,gw-libretro,$(LIBRETRO_GW_VERSION))
LIBRETRO_GW_LICENSE = GPLv3
LIBRETRO_GW_DEPENDENCIES += retroarch
LIBRETRO_GW_EMULATOR_INFO = gw.libretro.core.yml

define LIBRETRO_GW_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ \
	    -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_GW_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/gw_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/gw_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))