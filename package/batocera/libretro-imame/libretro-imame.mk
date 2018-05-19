################################################################################
#
# IMAME
#
################################################################################
# Version.: Commits on Apr 20, 2018
LIBRETRO_IMAME_VERSION = bd3833c41f6894ba1c5d2f3f35b29190658517a0
LIBRETRO_IMAME_SITE = $(call github,libretro,mame2000-libretro,$(LIBRETRO_IMAME_VERSION))

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
