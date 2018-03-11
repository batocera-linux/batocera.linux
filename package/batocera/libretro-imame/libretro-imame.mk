################################################################################
#
# IMAME
#
################################################################################
LIBRETRO_IMAME_VERSION = d93c6483dd31681d404b55c2126e7c2ea86c7d1d
LIBRETRO_IMAME_SITE = $(call github,libretro,imame4all-libretro,$(LIBRETRO_IMAME_VERSION))

define LIBRETRO_IMAME_BUILD_CMDS
	mkdir -p $(@D)/obj_libretro_libretro/cpu
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CC="$(TARGET_CC)" -C $(@D) -f Makefile ARM=1
#	$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" VERBOSE=1 -C $(@D) -f makefile.libretro ARM=1
endef

define LIBRETRO_IMAME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mame2000_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/imame4all_libretro.so
endef

$(eval $(generic-package))
