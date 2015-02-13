################################################################################
#
# 4DO
#
################################################################################
LIBRETRO_4DO_VERSION = master
LIBRETRO_4DO_SITE = $(call github,libretro,4do-libretro,master)

define LIBRETRO_4DO_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D) platform="$(LIBRETRO_PLATFORM)"
endef

define LIBRETRO_4DO_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/4do_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/4do_libretro.so
endef

$(eval $(generic-package))
