################################################################################
#
# DESMUME2015
#
################################################################################
# Version : Commits on May 8, 2018
LIBRETRO_DESMUME2015_VERSION = 5957aa07b1b8b60142cdcaccffa827316dc548d5
LIBRETRO_DESMUME2015_SITE = $(call github,libretro,desmume2015,$(LIBRETRO_DESMUME2015_VERSION))

define LIBRETRO_DESMUME2015_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/desmume2015/src/frontend/libretro -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_DESMUME2015_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/desmume2015/src/frontend/libretro/desmume2015_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/desmume2015_libretro.so
endef

$(eval $(generic-package))
