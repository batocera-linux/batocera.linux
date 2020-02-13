################################################################################
#
# GENESISPLUSGX
#
################################################################################
# Version.: Commits on Feb 05, 2020
LIBRETRO_GENESISPLUSGX_VERSION = 50551066f71f8a5ea782ea3747891fd6d24ebe67
LIBRETRO_GENESISPLUSGX_SITE = $(call github,libretro,Genesis-Plus-GX,$(LIBRETRO_GENESISPLUSGX_VERSION))
LIBRETRO_GENESISPLUSGX_LICENSE = Non-commercial

ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ROCKPRO64),y)
	LIBRETRO_GENESISPLUSGX_PLATFORM += rockpro64
else ifeq ($(BR2_PACKAGE_BATOCERA_TARGET_ODROIDN2),y)
	LIBRETRO_GENESISPLUSGX_PLATFORM += odroidn2
else
	LIBRETRO_GENESISPLUSGX_PLATFORM = $(LIBRETRO_PLATFORM)
endif

define LIBRETRO_GENESISPLUSGX_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" \
		-C $(@D) -f Makefile.libretro platform="$(LIBRETRO_GENESISPLUSGX_PLATFORM)"
endef

define LIBRETRO_GENESISPLUSGX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/genesis_plus_gx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/genesisplusgx_libretro.so
endef

$(eval $(generic-package))
