################################################################################
#
# libretro-beetle-pce
#
################################################################################
# Version: Commits on April 11, 2026
LIBRETRO_BEETLE_PCE_VERSION = ae99235c2139c176c1a8d0fde2957bf701d3cab0
LIBRETRO_BEETLE_PCE_SITE = $(call github,libretro,beetle-pce-libretro,$(LIBRETRO_BEETLE_PCE_VERSION))
LIBRETRO_BEETLE_PCE_LICENSE = GPLv2
LIBRETRO_BEETLE_PCE_DEPENDENCIES += retroarch
LIBRETRO_BEETLE_PCE_EMULATOR_INFO = pce.libretro.core.yml

define LIBRETRO_BEETLE_PCE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
	    -C $(@D) platform="$(LIBRETRO_PLATFORM)" \
        GIT_VERSION="-$(shell echo $(LIBRETRO_BEETLE_PCE_VERSION) | cut -c 1-7)"
endef

define LIBRETRO_BEETLE_PCE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_pce_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/pce_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))
