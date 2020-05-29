################################################################################
#
# GENESISPLUSGX
#
################################################################################
# Version.: Commits on May 16, 2020
LIBRETRO_GENESISPLUSGX_VERSION = 9316c9ef48c76f84ae8b62fb9ff9fb7c85e2728d
LIBRETRO_GENESISPLUSGX_SITE = $(call github,ekeeke,Genesis-Plus-GX,$(LIBRETRO_GENESISPLUSGX_VERSION))
LIBRETRO_GENESISPLUSGX_LICENSE = Non-commercial

LIBRETRO_GENESISPLUSGX_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKPRO64),y)
	LIBRETRO_GENESISPLUSGX_PLATFORM += rockpro64
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2),y)
	LIBRETRO_GENESISPLUSGX_PLATFORM += CortexA73_G12B
endif

define LIBRETRO_GENESISPLUSGX_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) -f Makefile.libretro platform="$(LIBRETRO_GENESISPLUSGX_PLATFORM)"
endef

define LIBRETRO_GENESISPLUSGX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/genesis_plus_gx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/genesisplusgx_libretro.so
endef

$(eval $(generic-package))
