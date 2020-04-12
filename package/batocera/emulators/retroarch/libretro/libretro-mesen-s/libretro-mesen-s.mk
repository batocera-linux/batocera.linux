################################################################################
#
# MESEN-S
#
################################################################################
# Version.: Commits on Apr 10, 2020
LIBRETRO_MESEN_S_VERSION = 2d0b0c47bbb29440a502c975f39233cb0c9f8001
LIBRETRO_MESEN_S_SITE = $(call github,SourMesen,Mesen-S,$(LIBRETRO_MESEN_S_VERSION))

define LIBRETRO_MESEN_S_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/Libretro
endef

define LIBRETRO_MESEN_S_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/Libretro/mesen-s_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mesen-s_libretro.so
endef

$(eval $(generic-package))
