################################################################################
#
# FMSX
#
################################################################################
# Version.: Commits on Aug 12, 2018
LIBRETRO_FMSX_VERSION = 778773f04ef0d7c0f7f3c423fb4065981e811a36
LIBRETRO_FMSX_SITE = $(call github,libretro,fmsx-libretro,$(LIBRETRO_FMSX_VERSION))

define LIBRETRO_FMSX_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D) platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_FMSX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/fmsx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/fmsx_libretro.so
endef

$(eval $(generic-package))
