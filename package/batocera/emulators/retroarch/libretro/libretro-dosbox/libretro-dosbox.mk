################################################################################
#
# DOSBOX
#
################################################################################
# Version.: Commits on Sep 30, 2018
LIBRETRO_DOSBOX_VERSION = 8f2d7318b6e66e397448a5905b30bc4f92de7133
LIBRETRO_DOSBOX_SITE = $(call github,libretro,dosbox-libretro,$(LIBRETRO_DOSBOX_VERSION))

define LIBRETRO_DOSBOX_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_LD)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/ -f Makefile.libretro platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_DOSBOX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/dosbox_libretro.so \
	  $(TARGET_DIR)/usr/lib/libretro/dosbox_libretro.so
endef

$(eval $(generic-package))
