################################################################################
#
# YABAUSE
#
################################################################################
# Version.: Commits on Aug 25, 2018
LIBRETRO_YABAUSE_VERSION = fae968218a93d10ca9b811ed47df942f8bec697d
LIBRETRO_YABAUSE_SITE = $(call github,libretro,yabause,$(LIBRETRO_YABAUSE_VERSION))

define LIBRETRO_YABAUSE_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" \
        $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" LD="$(TARGET_CXX)" RANLIB="$(TARGET_RANLIB)" AR="$(TARGET_AR)" -C $(@D)/libretro -f Makefile platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_YABAUSE_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/libretro/yabause_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/yabause_libretro.so
endef

$(eval $(generic-package))
