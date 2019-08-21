################################################################################
#
# FMSX
#
################################################################################
# Version.: Commits on Jan 4, 2019
LIBRETRO_FMSX_VERSION = 6b241974ffb4d2a3fc681b65a8ff6b717501cb67
LIBRETRO_FMSX_SITE = $(call github,libretro,fmsx-libretro,$(LIBRETRO_FMSX_VERSION))
LIBRETRO_FMSX_LICENSE = Non-commercial

define LIBRETRO_FMSX_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D) platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_FMSX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fmsx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fmsx_libretro.so
endef

$(eval $(generic-package))
