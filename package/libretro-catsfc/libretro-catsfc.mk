################################################################################
#
# CATSFC
#
################################################################################
LIBRETRO_CATSFC_VERSION = 361b6927ef6af4e0913f18909cb841fd192e69d1
LIBRETRO_CATSFC_SITE = $(call github,libretro,CATSFC-libretro,$(LIBRETRO_CATSFC_VERSION))

define LIBRETRO_CATSFC_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_CATSFC_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/catsfc_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/catsfc_libretro.so
endef

$(eval $(generic-package))
