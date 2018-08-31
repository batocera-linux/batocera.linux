################################################################################
#
# CATSFC
#
################################################################################
# Version.: Commits on Aug 21, 2018
LIBRETRO_CATSFC_VERSION = 878f1ce501f6977e666c7a43bfd1199e228bde60
LIBRETRO_CATSFC_SITE = $(call github,libretro,snes9x2005,$(LIBRETRO_CATSFC_VERSION))

define LIBRETRO_CATSFC_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_CATSFC_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/snes9x2005_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/catsfc_libretro.so
endef

$(eval $(generic-package))
