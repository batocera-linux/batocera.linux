################################################################################
#
# BLUEMSX
#
################################################################################
# Version.: Commits on Feb 2, 2019
LIBRETRO_BLUEMSX_VERSION = d0fd4a7bf3f76329ab078e4e1e2db13ea20c106b
LIBRETRO_BLUEMSX_SITE = $(call github,libretro,blueMSX-libretro,$(LIBRETRO_BLUEMSX_VERSION))
LIBRETRO_BLUEMSX_LICENSE = GPLv2

define LIBRETRO_BLUEMSX_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D) -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_BLUEMSX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/bluemsx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/bluemsx_libretro.so
endef

$(eval $(generic-package))
