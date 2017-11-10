################################################################################
#
# BEETLE_LYNX
#
################################################################################
LIBRETRO_BEETLE_LYNX_VERSION = 3b3fbd32c252bf030cc75d289093c3fe6aa3f59f
LIBRETRO_BEETLE_LYNX_SITE = $(call github,libretro,beetle-lynx-libretro,$(LIBRETRO_BEETLE_LYNX_VERSION))

define LIBRETRO_BEETLE_LYNX_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/ -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_BEETLE_LYNX_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/mednafen_lynx_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mednafen_lynx_libretro.so
endef

$(eval $(generic-package))
