################################################################################
#
# MESEN-S
#
################################################################################
LIBRETRO_MESEN_S_VERSION = 5da37974fc6a8efc651c834e42162dd8fe8af99e
LIBRETRO_MESEN_S_SITE = $(call github,SourMesen,Mesen-S,$(LIBRETRO_MESEN_S_VERSION))

define LIBRETRO_MESEN_S_BUILD_CMDS
	CFLAGS="$(TARGET_CFLAGS)" CXXFLAGS="$(TARGET_CXXFLAGS)" $(MAKE) CXX="$(TARGET_CXX)" CC="$(TARGET_CC)" -C $(@D)/Libretro
endef

define LIBRETRO_MESEN_S_INSTALL_TARGET_CMDS
	$(INSTALL) -D $(@D)/Libretro/mesen-s_libretro.so \
		$(TARGET_DIR)/usr/lib/libretro/mesen-s_libretro.so
endef

$(eval $(generic-package))
