################################################################################
#
# libretro-genesisplusgx-wide
#
################################################################################
# Version: Commits on Jul 28, 2026
LIBRETRO_GENESISPLUSGX_WIDE_VERSION = b7ad005431f5f0b55e559f6d598d1ed2479bf13b
LIBRETRO_GENESISPLUSGX_WIDE_SITE = $(call github,libretro,Genesis-Plus-GX-Wide,$(LIBRETRO_GENESISPLUSGX_WIDE_VERSION))
LIBRETRO_GENESISPLUSGX_WIDE_LICENSE = Non-commercial
LIBRETRO_GENESISPLUSGX_WIDE_DEPENDENCIES += retroarch
LIBRETRO_GENESISPLUSGX_WIDE_EMULATOR_INFO = genesisplusgx-wide.libretro.core.yml

LIBRETRO_GENESISPLUSGX_WIDE_PLATFORM = $(LIBRETRO_PLATFORM)

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_S922X),y)
	LIBRETRO_GENESISPLUSGX_WIDE_PLATFORM += CortexA73_G12B
endif

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ORANGEPI_PC),y)
	LIBRETRO_GENESISPLUSGX_WIDE_PLATFORM += rpi2
endif

define LIBRETRO_GENESISPLUSGX_WIDE_BUILD_CMDS
	$(TARGET_CONFIGURE_OPTS) $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) \
	    -f Makefile.libretro platform="$(LIBRETRO_GENESISPLUSGX_WIDE_PLATFORM)"
endef

define LIBRETRO_GENESISPLUSGX_WIDE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/genesis_plus_gx_wide_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/genesisplusgx-wide_libretro.so
endef

$(eval $(generic-package))
$(eval $(emulator-info-package))