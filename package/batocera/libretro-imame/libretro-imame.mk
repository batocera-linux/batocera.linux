################################################################################
#
# IMAME
#
################################################################################
LIBRETRO_IMAME_VERSION = 4027bf6fd0c2330ad8e017fd6a8ace4ea2c9cc63
LIBRETRO_IMAME_SITE = $(call github,libretro,imame4all-libretro,$(LIBRETRO_IMAME_VERSION))

define LIBRETRO_IMAME_BUILD_CMDS
	mkdir -p $(@D)/obj_libretro_libretro/cpu
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CC="$(TARGET_CC)" -C $(@D) -f makefile.libretro ARM=1
#	$(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" VERBOSE=1 -C $(@D) -f makefile.libretro ARM=1
endef

define LIBRETRO_IMAME_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/imame4all_libretro.so
endef

$(eval $(generic-package))
